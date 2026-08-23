---
id: TASK-70
title: >-
  Investigate why 'it is making a sound' is missing from roots.csv and
  errors.csv
status: In Progress
assignee:
  - '@agent'
created_date: '2026-08-23 22:35'
updated_date: '2026-08-23 22:35'
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
- [ ] #1 Locate entry ID for 'it is making a sound'
- [ ] #2 Identify why it is skipped or unwritten
- [ ] #3 Fix __main__.py so every row is recorded in either roots.csv or errors.csv
- [ ] #4 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Search chr-corpus/corpus.csv for 'making a sound' or 'sound'.
2. Inspect __main__.py skip conditions (e.g. spaces in forms, unhandled entry types, or row_written handling).
3. Apply fix to __main__.py so skipped multi-word or unparsed rows are written to errors.csv.
4. Verify all corpus rows are accounted for.
<!-- SECTION:PLAN:END -->
