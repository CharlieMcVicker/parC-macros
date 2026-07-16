---
id: TASK-48
title: >-
  Test leaving optional feature values in definitions but omitting them from
  marker files
status: In Progress
assignee:
  - '@agent'
created_date: '2026-07-16 21:07'
updated_date: '2026-07-16 21:07'
labels: []
dependencies: []
ordinal: 47000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Re-add UNMARKED to FeatureDefinitions, but keep it omitted from FeatureMarkers and ContingentFeatureMarkers. Then run tests to verify combinations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Re-add UNMARKED to FeatureDefinitions in generate_markers.py
- [ ] #2 Regenerate configurations and verify combination test results
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify generate_markers.py to re-add UNMARKED to the values in FeatureDefinitions, but keep it excluded from FeatureMarkers and ContingentFeatureMarkers.\n2. Regenerate the markers for Cherokee.\n3. Run test_optional_combinations.py to see the outcome.
<!-- SECTION:PLAN:END -->
