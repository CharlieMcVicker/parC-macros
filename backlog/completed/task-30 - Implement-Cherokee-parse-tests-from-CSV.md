---
id: TASK-30
title: Implement Cherokee parse tests from CSV
status: Done
assignee:
  - '@agent'
created_date: '2026-07-10 23:20'
updated_date: '2026-07-10 23:23'
labels: []
dependencies: []
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify tests/test_chr_parse.py to read test cases from a CSV file on disk with columns: surface,root,pronominal,prefix_class,aspect,aspect_class.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove old Spanish parsing tests from tests/test_chr_parse.py
- [x] #2 Load Cherokee test examples from a CSV file
- [x] #3 Generate parsed results and assert they match the features specified in the CSV
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Modified test_chr_parse.py to load test examples dynamically from test_chr_parse.csv, matching both morphological and lexical features. Removed the outdated Spanish tests.
<!-- SECTION:FINAL_SUMMARY:END -->
