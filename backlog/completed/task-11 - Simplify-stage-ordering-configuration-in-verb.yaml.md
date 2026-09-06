---
id: TASK-11
title: Simplify stage ordering configuration in verb.yaml
status: Done
assignee:
  - '@agent'
created_date: '2026-07-04 20:50'
updated_date: '2026-07-04 20:50'
labels: []
dependencies: []
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace both 'stages' and 'order' fields in spanish-config/verb.yaml with a single 'stages' field representing the ordered stages, and update generate_markers.py to use it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Replace 'stages' and 'order' in verb.yaml with a single ordered 'stages' field
- [x] #2 Update generate_markers.py to read order from the single 'stages' list
- [x] #3 Ensure tests still pass
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the duplicate stages and order fields in spanish-config/verb.yaml with a single ordered 'stages' field, updated generate_markers.py to read stage ordering from 'stages' if 'order' is absent, and verified all tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
