---
id: TASK-70
title: >-
  Investigate why 'it is making a sound' is missing from roots.csv and
  errors.csv
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 22:35'
updated_date: '2026-09-06 17:21'
labels: []
dependencies: []
ordinal: 69000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Locate 'it is making a sound' in chr-corpus/corpus.csv, trace why it is skipped in parse_chr_dict __main__.py or derivation, and fix.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Locate entry ID for 'it is making a sound'
- [x] #2 Identify why it is skipped or unwritten
- [x] #3 Fix __main__.py so every row is recorded in either roots.csv or errors.csv
- [x] #4 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Search chr-corpus/corpus.csv for 'making a sound' or 'sound'.
2. Inspect __main__.py skip conditions (e.g. spaces in forms, unhandled entry types, or row_written handling).
3. Apply fix to __main__.py so skipped multi-word or unparsed rows are written to errors.csv.
4. Verify all corpus rows are accounted for.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Identified entry 1715 ('it is making a sound') and verified that dictionary pipeline now accounts for all 707 corpus rows across roots.csv (497) and errors.csv (210) with 0 unrecorded rows. All 428 tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
