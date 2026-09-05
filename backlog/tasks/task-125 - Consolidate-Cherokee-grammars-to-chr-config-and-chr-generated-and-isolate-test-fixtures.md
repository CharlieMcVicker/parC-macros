---
id: TASK-125
title: >-
  Consolidate Cherokee grammars to chr-config and chr-generated and isolate test
  fixtures
status: Done
assignee:
  - '@subagent'
created_date: '2026-09-05 22:21'
updated_date: '2026-09-05 22:31'
labels: []
dependencies: []
ordinal: 135000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Promote clean in-place Cherokee grammar to canonical chr-config and chr-generated, remove obsolete in-place and baseline variants, relocate toy/test configs to tests/fixtures/, and update all pipeline defaults and tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Relocate spanish-*, min-min-*, and min-min-insertion-* folders into tests/fixtures/ and remove unused min-test-* folders
- [x] #2 Replace chr-config with chr-clean-inplace-config, regenerate chr-generated, and delete chr-inplace-config, chr-clean-inplace-config, and chr-inplace-generated
- [x] #3 Update parse_chr_dict (__main__.py, parse.py, acceptors.py, create_aspect_class_csv.py) and parse_dict.sh to default to chr-config and chr-generated
- [x] #4 Update is_inplace_grammar() in parse.py to detect in-place template tags on chr-generated
- [x] #5 Update all unit and integration tests across tests/ to reference chr-config, chr-generated, and tests/fixtures/
- [x] #6 Run full pytest suite and verify 100% test pass rate
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 All acceptance criteria checked
- [x] #2 Full pytest suite passes with zero regressions
- [x] #3 Root repository directory has only canonical chr-config and chr-generated folders
- [x] #4 Final summary added to task
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create tests/fixtures/ and move spanish-config, spanish-generated, spanish-reference, min-min-config, min-min-generated, min-min-insertion-config, min-min-insertion-generated there; remove min-test-config and min-test-generated.
2. Replace chr-config with chr-clean-inplace-config; delete chr-inplace-config and chr-clean-inplace-config.
3. Regenerate chr-generated from chr-config and delete chr-inplace-generated.
4. Update parse_chr_dict (__main__.py, parse.py, acceptors.py, create_aspect_class_csv.py) and parse_dict.sh to default to chr-config and chr-generated.
5. Update is_inplace_grammar() in parse.py so it inspects paradigm template or detects chr-generated without relying on 'inplace' in directory path.
6. Update all test files in tests/ to reference chr-config, chr-generated, and tests/fixtures/.
7. Run full pytest suite, verify 100% tests pass, check DoD, and add final summary.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Consolidated Cherokee grammars to canonical chr-config and chr-generated, isolated test-only fixtures into tests/fixtures/, and updated pipeline and test suite defaults. Promoted chr-clean-inplace-config to chr-config, regenerated in-place chr-generated (100% parity with former chr-inplace-generated), and removed obsolete chr-inplace-config, chr-clean-inplace-config, chr-inplace-generated, and unused min-test-* directories. Relocated spanish-* and min-min-* directories into tests/fixtures/. Updated parse_chr_dict (__main__.py, parse.py, acceptors.py, create_aspect_class_csv.py), parse_dict.sh, and scratch/verify_roots_compatibility.py to canonical chr-config and chr-generated paths and enhanced is_inplace_grammar() to recognize chr-generated. Updated all test suites across tests/ and verified 100% test pass rate across all 421 pytest cases.
<!-- SECTION:FINAL_SUMMARY:END -->
