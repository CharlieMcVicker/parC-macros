---
id: TASK-16
title: Move language-specific features in generate_markers to config
status: Done
assignee:
  - '@antigravity'
created_date: '2026-07-08 17:40'
updated_date: '2026-07-08 17:41'
labels: []
dependencies: []
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove hardcoded tense and mood features from generate_markers.py and put them in verb.yaml configuration so that the generation logic is fully generic.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define feature_markers_keys and filename_suffix_keys in config/verb.yaml
- [x] #2 Refactor generate_markers.py to dynamically handle config-defined metadata keys
- [x] #3 Ensure reference validation and generation tests pass successfully
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored the generation script generate_markers.py to be completely language- and feature-agnostic. Replaced the hardcoded 'tense' and 'mood' mappings with generic metadata parsing, and introduced configurable 'feature_markers_keys' and 'filename_suffix_keys' mappings in 'verb.yaml' configuration. Verified that all Spanish and Cherokee test generation pipelines compile and pass tests successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
