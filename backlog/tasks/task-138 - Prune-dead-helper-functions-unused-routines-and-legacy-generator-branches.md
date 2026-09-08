---
id: TASK-138
title: 'Prune dead helper functions, unused routines, and legacy generator branches'
status: Done
assignee:
  - '@subagent-138'
created_date: '2026-09-06 18:07'
updated_date: '2026-09-08 12:52'
labels: []
dependencies: []
priority: medium
type: chore
ordinal: 148000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove uncalled helper routines and legacy CLI paths across parse_chr_dict (str_to_lexical_hashable, parses_by_form, get_roots_for_parses, parse.py main loop, generate_legacy_aspect_config and --legacy in create_aspect_class_csv.py, and dead non-in-place fallback in reconstruct.memoized_inflect).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove unused str_to_lexical_hashable, parses_by_form, get_roots_for_parses, and obsolete main() interactive CLI from parse_chr_dict/parse.py
- [x] #2 Remove generate_legacy_aspect_config, generate_inplace_aspect_csv alias, and --legacy CLI argument from parse_chr_dict/create_aspect_class_csv.py
- [x] #3 Remove dead non-in-place grammar fallback branch (inflect() with legacy_features) from parse_chr_dict/reconstruct.py memoized_inflect
- [x] #4 Verify all unit and integration tests pass cleanly
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Pruned dead helper routines and legacy branches across parse_chr_dict: removed str_to_lexical_hashable, parses_by_form, get_roots_for_parses, and obsolete main() interactive CLI from parse.py; pruned generate_legacy_aspect_config, generate_inplace_aspect_csv alias, dead writer setups, and --legacy CLI argument from create_aspect_class_csv.py; eliminated non-in-place grammar fallback branch from reconstruct.memoized_inflect and removed unused imports; updated tests/test_aspect_class_csv.py to use generate_inplace_aspect_config; verified all 129 test cases pass.
<!-- SECTION:FINAL_SUMMARY:END -->
