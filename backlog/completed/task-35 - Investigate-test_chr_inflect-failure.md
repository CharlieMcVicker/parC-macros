---
id: TASK-35
title: Investigate test_chr_inflect failure
status: Done
assignee:
  - '@myself'
created_date: '2026-07-11 02:58'
updated_date: '2026-07-11 15:39'
labels: []
dependencies: []
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate why tests/test_chr_inflect.py:79 AssertionError is failing compared to transduction_test.py, and come up with ideas before clearing cache.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify difference between test_chr_inflect.py:79 and transduction_test.py
- [x] #2 Identify root cause of failure
- [x] #3 Provide ideas/actions before clearing cache
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Identified tag-ordering mismatch between the query stringification (which sorted lexical/inflectional tags alphabetically) and the FST graph domain (which compiles lexical POS feature order followed by inflectional alphabetical order). Fixed by ordering the lexical tags manually in the test query.
<!-- SECTION:FINAL_SUMMARY:END -->
