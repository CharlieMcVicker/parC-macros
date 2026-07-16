---
id: TASK-45
title: Absorb optional features complexity into parC-macros
status: Done
assignee:
  - '@agent'
created_date: '2026-07-16 20:23'
updated_date: '2026-07-16 20:26'
labels: []
dependencies: []
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
For each 'optional' feature, generate an additional option 'UNMARKED' which has an empty marker set [] each time it would need to have markers in a featuremarker or contingentfeaturemarker file.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify optional features from config/verb.yaml
- [x] #2 Generate UNMARKED with [] in non-contingent FeatureMarkers
- [x] #3 Generate UNMARKED with [] in ContingentFeatureMarkers under each class value
- [x] #4 Include UNMARKED in the list of values for the optional feature in FeatureDefinitions
- [x] #5 Run validation tests to verify expected output is generated
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Identify optional features in verb_config by checking features defined with 'optional: true'.\n2. Modify verb_config['features'] in-place to append 'UNMARKED' to the values of each optional feature. This ensures update_feature_definitions automatically lists 'UNMARKED' in FeatureDefinitions.\n3. Modify generate_paradigm_configs and generate_standard_feature_markers to insert an 'UNMARKED': [] entry in the markers dictionary for any optional feature.\n4. Modify generate_contingent_configs to insert 'UNMARKED': [] under each class mapping for any optional feature.\n5. Run existing tests and verify the generated output files.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented support for optional features by absorbing their complexity. Identified optional features from the configuration, appended 'UNMARKED' to their feature values list in FeatureDefinitions, and generated empty marker list 'UNMARKED: []' in standard FeatureMarkers and under each class in ContingentFeatureMarkers. Wrote validation tests and verified everything passed successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
