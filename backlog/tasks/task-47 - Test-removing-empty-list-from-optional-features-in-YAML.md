---
id: TASK-47
title: Test removing empty list from optional features in YAML
status: Done
assignee:
  - '@agent'
created_date: '2026-07-16 21:03'
updated_date: '2026-07-16 21:04'
labels: []
dependencies: []
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify generate_markers.py to not output UNMARKED or empty list markers in the YAML files, then run test_optional_combinations.py to see the results.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Modify generate_markers.py to exclude UNMARKED/empty lists from generated configurations
- [x] #2 Verify test results using test_optional_combinations.py
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify generate_markers.py to prevent adding UNMARKED to the values in FeatureDefinitions and prevent generating UNMARKED mappings in FeatureMarkers/ContingentFeatureMarkers.\n2. Regenerate the markers for Cherokee.\n3. Run test_optional_combinations.py to see the outcome.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Running the combinations test after removing UNMARKED resulted in: 1. Unrecognized token exceptions when trying to use UNMARKED (since it is no longer defined in FeatureDefinitions), and 2. Empty output lattices ([]) when omitting the optional features. This confirms that without explicit UNMARKED definitions or some other form of default handling, the FST fails to inflect unless all features are active.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed UNMARKED generation from parc_macros/generate_markers.py. Re-ran test_optional_combinations.py. Observed that passing UNMARKED now throws unrecognized token errors, and omitting the features still results in empty output lattices.
<!-- SECTION:FINAL_SUMMARY:END -->
