---
id: TASK-50
title: Fix non-contingent feature marker generation to merge multiple CSVs
status: Done
assignee:
  - '@antigravity'
created_date: '2026-07-16 21:56'
updated_date: '2026-07-16 22:05'
labels: []
dependencies: []
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Group and merge standard (non-contingent) feature markers by feature before writing out to avoid overwriting rules when multiple CSVs map to the same feature.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Standard feature markers for a feature are merged across multiple CSVs
- [ ] #2 Existing tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify generate_contingent_configs in parc_macros/generate_markers.py to group and merge standard (non-contingent) feature markers by feature before calling generate_standard_feature_markers().\n2. Run pytest to ensure everything works and no regressions are introduced.\n3. Verify verb_translocutive.yaml is generated with all rules from verb-wi-drop.csv, verb-wi-realize.csv, and verb-wi.csv.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed non-contingent feature marker generation by grouping and merging standard feature markers by feature name before writing YAML files. This prevents multiple CSV files targeting the same non-contingent feature (such as translocutive) from overwriting each other, correctly merging all rules (e.g. drop_WI, insert_WI, and add_WI) into a single unified FeatureMarkers file.
<!-- SECTION:FINAL_SUMMARY:END -->
