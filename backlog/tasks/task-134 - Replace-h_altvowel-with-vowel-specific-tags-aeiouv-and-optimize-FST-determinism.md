---
id: TASK-134
title: >-
  Replace h_alt=vowel with vowel-specific tags (aeiouv) and optimize FST
  determinism
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-06 17:55'
updated_date: '2026-09-06 18:00'
labels: []
dependencies: []
priority: high
type: enhancement
ordinal: 144000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace generic [H_alt=vowel] tag with specific vowel quality tags (a, e, i, o, u, v) in phonology rules, inventory, lexicon, parser, and tests to eliminate non-deterministic vowel branching. Identify and apply other FST determinism optimizations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Replace [H_alt=vowel] with specific vowel quality tags in phonology rules, inventory, and patterns
- [x] #2 Update parse_chr_dict (h_alternation, derive, types, parse) to recognize and handle vowel-specific h_alt tags
- [x] #3 Update roots.csv and roots_inplace.csv to use vowel-specific tags
- [x] #4 Identify and apply additional determinism optimizations across phonology and morphotactics
- [x] #5 Verify 100% pytest pass rate with zero regressions
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update chr-config/Phonology/Inventory/alphabet.yaml with vowel-specific H_alt tags and TempTags.
2. Update chr-config/Phonology/Rules/h_alternation.yaml with deterministic targeted rules per vowel quality and string_map realization.
3. Regenerate chr-generated/ assets using generate_markers.
4. Update parse_chr_dict modules (h_alternation.py, parse.py, derive.py, types.py) to support vowel-specific tags.
5. Update roots.csv and roots_inplace.csv to replace generic [H_alt=vowel] with specific [H_alt=vowel_{v}] tags.
6. Update tests in test_h_alternation_targeted.py and add coverage for determinism.
7. Run complete test suite and verify 100% pass rate.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the generic [H_alt=vowel] tag with specific vowel quality tags ([H_alt=vowel_a], [H_alt=vowel_e], [H_alt=vowel_i], [H_alt=vowel_o], [H_alt=vowel_u], [H_alt=vowel_v]) across phonology rules, inventory, morphotactics, dictionary parsing, and roots data.

Key Optimizations & Changes:
1. Replaced non-deterministic realize_h_vowel rule (which previously emitted '<V>', branching over all 6 vowels) with an exact 1:1 string_map mapping each [TEMP_VOWEL_{X}_H] strictly to vowel {x}.
2. Defined deterministic 3-step targeted phonology rules per vowel quality (mark_h_vowel_{v}, tag_h_vowel_{v}, delete_trigger_vowel_{v}) in chr-config/Phonology/Rules/h_alternation.yaml.
3. Updated chr-config/Phonology/Inventory/alphabet.yaml and regenerated chr-generated/ assets via generate_markers.
4. Extended parse_chr_dict modules (h_alternation.py, parse.py) to recognize and handle the vowel-specific tags.
5. Successfully resolved and converted all 87 vowel alternating roots in roots.csv and roots_inplace.csv to their exact vowel qualities (32 vowel_a, 26 vowel_i, 19 vowel_v, 10 vowel_o).
6. Updated tests/test_h_alternation_targeted.py with exact determinism assertions and updated FST state count checks across integration suites.
7. Verified 100% test pass rate across all 417 pytest tests.
<!-- SECTION:FINAL_SUMMARY:END -->
