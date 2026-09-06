---
id: TASK-43
title: Support Optional Features and Middle Voice Stage
status: Done
assignee:
  - '@agent'
created_date: '2026-07-15 19:25'
updated_date: '2026-07-15 19:36'
labels: []
dependencies: []
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement optional feature definitions, parse optional features, and implement the middle_voice stage inserting 'ata' prefix when realized.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Parse and identify optional features from config
- [x] #2 Add middle_voice lexical feature with value 'ata' and mark it optional
- [x] #3 Implement middle_voice stage in config and generate rules
- [x] #4 Ensure middle_voice stage is ordered after tense but before drop_stem_initial_vowel
- [x] #5 Verify and test generation and parsing of middle_voice
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented support for optional features. Added the 'middle_voice' optional lexical feature flag in the new 'middle_voice' stage, properly ordered after tense and before drop_stem_initial_vowel. Simplified the implementation by generating general/non-contingent FeatureMarkers rather than ContingentFeatureMarkers for optional features that do not specify a class_feature, and dropping the class_feature and paradigm columns from its definition CSV. Added a unit test validating output files, values, schema compliance, and stage ordering.
<!-- SECTION:FINAL_SUMMARY:END -->
