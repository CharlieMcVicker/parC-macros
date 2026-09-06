---
id: TASK-27
title: Update contingent feature generation for new nested schema
status: Done
assignee: []
created_date: '2026-07-10 21:36'
updated_date: '2026-07-10 21:36'
labels: []
dependencies: []
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the contingent feature marker generation in parc_macros to generate the simplified schema containing 'kind', 'features' (list of features), and 'markers' (nested objects matching 'features' depth/order, with leaf levels being arrays of marker objects).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update generate_contingent_configs to output the simplified nested schema
- [x] #2 Remove legacy keys class_name and feature from contingent markers output
- [x] #3 Verify and validate Cherokee contingent tests pass with new schema
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated generate_contingent_configs to generate contingent feature markers under the simplified schema using 'features' array instead of 'class_name' and 'feature' keys. Updated ContingentFeatureMarkers.json schema to define and validate the recursive nested markers representation. Verified that all Cherokee tests pass and validate successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
