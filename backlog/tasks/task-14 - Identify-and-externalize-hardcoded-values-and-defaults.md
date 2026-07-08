---
id: TASK-14
title: Identify and externalize hardcoded values and defaults
status: Done
assignee:
  - '@agent'
created_date: '2026-07-04 20:59'
updated_date: '2026-07-04 21:03'
labels: []
dependencies: []
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Locate hardcoded grammar/metadata values (e.g. conjugation_class, other default metadata values) in the code and move them to metadata on disk (e.g. config files).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Search codebase for hardcoded grammar values and default metadata references
- [x] #2 Document found occurrences and design a metadata structure for them
- [x] #3 Move identified hardcoded and default values to config files on disk
- [x] #4 Refactor code to load these values dynamically from config
- [x] #5 Ensure all tests pass successfully
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Load verb.yaml (or verb_spec.yaml) and identify:\n   - Part of speech name (from filename base: verb).\n   - Class feature: require the field 'class_feature' to be specified in the yaml.\n   - Default CSV metadata (e.g. under defaults: section in verb.yaml).\n2. Update spanish-config/verb.yaml on disk to include these metadata/default definitions.\n3. Refactor parc_macros/generate_markers.py to use these dynamic config settings instead of hardcoded values, raising an error if 'class_feature' is missing.\n4. Ensure all tests pass successfully.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored generate_markers.py and tests/test_generation.py to remove all hardcoded values (conjugation_class, default metadata values, and POS-specific prefixes/filenames). Instead, these values are dynamically loaded from the part of speech config file (e.g. spanish-config/verb.yaml) which now explicitly defines 'class_feature' and a 'defaults' dictionary.
<!-- SECTION:FINAL_SUMMARY:END -->
