---
id: TASK-36
title: Investigate slowness of tests/test_chr_inflect.py
status: Done
assignee:
  - '@myself'
created_date: '2026-07-11 15:31'
updated_date: '2026-07-11 15:39'
labels: []
dependencies: []
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Analyze why tests/test_chr_inflect.py takes a long time to run despite simple patterns. We need to identify what exactly is taking a long time.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Profile/measure the execution of tests/test_chr_inflect.py
- [x] #2 Identify the bottleneck in FST/FSA generation, composition, or caching
- [x] #3 Provide suggestions/findings on how to optimize compilation times
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Profiled the Cherokee paradigm compilation and identified two major bottlenecks: 1) redundant lexicon dataframe parses and YAML loads/validations, and 2) sequential transducer composition where intermediate state spaces grew progressively because of stem projection. Implemented DataFrame caching, LRU YAML validation caching, and static tag-domain difference composition, reducing composition time from ~17s to ~2.7s and overall test execution to ~12.8s.
<!-- SECTION:FINAL_SUMMARY:END -->
