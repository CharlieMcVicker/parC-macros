---
id: TASK-116
title: >-
  Save h_root and h_alt_tag in roots.csv and reject incompatible alternating
  forms
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 17:24'
updated_date: '2026-09-04 17:56'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 126000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enforce strict root equality across forms during dictionary parsing and validation, ensuring that alternating forms must share the identical base h_root and vary only by morphotactic h_alt_tag. Replace glottal_root with h_alt_tag in roots.csv and the LexicalVerb pipeline. Incompatible root pairs (such as shirt rows anhaw vs anhiw/aniw) will correctly fail rather than storing disparate roots.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Replace glottal_root column with h_alt_tag in roots.csv (ROOTS_FIELDNAMES) and LexicalVerb serialization
- [x] #2 Enforce that all parsed forms in derive_hypotheses_for_forms match hyp.h_root (strip_h_alt_tags(p_data.root) == hyp.h_root) with h_alt_tag tracking the alternation
- [x] #3 Update reconstruct.py validation to inflect all forms using h_root and h_alt_tag directly without separate glottal_root strings
- [x] #4 Verify that shirt entries (192, 193, 195, 567, 568, 569) fail parsing and are logged to errors.csv instead of storing incompatible roots (anhaw, anhiw) in roots.csv
- [x] #5 Ensure all unit tests and regression tests pass cleanly
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update parse_chr_dict/types.py: replace glottal_root with h_alt_tag in LexicalVerb serialization (to_dict, to_row_dict, lexical_tuple).
2. Update parse_chr_dict/__main__.py: replace glottal_root with h_alt_tag in ROOTS_FIELDNAMES and hypothesis sorting.
3. Update parse_chr_dict/meta_label_compiler.py: enforce strict root equality strip_h_alt_tags(p_data.root) == hyp.h_root across all forms (including glottal triggers), tracking the morphotactic alternation solely via h_alt_tag and removing determine_h_alt_glottal_root.
4. Update parse_chr_dict/reconstruct.py: validate all forms using h_root and h_alt_tag directly without disparate glottal_root strings.
5. Update parse_chr_dict/near_misses.py and test assertions in tests/test_meta_label_compiler.py and tests/test_lexical_verb_types.py for the h_alt_tag schema.
6. Regenerate roots.csv, confirm shirt rows (192, 193, 195, 567, 568, 569) are logged to errors.csv, and verify the full test suite passes.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced glottal_root with h_alt_tag in roots.csv, LexicalVerb, and validation pipelines. Enforced strict base root equality (strip_h_alt_tags(p_data.root) == hyp.h_root) across all alternating forms, pruning incompatible pairs (such as anhaw and anhiw for shirt entries 192, 193, 195, 567, 568, 569, which now properly fail into errors.csv). Updated reconstruct.py and meta_label_compiler.py to route alternation directly via h_alt_tag and in-place phonology rules. All 412 unit and regression tests pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
