---
id: TASK-29
title: Fix pytest test failures
status: Done
assignee:
  - '@myself'
created_date: '2026-07-10 23:14'
updated_date: '2026-07-10 23:14'
labels: []
dependencies: []
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Address the two failing tests in the test suite:\n1. Fix test_can_import failure by symlinking packages from local venv in ~/code/parC.\n2. Fix test_generation_cherokee failure by updating the assertion to include the new 'e-a' aspect class.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Symlink missing packages from ~/code/parC local venv into conda environment to fix test_can_import
- [x] #2 Update test_generation_cherokee assertion to include 'e-a' aspect class
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Locate local venv in ~/code/parC and find where _pywrapfst is.\n2. Symlink the missing libraries/packages to the parC-macros conda environment.\n3. Modify tests/test_generation.py to include 'e-a' in the aspect_class assertion.\n4. Run pytest to verify all tests pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Resolved the pytest test suite failures:\n- Symlinked pywrapfst and _pywrapfst from parC local venv into conda environment to fix pynini import in test_can_import.\n- Updated Cherokee generation assertions in tests/test_generation.py to include new e-a aspect class and k_a_stem prefix class.
<!-- SECTION:FINAL_SUMMARY:END -->
