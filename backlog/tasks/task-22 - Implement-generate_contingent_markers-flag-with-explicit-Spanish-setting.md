---
id: TASK-22
title: Implement generate_contingent_markers flag with explicit Spanish setting
status: Done
assignee:
  - '@agent'
created_date: '2026-07-10 20:14'
updated_date: '2026-07-10 20:14'
labels: []
dependencies: []
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename the contingent generation flag back to use_contingent_features / generate_contingent_markers, defaulting to false, and explicitly define generate_contingent_markers: false in the Spanish config and generate_contingent_markers: true in Cherokee config.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update generator to use generate_contingent_markers/use_contingent_features
- [x] #2 Update spanish-config/verb.yaml with generate_contingent_markers: false
- [x] #3 Update chr-config/verb.yaml with generate_contingent_markers: true
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Changed the dynamic generation flag to generate_contingent_markers/use_contingent_features. Added generate_contingent_markers: false explicitly to the Spanish configuration and generate_contingent_markers: true to Cherokee configuration. Verified both outputs generate correctly and all tests pass.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Renamed the flag back to use_contingent_features / generate_contingent_markers (defaulting to false) to generate standard class-specific paradigms. Explicitly configured Spanish with generate_contingent_markers: false and Cherokee with generate_contingent_markers: true, and verified all tests pass perfectly.
<!-- SECTION:FINAL_SUMMARY:END -->
