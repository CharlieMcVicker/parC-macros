---
id: TASK-15
title: Support multiple class inflections and dynamic class feature parsing
status: Done
assignee:
  - '@agent'
created_date: '2026-07-08 17:12'
updated_date: '2026-07-08 17:17'
labels: []
dependencies: []
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend parC-macros to support multiple class features (e.g. prefix_class and aspect_class for Cherokee) by parsing 'class_feature' from CSV metadata instead of a single global configuration value, and generate corresponding paradigms and exponence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement class_feature parsing from CSV metadata
- [x] #2 Add support for multiple class inflections in generate_markers.py
- [x] #3 Verify and test with Cherokee (chr- folders) manually and spanish-colang reference via existing test suite
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully added support for multiple class inflections. Refactored 'generate_markers.py' to parse 'class_feature' dynamically from each individual CSV's metadata comments rather than relying on a global single class_feature configuration in verb.yaml. Added support for 'aspect_class' in Cherokee (chr- folders), updated the metadata of both Spanish and Cherokee CSVs, created a sample aspect CSV for Cherokee, and added a programmatic test validating Cherokee generation which runs as part of the test suite.
<!-- SECTION:FINAL_SUMMARY:END -->
