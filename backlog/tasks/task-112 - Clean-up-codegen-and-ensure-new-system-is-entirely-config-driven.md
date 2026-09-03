---
id: TASK-112
title: Clean up codegen and ensure new system is entirely config driven
status: Done
assignee:
  - '@agent'
created_date: '2026-09-03 18:10'
updated_date: '2026-09-03 18:29'
labels: []
dependencies: []
ordinal: 122000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
1. No hardcoded tag lists in alphabet (merge data on disk with generated in memory before spell out)
2. No hardcoded class lists in rules (generate in memory)
3. Remove redundant rule-trigger csv in the config directory
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Integrate in-place alphabet tag generation dynamically in memory from CSVs, eliminating hardcoded tag lists in source alphabet.yaml
- [x] #2 Integrate in-place phoneme group pattern generation dynamically in memory, eliminating hardcoded pattern unions in source phoneme_groups.yaml
- [x] #3 Generate drop_root_final and drop_stem_initial_vowel rules in memory from trigger annotations and configs, eliminating hardcoded class lists in rules
- [x] #4 Remove redundant rule-trigger CSV files (verb-aspect-drop-final.csv and verb-aspect-drop-final-two.csv) from source config
- [x] #5 Create clean third config directory and verify generation parity against chr-inplace-generated (983 FST states and schema validation)
- [x] #6 Deprecate/remove obsolete parc_macros/generate_inplace_config.py standalone script
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Analyze current hardcoded in-place artifacts and diffs between generate_inplace_config.py and chr-inplace-config.
2. Build new in-memory generation modules in parc_macros (dynamic alphabet tags, phoneme patterns, and rule triggers from CSVs).
3. Update generate_morpheme_replace_rules.py to strip * and @ triggers from verb-aspect.csv and supply them to drop_root_final rule generation.
4. Construct clean third config directory (e.g. chr-inplace-clean-config) with minimal base alphabet, base patterns, base rules, and zero redundant trigger CSVs.
5. Integrate in-memory phonology and rule generation into generate_markers.py when in_place=True.
6. Verify output parity against chr-inplace-generated across all YAML files, schema validation, and FST state count (983 states).
7. Deprecate / remove obsolete generate_inplace_config.py.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Consolidated in-place phonology and rule generation into generate_markers.py. Created clean third config directory chr-clean-inplace-config with zero hardcoded morpheme tags or class lists. Removed redundant drop-final CSVs and obsolete generate_inplace_config.py. Verified 100% YAML schema validation and FST compilation parity (983 states).
<!-- SECTION:FINAL_SUMMARY:END -->
