---
id: TASK-147
title: Generate open_root_template from slot spec and template definition
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-08 15:22'
updated_date: '2026-09-08 15:28'
labels: []
dependencies: []
priority: high
type: enhancement
ordinal: 157000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define template structure in chr-config/verb.yaml using slot references
- [x] #2 Implement generate_open_root_template in parc_macros to derive open_root_template dynamically from template elements and slots
- [x] #3 Remove hardcoded open_root_template from chr-config/verb.yaml
- [x] #4 Ensure generated Morphotactics/Paradigm/verb.yaml receives the dynamically compiled open_root_template
- [x] #5 Update tests to verify dynamic template derivation and preserve all test passes
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented dynamic derivation of open_root_template from slot specifications and linear template definition in parc_macros. Removed hardcoded open_root_template from chr-config/verb.yaml in favor of structured slot references (slot:pronominal, slot:aspect, slot:tense) under paradigm.template. Updated Paradigm.json schema to support template. Updated generate_phonology.py to derive open_root_template dynamically if not explicitly specified. Updated tests across test_yaml_validation.py, test_config.py, and added unit test test_derive_open_root_template() in test_markers_generation.py. All 128 tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
