---
id: TASK-46
title: Create test for optional feature inflection
status: Done
assignee:
  - '@agent'
created_date: '2026-07-16 21:01'
updated_date: '2026-07-16 21:02'
labels: []
dependencies: []
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a test verifying inflection with combinations of optional features set to on/off (present/UNMARKED/omitted) to diagnose transduction failures.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create a test verifying inflection under different optional feature combinations
- [x] #2 Identify if transduction fails when optional features are unmarked or omitted
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a new test case in tests/test_generation.py or as a separate test file.\n2. In the test, load the FST/inflect graph for Cherokee.\n3. Attempt inflection of a root verb (e.g., from Cherokee test dictionary/corpus) with all combinations of optional features (translocutive, distributive, partitive) set to either '+' (on), 'UNMARKED' (off), or omitted.\n4. Log/assert which combinations result in successful inflections versus failures.\n5. Present the results and explain the behavior.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Ran the combination test on 'atat' showing that indeed, only when all three optional features (translocutive, distributive, partitive) are set to '+' (active) does inflection succeed. Any combination with 'UNMARKED' or 'OMITTED' fails to inflect.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created tests/test_optional_combinations.py to run all 27 combinations of the three optional features. The results confirmed the hypothesis: only the combination with all features set to '+' successfully inflects, while any other combination results in an empty output lattice.
<!-- SECTION:FINAL_SUMMARY:END -->
