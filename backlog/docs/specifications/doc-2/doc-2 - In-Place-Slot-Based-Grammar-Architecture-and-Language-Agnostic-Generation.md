---
id: doc-2
title: In-Place Slot-Based Grammar Architecture and Language-Agnostic Generation
type: specification
created_date: '2026-09-08 14:56'
updated_date: '2026-09-08 14:57'
---
# In-Place Slot-Based Grammar Architecture and Language-Agnostic Generation

## 1. Executive Summary & Vision

We are going **all in on our in-place slot-based grammar** in `parC-macros`.

In this architecture, every inflectional and lexical morpheme tag is placed directly at its linear physical site within the morphological template rather than being deferred as trailing feature tags after `[EOW]`. This local rewrite model eliminates Cartesian FST state explosion, replaces complex stage gating with fast local `string_map` transducers, and provides instantaneous ambiguity resolution during dictionary parsing.

A **Slot** is a structural site in the verb template where a morpheme is realized:
- A slot may consist of a single underlying tag (e.g., `<Tense>` -> `[Tense=present_a]`).
- A slot may be a composite of two ordered elements (e.g., `<PrefixClass><Pro>` -> `[PrefixClass=a_stem][Pro=1sg.A]`).
- A slot may be a composite of three ordered elements with optional components (e.g., `<AspectClass><Variant><Aspect>` -> `[AspectClass=become][Variant=2][Aspect=present]`).

### Core Architectural Mandates
1. **Formal Slot Specification in Configuration (`verb.yaml`)**:
   Slots will be defined explicitly as a list of first-class objects in `verb.yaml`. Each slot declares its identifier, surface role, rule target, data sources, and internal structure via an ordered list of `TagGroup` entries with an `optional` boolean flag. This provides an elegant, principled mechanism for handling variants (e.g., `Variant` is optional; when absent, standard variant 1 is implied).
2. **Language-Agnostic Generation Boundary (`parc_macros/`)**:
   `parc_macros/` must be strictly language-agnostic. No Cherokee-specific file paths (`verb-pronominal.csv`, `verb-aspect.csv`, `verb-tense.csv`, `aspect_effects.csv`), hardcoded class names (`prefix_class`, `aspect_class`), or ad-hoc phonological rules (`drop_first_a`, `drop_first_v`) may exist in `parc_macros/`. The generator must derive alphabet entries, pattern definitions, morpheme replacement rules, and template lattices dynamically from the slot specifications.
3. **Programmatic Grammar-to-Python Handoff (`parse_chr_dict/`)**:
   Instead of manual, duplicated string-slicing and hardcoded dictionaries in `parse_chr_dict` (`SLOT_NAME_TO_TAG`, `SLOT_TAG_MAP`, hardcoded boundary tag matching for root filters), the compilation step will emit a structured metadata manifest (`slots.json` or compiled `Paradigm/verb.yaml`). The Python parsing and reconstruction engine (`parse_chr_dict`) will consume this manifest programmatically to drive tag tokenization, root boundary filtering, and forward inflection serialization.

---

## 2. Investigation: Non-Programmatic Assumptions Across the Codebase

A deep audit of `parc_macros/` and `parse_chr_dict/` revealed extensive non-programmatic assumptions and language-specific leaks.

### 2.1 Leaks in `parc_macros/`

1. **Hardcoded File Paths in `parc_macros/generate_phonology.py`**:
   - `extract_phonology_data()` directly opens hardcoded filenames:
     - `config_dir / "verb-pronominal.csv"`
     - `config_dir / "verb-tense.csv"`
     - `config_dir / "verb-aspect.csv"`
     - `config_dir / "verb-aspect-stative.csv"`
     - `config_dir / "aspect_effects.csv"` / `verb-aspect-drop-final.csv` / `verb-aspect-drop-final-two.csv`
     - `config_dir / "verb-pronominal-drop-first-a.csv"` / `verb-pronominal-drop-first-v.csv`
   - These hardcoded paths violate the strict invariant that `parc_macros/` is a generic, language-agnostic framework.
2. **Hardcoded Tag Titles & Rules in `parc_macros/generate_morpheme_replace_rules.py`**:
   - `CLASS_FEATURE_TO_TAG_TITLE` hardcodes:
     ```python
     CLASS_FEATURE_TO_TAG_TITLE = {
         "prefix_class": "PrefixClass",
         "aspect_class": "AspectClass",
         "tense_present_class": "TenseClass",
         "tense_class": "TenseClass",
     }
     ```
   - Pattern assembly in `_generate_rules()` assumes a 2-tag structure or hardcodes `[Variant=idx]` as an ad-hoc special case:
     ```python
     if idx == 1:
         pattern = f"[{class_tag_title}={class_name}][{feature_tag_title}={feat_name}]"
     else:
         pattern = f"[{class_tag_title}={class_name}][Variant={idx}][{feature_tag_title}={feat_name}]"
     ```
   - It cannot generalize to arbitrary n-tag slots or other optional feature tags.
3. **Hardcoded Cherokee Phonological Rules in `parc_macros/generate_phonology.py`**:
   - Generates Cherokee-specific `drop_stem_initial_vowel.yaml` by inspecting `drop_first_a_triggers` (`a_stem` with `3sg.A` / `3sg.B`) and `drop_first_v_triggers` (`v_stem` with `3sg.B`).
   - Generates Cherokee-specific `drop_root_final.yaml` by injecting `[AspectClass=...][Variant=...][Aspect=...]`.
4. **Opaque Template Handoff in `parc_macros/generate_markers.py`**:
   - `generate_markers.py` reads `open_root_template` as an unvalidated raw string from `verb.yaml`.
   - It blindly copies the template into `chr-generated/Morphotactics/Paradigm/verb.yaml` without verifying that the referenced patterns exist or match the declared morpheme replacement rules.

### 2.2 Non-Programmatic Assumptions in `parse_chr_dict/`

1. **Hardcoded Tag Maps in `parse_chr_dict/parse.py`**:
   - `SLOT_NAME_TO_TAG` and `SLOT_TAG_MAP` hardcode bidirectional mappings between feature names and bracketed tag titles:
     ```python
     SLOT_NAME_TO_TAG = {
         "prefix_class": "PrefixClass",
         "pronominal": "Pro",
         "h_alt_tag": "H_alt",
         "aspect_class": "AspectClass",
         "variant": "Variant",
         "aspect": "Aspect",
         "tense": "Tense",
     }
     ```
   - Any modification to slot names or tag titles requires manual updates across `parse.py`, `reconstruct.py`, `types.py`, and `segment.py`.
2. **Hardcoded Tag Extraction in `read_parse()`**:
   - In `parse_chr_dict/parse.py`, `read_parse()` loops over tokens and matches literal strings `"PrefixClass"`, `"Pro"`, `"AspectClass"`, `"Variant"`, `"Aspect"`, `"Tense"`, `"DIST"`, `"H_alt"` to populate individual fields of `ParseData`.
3. **Hardcoded Root Boundary Assumptions in `build_root_filter_fsa()`**:
   - `build_root_filter_fsa()` in `parse_chr_dict/parse.py` hardcodes:
     ```python
     # Pre-root boundary tags: all [H_alt=...] tags
     h_alt_tags = [s for s in all_syms if s.startswith("[H_alt=")]
     # Post-root boundary tags: all [AspectClass=...] tags
     asp_tags = [s for s in all_syms if s.startswith("[AspectClass=")]
     ```
   - It directly presumes that `<Root>` is preceded immediately by `[H_alt=...]` and followed immediately by `[AspectClass=...]`. If the template structure shifts (e.g. if H-alt becomes optional or moves), this FSA construction breaks silently.
4. **Hardcoded Tag Serialization in `reconstruct.py` & `types.py`**:
   - `build_tag_str()` in `reconstruct.py` and `ParseData.to_tag_string()` in `types.py` assemble the linear tag string using hardcoded sequential concatenation:
     ```python
     parts.append("[WI]") # if translocutive
     parts.append(f"[DIST={dist}]") # if distributive
     parts.append(f"[PrefixClass={pref}]")
     parts.append(f"[Pro={pro}]")
     parts.append(h_alt)
     parts.append(clean_root)
     parts.append(f"[AspectClass={asp_cls}]")
     if var > 1: parts.append(f"[Variant={var}]")
     parts.append(f"[Aspect={asp}]")
     parts.append(f"[Tense={tense}]")
     ```
   - The ordering is hardcoded in Python rather than being derived from the grammar template.
5. **Hardcoded Stem-Shape morphtactics in `acceptors.py`**:
   - `compile_prefix_stem_shape_acceptor()` hardcodes the sequence:
     `[PrefixClass=c]` followed by `<Pro>`, optional `<H_ALT>`, and root phoneme.
6. **Hardcoded UI Tag Matching in `segment.py`**:
   - `segment.py` uses hardcoded `.startswith("[PrefixClass=")`, `.startswith("[AspectClass=")` to colorize and label morphemes for CLI output.

---

## 3. Target Data Structures: Parameterizing Slots in `verb.yaml`

To eliminate these assumptions, `verb.yaml` becomes the single source of truth for all slot definitions, their internal structure, and the verb template composition.

### 3.1 Slot Configuration Schema in `verb.yaml`

```yaml
slots:
  - name: pronominal
    role: prefix
    rule: $pro_replace
    sources:
      - "verb-pronominal.csv"
    structure:
      - TagGroup: PrefixClass
        optional: false
      - TagGroup: Pro
        optional: false

  - name: aspect
    role: suffix
    rule: $aspect_replace
    sources:
      - "verb-aspect.csv"
      - "verb-aspect-stative.csv"
    structure:
      - TagGroup: AspectClass
        optional: false
      - TagGroup: Variant
        optional: true
      - TagGroup: Aspect
        optional: false

  - name: tense
    role: suffix
    rule: $tense_replace
    sources:
      - "verb-tense.csv"
    structure:
      - TagGroup: Tense
        optional: false

paradigm:
  generate_contingent_markers: true
  template_slots:
    - "<PrepronominalPrefixes>"
    - "slot:pronominal"
    - "<H_alt>"
    - "<Root>"
    - "slot:aspect"
    - "slot:tense"
  open_root_template: "<PrepronominalPrefixes><PrefixClass><Pro><H_alt><Root><AspectClass><Variant><Aspect><Tense>"
```

### 3.2 Semantic Rules for Slot Definitions

1. **`name`**: Unique identifier for the slot (e.g. `pronominal`, `aspect`, `tense`).
2. **`role`**: Positional category relative to root (`prefix`, `suffix`, or `infix`).
3. **`rule`**: Top-level morpheme replacement rule name (e.g. `$pro_replace`, `$aspect_replace`, `$tense_replace`).
4. **`sources`**: List of CSV file paths (relative to config directory) providing the morpheme replacement matrices for this slot.
5. **`structure`**: Ordered list of components that constitute this slot:
   - **`TagGroup`**: Name of the tag category (e.g. `PrefixClass`, `Pro`, `AspectClass`, `Variant`, `Aspect`, `Tense`).
     - Maps to the pattern reference `<TagGroup>` in `phoneme_groups.yaml`.
     - Maps to bracketed tags `[TagGroup=value]`.
   - **`optional`**: Boolean.
     - If `false`, the tag must appear in every realization of this slot.
     - If `true`, the tag may be omitted when the feature takes its default/unmarked value (e.g., `Variant=1` is omitted; `Variant=2`, `Variant=3` are present).
6. **`template_slots`**:
   - Defines the linear sequence of the full template.
   - Non-slot elements (e.g. `<PrepronominalPrefixes>`, `<H_alt>`, `<Root>`) are declared directly.
   - Slot references (`slot:<name>`) expand into the sequence of `<TagGroup>` tags defined in that slot.
   - `open_root_template` can either be verified against `template_slots` or generated automatically by expanding each `slot:<name>` into its constituent `<TagGroup>` tags.

---

## 4. Generic Generator Architecture in `parc_macros/`

With `slots` defined in `verb.yaml`, `parc_macros` becomes completely language-agnostic.

### 4.1 Generic Morpheme Replacement Rule Compiler (`generate_morpheme_replace_rules.py`)

Instead of parsing `# kind: morpheme_replace` headers with hardcoded `CLASS_FEATURE_TO_TAG_TITLE` and hardcoded `[Variant=...]` logic:
1. `generate_morpheme_replace_rules` reads the `slots` list from `verb.yaml`.
2. For each slot:
   - Reads each CSV in `slot["sources"]`.
   - Maps CSV columns to the slot's `structure`:
     - Primary key column (row index) maps to the first non-optional `TagGroup` (e.g. `PrefixClass` or `AspectClass`).
     - Feature columns (header row) map to the final `TagGroup` (e.g. `Pro`, `Aspect`, `Tense`).
     - Middle optional `TagGroup`s (e.g. `Variant`) are populated when cell values specify delimited variants (e.g. `val1; val2; val3`).
   - For a single-tag slot (e.g. `Tense`):
     - Maps each feature directly: `[Tense={feat}] -> surface`.
   - For a two-tag slot (e.g. `PrefixClass` + `Pro`):
     - Maps `[PrefixClass={row}][Pro={col}] -> surface`.
   - For a three-tag slot with optional variant (e.g. `AspectClass` + `Variant`? + `Aspect`):
     - Variant 1 (omitted optional tag): `[AspectClass={row}][Aspect={col}] -> surface`.
     - Variant N (present optional tag): `[AspectClass={row}][Variant={N}][Aspect={col}] -> surface`.
3. Outputs the compiled rule directly to `Phonology/Rules/{rule_name}.yaml`. Zero language-specific code.

### 4.2 Generic Alphabet & Pattern Extraction (`generate_phonology.py`)

Instead of hardcoded `_parse_csv_matrix()` calls for Cherokee files:
1. A generic `SlotDataExtractor`:
   - Iterates through `slots` in `verb.yaml`.
   - Extracts all attested tag values for each `TagGroup` from the slot's declared CSV sources.
   - For optional `TagGroup`s like `Variant`, detects the maximum variant count from delimited cells and generates tags `[Variant=2]`, `[Variant=3]`, etc.
2. Generates `alphabet.yaml`:
   - Emits tag inventory entries grouped by `TagGroup`.
3. Generates `phoneme_groups.yaml`:
   - Emits pattern for each `TagGroup`:
     - `<PrefixClass>`: `[PrefixClass=c1]|[PrefixClass=c2]|...`
     - `<Pro>`: `[Pro=p1]|[Pro=p2]|...`
     - `<AspectClass>`: `[AspectClass=a1]|[AspectClass=a2]|...`
     - `<Variant>`: `([Variant=2]|[Variant=3]|...)?` (enclosing in `()?` if `optional: true`)
     - `<Tense>`: `[Tense=t1]|[Tense=t2]|...`
4. Language-specific phonological context rules:
   - Shift from programmatic generation in Python to declarative YAML rule definitions or modular effect CSVs specified in `verb.yaml` (e.g. `phonology_effects: ["aspect_effects.csv", "verb-pronominal-drop-first-a.csv"]`).

---

## 5. Programmatic Handoff Architecture to `parse_chr_dict/`

### 5.1 The Compiled Grammar Manifest (`slots.json`)

During generation, `parc_macros` writes a compiled `slots.json` (or adds a `slots` section to the compiled `Morphotactics/Paradigm/verb.yaml`):

```json
{
  "slots": [
    {
      "name": "pronominal",
      "role": "prefix",
      "rule": "pro_replace",
      "tags": ["PrefixClass", "Pro"]
    },
    {
      "name": "aspect",
      "role": "suffix",
      "rule": "aspect_replace",
      "tags": ["AspectClass", "Variant", "Aspect"]
    },
    {
      "name": "tense",
      "role": "suffix",
      "rule": "tense_replace",
      "tags": ["Tense"]
    }
  ],
  "template": [
    "<PrepronominalPrefixes>",
    "<PrefixClass>",
    "<Pro>",
    "<H_alt>",
    "<Root>",
    "<AspectClass>",
    "<Variant>",
    "<Aspect>",
    "<Tense>"
  ],
  "tag_to_slot": {
    "PrefixClass": "pronominal",
    "Pro": "pronominal",
    "AspectClass": "aspect",
    "Variant": "aspect",
    "Aspect": "aspect",
    "Tense": "tense"
  },
  "root_boundaries": {
    "left": "<H_alt>",
    "right": "<AspectClass>"
  }
}
```

### 5.2 Consumption in `parse_chr_dict/`

1. **Dynamic Tag Mappings**:
   - `parse_chr_dict/parse.py` reads `slots.json` (or defaults to `chr-config/verb.yaml` if not yet compiled).
   - `SLOT_NAME_TO_TAG` and `SLOT_TAG_MAP` are constructed dynamically from the schema.
2. **Programmatic Root Boundary FSA**:
   - `build_root_filter_fsa()` inspects `root_boundaries`:
     - Left boundary tag pattern: resolves pattern `<H_alt>`.
     - Right boundary tag pattern: resolves pattern `<AspectClass>`.
   - Builds `exact_root_filter` automatically:
     `sigma* + left_fsa + root_fsa + right_fsa + sigma*`
   - Zero hardcoding of `[H_alt=` or `[AspectClass=`.
3. **Programmatic Tag Serialization**:
   - `to_tag_string()` and `build_tag_str()` iterate through the compiled `template` sequence:
     - For each tag element in template:
       - If it is `<Root>`, appends root string.
       - If it is an optional tag and absent/default, skips it.
       - Otherwise, looks up the feature value from `ParseData` or `feature_values` and appends `[{TagGroup}={value}]`.
   - Guarantees 100% template alignment between generation and runtime inflection.

---

## 6. Draft Implementation & Spike Plan

### 6.1 Git Strategy
- Create and switch to spike branch: `feat/inplace-slots-spike`.
- Work is tracked under `TASK-146`.

### 6.2 Implementation Phases
1. **Phase 1: Config Schema & Parameterization**
   - Add `slots` definition to `chr-config/verb.yaml`.
   - Update `parc_macros/schemas/Paradigm.json` to validate `slots` and `template_slots`.
2. **Phase 2: Language-Agnostic Generation in `parc_macros/`**
   - Refactor `generate_morpheme_replace_rules.py` to compile rules directly from the `slots` declaration in `verb.yaml`.
   - Refactor `generate_phonology.py` to extract alphabet and patterns dynamically driven by `slots`.
   - Emit compiled `slots.json` manifest into `chr-generated/`.
3. **Phase 3: Programmatic Runtime Integration in `parse_chr_dict/`**
   - Implement `load_slot_manifest()` helper in `parse_chr_dict`.
   - Update `parse_chr_dict/parse.py` to build `SLOT_NAME_TO_TAG`, `SLOT_TAG_MAP`, and `build_root_filter_fsa()` from slot manifest.
   - Update `reconstruct.py` and `types.py` to utilize programmatic slot tag ordering.
4. **Phase 4: Full Verification & Parity Testing**
   - Regenerate all grammar assets: `python parc_macros/generate_markers.py chr-config chr-generated`.
   - Run full test suite: `PYTHONPATH=. pytest`.
   - Run dictionary parser verification: `YAML_DIR=chr-generated/ python -u -m parse_chr_dict`.
   - Validate zero regression on `roots.csv`.
