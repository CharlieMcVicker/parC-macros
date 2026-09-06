---
id: TASK-32
title: Update inflection test to use infer_lexical_features
status: Done
assignee:
  - '@agent'
created_date: '2026-07-10 23:54'
updated_date: '2026-07-11 00:19'
labels: []
dependencies: []
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the test_chr_inflect.py file to call build_inflect_graph_for_root_regex with infer_lexical_features=True and verify it works
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update tests/test_chr_inflect.py
- [x] #2 Run pytest tests/test_chr_inflect.py -s and log output
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated test_chr_inflect.py to utilize infer_lexical_features=True when constructing the FST via build_inflect_graph_for_root_regex. Added a test case for specific root inflection (which maps correctly using pynini.cross) and a test case for wildcard regex roots. Documented and verified that wildcard root FSTs successfully insert the correct contingent prefix and suffix markers, though the identity of the root itself is not mapped one-to-one because of the nature of pynini.cross on wildcard patterns.
<!-- SECTION:FINAL_SUMMARY:END -->
