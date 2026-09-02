---
id: doc-1
title: In-Place Morpheme Tags and FST State Space Optimization
type: specification
created_date: '2026-09-02 19:51'
updated_date: '2026-09-02 19:51'
---
# In-Place Morpheme Tags and FST State Space Optimization

## 1. Executive Summary

This specification outlines the architecture, implementation strategy, and verification protocol for replacing long-distance trailing feature labels in `parC-macros` with in-place adjacent morpheme tags.

Currently, the Cherokee verb grammar relies on generic placeholder tokens (`[Pro]`, `[Aspect]`, `[Tense]`) in the stem template paired with trailing feature labels appended after `[EOW]` (`[prefix_class=...]`, `[aspect_class=...]`, `[aspect=...]`, etc.). In finite-state transducers, these long-distance cross-boundary dependencies require intermediate states to remember feature identities across the entire stem, resulting in exponential/Cartesian state explosion in `tag_domain` and during transducer composition.

By migrating to in-place adjacent tag sequences (`[PrefixClass=...][Pro=...]`, `[AspectClass=...][Aspect=...]`, `[TenseClass=...][Tense=...]`), every morphological slot becomes a strictly local string rewrite. This completely eliminates long-distance state holding, shrinks the post-`[EOW]` Cartesian feature domain by over 450x, replaces complex stage gating with fast local `string_map` rules, and enables instant ambiguity resolution during parsing.

---

## 2. Problem Statement & Theoretical Analysis

### 2.1 Current Architecture & The Long-Distance State Problem

The current underlying Cherokee verb template is defined as:
```
[BOW] [WI]? [DIST]? [Pro] <H_ALT>? <V>? (<C>+<V>)* <C>* [Aspect] [Tense] [EOW] [aspect_class=...] [prefix_class=...] [tense_present_class=...] [aspect=...] [pronominal=...] [rules=+] [tense=...]
```

In this model:
1. **Pronominal Slot**: `[Pro]` sits at the prefix position, but `prefix_class` (7 values) and `pronominal` (22 values) sit at the end of the word. The transducer must preserve $7 \times 22 = 154$ potential states across the entire root stem, suffixes, `[EOW]`, and intermediate tags.
2. **Aspect Slot**: `[Aspect]` sits at suffix position 1, while `aspect_class` (~90 values) and `aspect` (5 values) sit after `[EOW]`. This creates a $90 \times 5 = 450$ state multiplier carried across `[Tense]`, `[EOW]`, and intermediate tags.
3. **Cartesian Tag Domain Explosion**: When `infer_lexical_features=True` (open parsing and wildcard inflection), `parC` constructs a `tag_domain` that is the Cartesian product of all active features. Every stage in the cascade—including stages unrelated to aspect or pronouns—must maintain bypass/identity paths through all 450 aspect paths $\times$ 154 pronominal paths.
4. **Delayed Emission in Parsing (Inversion)**: When parsing a surface form (e.g. `gowatvts`), the surface suffix `ts` can only emit generic `[Aspect]`. It must delay emitting `[aspect_class=become]` until after `[EOW]`. Denser ambiguity (e.g. `-sk` shared by dozens of classes) forces parallel hypotheses to stay active across the entire tail of the word.

### 2.2 In-Place Morpheme Architecture

Cherokee is fundamentally a concatenative position-class language. Every morpheme category occupies a distinct, fixed linear slot:

```
Slot 1: Prepronominal Prefixes ([WI]?[DIST]?)
Slot 2: Pronominal Prefix ([PrefixClass][Pro])
Slot 3: Root-initial Alternation ([H_DROP] | [H_GLOT] | [H_LAT] | [H_NONE])
Slot 4: Verb Root Stem (<Root>)
Slot 5: Aspect Suffix ([AspectClass][Aspect])
Slot 6: Tense Suffix ([TenseClass][Tense])
```

By encoding both the lexical selector and inflectional category as adjacent tags at their physical site:
- Suffix rule: `[AspectClass=become][Aspect=completive]` -> `ts`
- Prefix rule: `[PrefixClass=a_stem][Pro=1sg.A]` -> `k`
- Tense rule: `[TenseClass=a_present][Tense=present]` -> `a`

The transducer operations become 100% local. Once rewritten, the lexical class identity is consumed and does not need to be tracked past the slot.

---

## 3. Morphotactic Schema & Templates

### 3.1 Pattern Definitions (`Phonology/Patterns/phoneme_groups.yaml`)

```yaml
  - name: PrepronominalPrefixes
    pattern: "[WI]?[DIST]?"
    ref: <PrepronominalPrefixes>

  - name: Root
    pattern: "<V>?(<C>+<V>)*<C>*"
    ref: <Root>

  - name: PrefixClass
    pattern: "[PrefixClass=a_stem]|[PrefixClass=v_stem]|[PrefixClass=e_stem]|[PrefixClass=k_a_stem]|[PrefixClass=vowel_stem]|[PrefixClass=cons_stem]|[PrefixClass=r_stem]"
    ref: <PrefixClass>

  - name: Pro
    pattern: "[Pro=1sg.A]|[Pro=Edl.A]|[Pro=Epl.A]|[Pro=Idl.A]|[Pro=Ipl.A]|[Pro=2sg.A]|[Pro=2dl.A]|[Pro=2pl.A]|[Pro=3sg.A]|[Pro=3ns.A]|[Pro=1sg.B]|[Pro=Edl.B]|[Pro=Epl.B]|[Pro=Idl.B]|[Pro=Ipl.B]|[Pro=2sg.B]|[Pro=2dl.B]|[Pro=2pl.B]|[Pro=3sg.B]|[Pro=3ns.B]|[Pro=1sg>3sg]|[Pro=2sg>3sg]"
    ref: <Pro>

  - name: AspectClass
    pattern: "[AspectClass=a]|[AspectClass=become]|[AspectClass=apl]|..." # Union of ~90 classes
    ref: <AspectClass>

  - name: Aspect
    pattern: "[Aspect=present]|[Aspect=incompletive]|[Aspect=completive]|[Aspect=immediate]|[Aspect=infinitive]"
    ref: <Aspect>

  - name: TenseClass
    pattern: "[TenseClass=a_present]|[TenseClass=i_present]"
    ref: <TenseClass>

  - name: Tense
    pattern: "[Tense=present]|[Tense=immediate]|[Tense=habitual]|[Tense=future_prog]|[Tense=assertive]|[Tense=reported]|[Tense=infinitive]"
    ref: <Tense>
```

### 3.2 Open Root Template (`verb.yaml`)

```yaml
paradigm:
  open_root_template: "<PrepronominalPrefixes><PrefixClass><Pro><H_ALT>?<Root><AspectClass><Aspect><TenseClass><Tense>"
```

---

## 4. Phonological & Morphotactic Rules

### 4.1 Morpheme Replacement Rules (`string_map`)
Each morpheme slot is compiled into a simple, static `string_map` rule:
- `pro_replace`: `[PrefixClass=...][Pro=...]` -> prefix string
- `aspect_replace`: `[AspectClass=...][Aspect=...]` -> aspect suffix string
- `tense_replace`: `[TenseClass=...][Tense=...]` -> tense suffix string

### 4.2 Local Context-Sensitive Phonology
- `drop_stem_initial_vowel`:
  ```yaml
  - name: drop_stem_initial_a
    string_map:
      - [a, ""]
    left_context: "[PrefixClass=a_stem]"
  ```
- `final_dropping`:
  ```yaml
  - name: drop_final_root_phone
    string_map:
      - ["<Phone>", ""]
    right_context: "[AspectClass=apl][Aspect=immediate]|[AspectClass=hvsk-nh[inf2]][Aspect=infinitive]|..."
  ```

### 4.3 Paradigm Definition via `global_markers`
In `parC`, stages using `global_markers` apply rules unconditionally across Sigma* without Cartesian `tag_domain` construction:
```yaml
kind: Paradigm
part_of_speech: $verb
stage_order:
  - final_dropping
  - aspect_suffix
  - h_alternation
  - drop_stem_initial_vowel
  - pronominal
  - tense
  - insert_dist
  - insert_wi
global_markers:
  - stage: final_dropping
    value: $drop_root_final
  - stage: aspect_suffix
    value: $aspect_replace
  - stage: h_alternation
    value: $h_alternation
  - stage: drop_stem_initial_vowel
    value: $drop_stem_initial_vowel
  - stage: pronominal
    value: $pro_replace
  - stage: tense
    value: $tense_replace
  - stage: insert_dist
    value: $insert_di
  - stage: insert_wi
    value: $insert_wi
```

---

## 5. Evaluation Protocol & Verification Strategy

### 5.1 Isolated Testbed (`chr-inplace-config` / `chr-inplace-generated`)
To avoid any disruption to the existing baseline:
1. Snapshot current baseline metrics from `chr-generated/`.
2. Copy `chr-config/` to `chr-inplace-config/`.
3. Generate into `chr-inplace-generated/`.

### 5.2 Metrics to Record
A script will record and report:
- Open Inflect Graph: State count, Arc count, Disk size (.fst)
- Open Parse Graph: State count, Arc count, Disk size (.fst)
- Paradigm compilation time (seconds)
- Corpus parse time across 100 rows

### 5.3 Parity Verification
- Run `parse_chr_dict` on `chr-corpus/corpus.csv`.
- Adapt `read_labels(s)` in Python to extract:
  - `prefix_class` from `[PrefixClass=...]`
  - `aspect_class` from `[AspectClass=...]`
  - `tense_present_class` from `[TenseClass=...]`
  - `pronominal` from `[Pro=...]`
  - `aspect` from `[Aspect=...]`
  - `tense` from `[Tense=...]`
- Assert 100% equivalence with baseline `roots.csv`.
