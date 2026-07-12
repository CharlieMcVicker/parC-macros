---
id: TASK-39
title: Create separate test CSV for open-ended parses
status: Done
assignee:
  - '@agent'
created_date: '2026-07-12 01:46'
updated_date: '2026-07-12 01:47'
labels: []
dependencies: []
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a new CSV file for test cases that are only checked against the open-ended/wildcard parse graph, and update test_chr_wildcard_parse.py to read from it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create tests/test_chr_wildcard_parse.csv with test cases
- [x] #2 Update tests/test_chr_wildcard_parse.py to load from the new CSV
- [x] #3 Ensure tests pass
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created tests/test_chr_wildcard_parse.csv with header row and modified tests/test_chr_wildcard_parse.py to read test cases from both CSV files. Verified that pytest successfully ran and passed all tests.
<!-- SECTION:FINAL_SUMMARY:END -->
