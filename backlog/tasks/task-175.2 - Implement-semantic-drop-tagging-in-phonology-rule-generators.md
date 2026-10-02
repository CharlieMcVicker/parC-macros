---
id: TASK-175.2
title: 'Implement semantic [drop] tagging in phonology rule generators'
status: Done
assignee:
  - '@subagent'
created_date: '2026-10-02 13:17'
updated_date: '2026-10-02 13:42'
labels:
  - fst
  - parc-macros
  - phonology
dependencies:
  - TASK-175.1
modified_files:
  - parc_macros/generate_phonology.py
  - chr-config/Phonology/Inventory/alphabet.yaml
  - chr-generated/Phonology/Inventory/alphabet.yaml
  - chr-generated/Phonology/Rules/mark_stem_initial_vowel.yaml
  - chr-generated/Phonology/Rules/drop_stem_initial_vowel.yaml
  - chr-generated/Phonology/Rules/drop_root_final.yaml
  - tests/fixtures/min-min-config/Phonology/Inventory/alphabet.yaml
  - tests/fixtures/min-min-insertion-config/Phonology/Inventory/alphabet.yaml
  - tests/test_markers_generation.py
parent_task_id: TASK-175
type: feature
ordinal: 187000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Non-concatenative edge drops (stem-initial vowel dropping and final root dropping) currently mark segments with transient `[TEMP]` and then erase them to empty string. To allow downstream consumers to recognize both the canonical root and the elided phone, update `parc_macros/generate_phonology.py` to replace `[TEMP]` with a semantic `[drop]` tag attached to the elided phone (e.g. `a[drop]`, `v[drop]`, `<Phone>[drop]`).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `generate_phonology.py` generates `mark_stem_initial_vowel.yaml` using `[drop]` instead of `[TEMP]` (e.g. `a` -> `a[drop]`, `v` -> `v[drop]`)
- [x] #2 `generate_phonology.py` updates `drop_stem_initial_vowel.yaml` to retain elided characters in the intermediate representation
- [x] #3 `generate_phonology.py` generates `drop_root_final.yaml` retaining the dropped phone before `[drop]` (e.g. `<Phone>[drop]`)
- [x] #4 Generated phonology YAML rules pass `python parc_macros/yaml_validation.py chr-generated/`
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add [drop] to alphabet.yaml under Temp Tags in chr-config and test fixtures
2. Update generate_phonology.py to generate mark_stem_initial_vowel.yaml using [drop] (e.g. vowel -> vowel[drop])
3. Update generate_phonology.py to generate drop_stem_initial_vowel.yaml retaining elisions in intermediate representation
4. Update generate_phonology.py to generate drop_root_final.yaml tagging elided root-final phones with [drop] (via Phone left context and right_context triggers)
5. Update tests/test_markers_generation.py expectations for [drop] tagging
6. Regenerate chr-generated and validate against JSON schemas
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced transient [TEMP] markers in phonological drop rule generators with semantic [drop] tagging. Updated mark_stem_initial_vowel.yaml to mark stem-initial vowels as vowel[drop] (e.g., a[drop], v[drop]), updated drop_stem_initial_vowel.yaml to retain elided segments in the intermediate representation, and updated drop_root_final.yaml to insert [drop] after the elided root-final phone(s). Added [drop] to alphabet inventories, regenerated chr-generated/, and verified schema validation and pytest suite (13/13 passing in test_markers_generation.py).
<!-- SECTION:FINAL_SUMMARY:END -->
