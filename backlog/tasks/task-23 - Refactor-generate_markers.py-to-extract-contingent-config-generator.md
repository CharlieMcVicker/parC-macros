---
id: TASK-23
title: Refactor generate_markers.py to extract contingent config generator
status: Done
assignee:
  - '@agent'
created_date: '2026-07-10 20:15'
updated_date: '2026-07-10 20:15'
labels: []
dependencies: []
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extract the ContingentFeatureMarkers and unified Paradigm generation logic into a separate helper function generate_contingent_configs in parc_macros/generate_markers.py to keep the main function clean and structured.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement generate_contingent_configs helper function
- [x] #2 Call generate_contingent_configs in main function
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Refactored generate_markers.py by extracting the contingent configurations generation logic to a helper function generate_contingent_configs. Verified all tests still pass.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Extracted contingent configurations generation logic to a helper function generate_contingent_configs, simplifying main and aligning with code patterns.
<!-- SECTION:FINAL_SUMMARY:END -->
