---
id: TASK-37
title: Implement Cherokee parse test with open ended root and feature inference
status: Done
assignee:
  - '@agent'
created_date: '2026-07-11 15:50'
updated_date: '2026-07-11 15:54'
labels: []
dependencies: []
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a test that uses an open ended '<Phone>*' root with infer lexical features to parse all the examples in tests/test_chr_parse.csv, build the inflection graph, invert it, and parse the features out. Stop working if parC doesn't support that.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create test using open ended '<Phone>*' root
- [x] #2 Infer lexical features to parse examples in test_chr_parse.csv
- [x] #3 Build inflection graph, invert it, and parse features
- [x] #4 Determine if parC supports it, otherwise stop
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully created a new test file tests/test_chr_wildcard_parse.py that builds an inflection graph with an open-ended '<Phone>*' root and infer_lexical_features=True, inverts it to a parse graph, and verifies that the parse lattice accepts the expected tag sequences for all cases in test_chr_parse.csv. The tests pass successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
