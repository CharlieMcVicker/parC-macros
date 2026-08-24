---
id: TASK-85
title: Migrate H-alternation unit test cases to CSV-driven test suite
status: Done
assignee:
  - '@myself'
created_date: '2026-08-24 16:04'
updated_date: '2026-08-24 16:04'
labels: []
dependencies: []
ordinal: 84000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace hardcoded test cases in tests/test_h_alternation.py with external CSV test datasets loaded dynamically by the test harness.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create CSV files defining test cases for all H-alternation phonological operations and compatibility checks
- [x] #2 Refactor tests/test_h_alternation.py to read test cases from the CSV files
- [x] #3 Verify all test cases pass via pytest against both Python and FST implementations
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create CSV test files under tests/data/ covering all test cases: triggers, drop_first_h, first_h_to_glottal, deaffricated_lateral, glottal_clusters, vowel_restoration, possible_alternates, and grades_are_compatible.\n2. Update tests/test_h_alternation.py to load test fixtures dynamically from these CSV files.\n3. Run pytest across tests/test_h_alternation.py and tests/test_h_alternation_corpus.py and ensure 100% pass rate.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Migrated all hardcoded Python test cases in tests/test_h_alternation.py to structured external CSV datasets under tests/data/ (h_alternation_triggers.csv, h_alternation_phonology_rules.csv, h_alternation_vowel_restoration.csv, h_alternation_possible_alternates.csv, h_alternation_grades_compatible.csv). Refactored tests/test_h_alternation.py to dynamically parameterize test runs from these CSV files. All 288 test cases pass across both Python and FST implementations.
<!-- SECTION:FINAL_SUMMARY:END -->
