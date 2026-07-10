---
id: TASK-28
title: Create empty 3sg.A pronominal entry for e_stem
status: Done
assignee:
  - '@agent'
created_date: '2026-07-10 22:37'
updated_date: '2026-07-10 22:38'
labels: []
dependencies: []
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update generation to also generate a blank suffixing/pronominal operation for 3sg.A e_stem instead of dropping it when the value is empty.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update marker generation to output empty/blank entry for 3sg.A e_stem
- [x] #2 Verify that the generated output contains the blank operation
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated marker generation to accept empty values if the kind is not 'rule', and updated the test suite to verify the blank pronominal entry for e_stem 3sg.A is generated.
<!-- SECTION:FINAL_SUMMARY:END -->
