---
id: TASK-175.3
title: >-
  Auto-generate surface cleanup rules and emit dual verb and verb_segmented
  paradigms
status: Done
assignee:
  - '@subagent'
created_date: '2026-10-02 13:17'
updated_date: '2026-10-02 14:44'
labels:
  - fst
  - parc-macros
  - paradigms
dependencies:
  - TASK-175.2
modified_files:
  - parc_macros/generate_morpheme_replace_rules.py
  - parc_macros/generate_phonology.py
  - parc_macros/generate_markers.py
  - chr-config/Phonology/Inventory/alphabet.yaml
  - tests/test_config.py
  - tests/test_markers_generation.py
parent_task_id: TASK-175
type: feature
ordinal: 188000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
To support both clean surface FST parsing (for dictionary derivation) and structured intermediate FST outputs (for game deck export), `parc_macros/generate_markers.py` must auto-generate a `strip_intermediate_markup.yaml` rule and emit two paradigm configurations in `chr-generated/Morphotactics/Paradigm/`: `verb.yaml` (full cascade with cleanup) and `verb_segmented.yaml` (intermediate cascade without cleanup). This guarantees 100% surface backward-compatibility while exposing first-class segmented inflection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `parc_macros/generate_markers.py` generates `chr-generated/Phonology/Rules/strip_intermediate_markup.yaml` deleting tags, dropped segments, and hyphens
- [x] #2 `generate_markers.py` emits `chr-generated/Morphotactics/Paradigm/verb.yaml` with `strip_intermediate_markup` as the final stage
- [x] #3 `generate_markers.py` emits `chr-generated/Morphotactics/Paradigm/verb_segmented.yaml` without the cleanup stage
- [x] #4 All 129 existing tests pass with 100% parity on surface `verb` paradigm via `pytest`
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update generate_morpheme_replace_rules.py to generate both clean surface rules (pro_replace, aspect_replace, tense_replace) and segmented rules (pro_replace_segmented, aspect_replace_segmented, tense_replace_segmented).
2. Update generate_phonology.py to generate both clean surface rules (drop_root_final, drop_stem_initial_vowel) and segmented rules (drop_root_final_segmented, drop_stem_initial_vowel_segmented).
3. Update generate_markers.py to emit both verb.yaml (using clean surface rules) and verb_segmented.yaml (using segmented rules) in Morphotactics/Paradigm/.
4. Regenerate all markers into chr-generated/ and validate with yaml_validation.py.
5. Update tests in test_markers_generation.py and test_config.py to verify dual generation and run full test suite with pytest to ensure 100% test passing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented dual clean surface and segmented rule generation across morpheme replacement and phonology rule generators. generate_markers.py generates both verb.yaml (surface) and verb_segmented.yaml (segmented). Separated hyphen into <Boundary> in alphabet.yaml so Sonorants are preserved. Verified full test suite of 167 tests passes.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Auto-generated clean surface and segmented morpheme replacement and phonological dropping rules. Emitted dual Morphotactics paradigms verb.yaml and verb_segmented.yaml. Full test suite (167 tests) passes with 100% parity.
<!-- SECTION:FINAL_SUMMARY:END -->
