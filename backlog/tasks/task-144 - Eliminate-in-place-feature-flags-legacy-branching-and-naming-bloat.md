---
id: TASK-144
title: 'Eliminate in-place feature flags, legacy branching, and naming bloat'
status: Done
assignee:
  - '@agent'
created_date: '2026-09-08 13:15'
updated_date: '2026-09-08 13:26'
labels:
  - refactor
  - cleanup
dependencies: []
priority: high
type: chore
ordinal: 154000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove the in-place vs legacy feature flags and dual-path branching across parc_macros and parse_chr_dict. Treat the standard morpheme architecture as the default and only grammar model, rename modules and functions to remove 'inplace' naming bloat, and prune dead legacy trailing-label generators and parsers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove --in-place CLI flag and is_in_place_mode check, making morpheme generation the only path in parc_macros/generate_markers.py and parc_macros/generate_morpheme_replace_rules.py
- [x] #2 Delete dead legacy trailing-label generators (generate_contingent_configs, generate_standard_feature_markers, generate_paradigm_configs, _generate_legacy_rules) in parc_macros
- [x] #3 Rename parc_macros/generate_inplace_phonology.py to parc_macros/generate_phonology.py and clean function names (extract_phonology_data, generate_alphabet, generate_patterns, generate_phonology_rules)
- [x] #4 Remove is_inplace_grammar and legacy read_labels branching from parse_chr_dict/parse.py, renaming read_inplace_parse to read_parse and removing inplace from helper dictionaries/constants
- [x] #5 Update ParseData.to_inplace_string to to_tag_string and rename build_inplace_tag_str/inflect_inplace_string in parse_chr_dict/reconstruct.py
- [x] #6 Update aspect class writer and generator names in parse_chr_dict/create_aspect_class_csv.py
- [x] #7 Consolidate test files, remove dead legacy tests, update all test fixtures and callers, and update AGENTS.md
- [x] #8 Full test suite passes cleanly and grammar generation succeeds without flags
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Refactor parc_macros/generate_inplace_phonology.py -> parc_macros/generate_phonology.py and rename functions extract_phonology_data, generate_alphabet, generate_patterns, generate_phonology_rules.
2. Refactor parc_macros/generate_morpheme_replace_rules.py to remove is_in_place_mode, in_place flag, and _generate_legacy_rules, keeping only clean 2-tag morpheme rule generation.
3. Refactor parc_macros/generate_markers.py to remove --in-place flag, in_place argument, dead legacy generators (generate_contingent_configs, generate_standard_feature_markers, generate_paradigm_configs), rename generate_inplace_paradigm_config -> generate_paradigm_config, and streamline generate_markers.
4. Refactor parse_chr_dict/types.py to rename to_inplace_string -> to_tag_string.
5. Refactor parse_chr_dict/reconstruct.py to rename build_inplace_tag_str -> build_tag_str and inflect_inplace_string -> inflect_tag_str.
6. Refactor parse_chr_dict/create_aspect_class_csv.py to rename setup_inplace_aspect_class_writer -> setup_aspect_class_writer and generate_inplace_aspect_config -> generate_aspect_config.
7. Refactor parse_chr_dict/parse.py to eliminate is_inplace_grammar, rename read_inplace_parse -> read_parse, prune legacy read_labels, and clean all constants and cache names.
8. Update all test files and fixtures: remove obsolete legacy tests (test_generation.py, test_backwards_compatibility_ac3), consolidate duplicate tests (test_clean_inplace_generation.py and test_inplace_compilation.py), rename test files and functions to remove inplace naming.
9. Regenerate chr-generated/ using updated generate_markers without flags and run the full test suite.
10. Update AGENTS.md documentation.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Eliminated all 'inplace'/'in-place' feature flags, dual-path branching, and naming bloat across parc_macros and parse_chr_dict. Standardized morpheme-tag parsing and generation as the default and only grammar architecture. Renamed generate_inplace_phonology.py to generate_phonology.py, pruned dead legacy trailing-label generators (generate_contingent_configs, generate_standard_feature_markers, generate_paradigm_configs, _generate_legacy_rules), pruned legacy parser branching and obsolete test files (test_generation.py, test_morpheme_replace.py, test_prefix_template.py, test_insertion_template.py), renamed test suites (test_compilation.py, test_clean_generation.py, test_config.py, test_markers_generation.py), and updated AGENTS.md. All 120 tests pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
