---
id: TASK-160
title: 'Investigate regression for corpus entries 821, 825, 1045 in errors.csv'
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 14:11'
updated_date: '2026-09-10 14:14'
labels: []
dependencies: []
ordinal: 170000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate why entries 821, 825, and 1045 became errors after recent changes, determine root cause, and implement fix.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Investigate failure reasons for entries 821, 825, 1045
- [x] #2 Fix root cause without breaking entry 1516 or test suite
- [x] #3 Verify all tests pass and entries derive correctly
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Identified that premature mutated_h_roots pruning in derive.py discarded [H_alt=none] when [TEMP_H]s -> hs identity mapping allowed spurious [H_alt=drop] parses on /hs/ suffixes. Removed aggressive pruning so unmutated [H_alt=none] roots survive; verified entries 821, 825, 1045 derive correctly and errors.csv dropped to 135 rows.
<!-- SECTION:FINAL_SUMMARY:END -->
