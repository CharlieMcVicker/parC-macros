---
id: TASK-6
title: Implement generation validation tests against spanish-colang reference
status: Done
assignee:
  - '@myself'
created_date: '2026-07-04 19:28'
updated_date: '2026-07-04 20:13'
labels: []
dependencies: []
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create pytest-based tests that run the generation script to expand compressed data and deeply check that the output matches the reference spanish-colang files exactly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create test cases in the tests/ directory that execute the generator
- [x] #2 Deeply check generated outputs against reference spanish-colang files
- [x] #3 Ensure tests pass cleanly in the current environment
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented pytest-based validation tests in tests/test_generation.py. The tests generate FeatureMarkers configurations from test.csv to a temporary directory, validate them using the yaml schema, and perform deep equality comparisons against the reference files from spanish-colang. All tests pass successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
