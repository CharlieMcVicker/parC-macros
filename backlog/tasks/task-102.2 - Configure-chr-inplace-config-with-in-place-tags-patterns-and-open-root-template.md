---
id: TASK-102.2
title: >-
  Configure chr-inplace-config with in-place tags, patterns, and open root
  template
status: In Progress
assignee:
  - '@subagent'
created_date: '2026-09-02 19:51'
updated_date: '2026-09-02 20:24'
labels: []
dependencies:
  - TASK-102.1
modified_files:
  - parc_macros/schemas/Inventory.json
  - parc_macros/generate_inplace_config.py
  - chr-inplace-config/Phonology/Inventory/alphabet.yaml
  - chr-inplace-config/Phonology/Patterns/phoneme_groups.yaml
  - chr-inplace-config/verb.yaml
  - chr-inplace-config/Phonology/Rules/drop_root_final.yaml
  - chr-inplace-config/Phonology/Rules/drop_stem_initial_vowel.yaml
  - chr-inplace-config/Phonology/Rules/h_alternation.yaml
  - tests/test_yaml_validation.py
  - tests/test_inplace_config.py
parent_task_id: TASK-102
priority: high
type: feature
ordinal: 103000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Clone verified chr-config to chr-inplace-config, declare pattern definitions for <PrepronominalPrefixes> and <Root>, define in-place tags in Inventory and Patterns, update open_root_template in verb.yaml, and adapt drop_root_final and drop_stem_initial_vowel to use local contexts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Clone clean chr-config/ to chr-inplace-config/
- [x] #2 Define <PrepronominalPrefixes> and <Root> in chr-inplace-config/Phonology/Patterns/phoneme_groups.yaml
- [x] #3 Define in-place tags in Inventory/alphabet.yaml and Patterns/phoneme_groups.yaml
- [x] #4 Update open_root_template in chr-inplace-config/verb.yaml to <PrepronominalPrefixes><PrefixClass><Pro><H_ALT>?<Root><AspectClass><Aspect><TenseClass><Tense>
- [x] #5 Adapt drop_root_final.yaml and drop_stem_initial_vowel.yaml to use local trigger contexts
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Clone clean chr-config/ to chr-inplace-config/ (excluding cache artifacts).
2. Implement parc_macros/generate_inplace_config.py to programmatically extract morphemes, classes, and drop triggers from CSV data:
   - Extract prefix classes and 22 pronominals from verb-pronominal.csv
   - Extract ~92 aspect classes and 5 aspects from verb-aspect.csv
   - Extract tense classes and 7 tenses from verb-tense.csv
   - Extract final drop triggers from verb-aspect-drop-final*.csv
   - Extract stem initial vowel drop triggers from verb-pronominal-drop-first-*.csv
3. Programmatically generate in-place tags in chr-inplace-config/Phonology/Inventory/alphabet.yaml.
4. Programmatically generate pattern groups in chr-inplace-config/Phonology/Patterns/phoneme_groups.yaml (<PrepronominalPrefixes>, <Root>, <PrefixClass>, <Pro>, <AspectClass>, <Aspect>, <TenseClass>, <Tense>, <Morpheme>).
5. Update open_root_template in chr-inplace-config/verb.yaml to '<PrepronominalPrefixes><PrefixClass><Pro><H_ALT>?<Root><AspectClass><Aspect><TenseClass><Tense>'.
6. Programmatically adapt chr-inplace-config/Phonology/Rules/drop_root_final.yaml and drop_stem_initial_vowel.yaml with local trigger contexts.
7. Validate all YAML files with parc_macros schema validation and PyYAML, and verify symbol table compilation with parC.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
### In-Place Configuration Implementation for Cherokee Verb Grammar

#### Summary of Changes
1. Automated Configuration Generator (`parc_macros/generate_inplace_config.py`):
   - Implemented a data-first programmatic generation pipeline that directly parses CSV sources (`verb-pronominal.csv`, `verb-aspect.csv`, `verb-tense.csv`, `verb-aspect-drop-final*.csv`, `verb-pronominal-drop-first-*.csv`).
   - Automatically derives in-place inventory tags and pattern regular expressions from CSV data.

2. Isolated Testbed Grammar (`chr-inplace-config/`):
   - Cloned clean `chr-config/` into `chr-inplace-config/`.
   - Inventory (`Phonology/Inventory/alphabet.yaml`):
     - Registered 7 prefix class tags (`[PrefixClass=...]`), 22 pronominal tags (`[Pro=...]`), 92 aspect class tags (`[AspectClass=...]`), 5 aspect tags (`[Aspect=...]`), 2 tense class tags (`[TenseClass=...]`), 7 tense tags (`[Tense=...]`).
     - Preserved all standard phones, temporary tags, and legacy morpheme markers.
   - Patterns (`Phonology/Patterns/phoneme_groups.yaml`):
     - Defined `<PrepronominalPrefixes>`: `"[WI]?[DIST]?"`.
     - Defined `<Root>`: `"<V>?(<C>+<V>)*<C>*"`.
     - Defined pattern groups for `<PrefixClass>`, `<Pro>`, `<AspectClass>`, `<Aspect>`, `<TenseClass>`, `<Tense>`, and updated `<Morpheme>`.
   - Verb Paradigm Template (`verb.yaml`):
     - Updated `open_root_template` to `"<PrepronominalPrefixes><PrefixClass><Pro><H_ALT>?<Root><AspectClass><Aspect><TenseClass><Tense>"`.
   - Context-Sensitive Dropping Rules (`Phonology/Rules/`):
     - Adapted `drop_root_final.yaml` to match local right contexts for dropping triggers (`hvsk-nh[inf2]`, `hvsk-nh[inf4]`, `hvsk-n`, `apl`, `apl[imp2]`).
     - Adapted `drop_stem_initial_vowel.yaml` to match local left contexts `<PrefixClass><Pro><H_ALT>?` for dropping triggers (`a_stem` with 3sg.A/3sg.B, `v_stem` with 3sg.B).
     - Defined composite rule sequences `$drop_root_final` and `$drop_stem_initial_vowel`.
     - Updated `h_alternation.yaml` to accept `<Pro>|[Pro]` as left context for `delete_h_none` and `delete_temp_tags`.

3. Schema and Validation Enhancements:
   - Updated `Inventory.json` schema regex in both `parc_macros` and `parC` to support tags with nested brackets (e.g. `[AspectClass=become[inf2]]`).
   - Fixed `set_yaml_dir` in `parC/constants.py` to dynamically update `_YAML_DIR`.
   - Added automated tests in `tests/test_yaml_validation.py` and `tests/test_inplace_config.py`. All 342 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
