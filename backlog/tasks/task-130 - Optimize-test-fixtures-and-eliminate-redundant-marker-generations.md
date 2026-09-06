---
id: TASK-130
title: Optimize test fixtures and eliminate redundant marker generations
status: Done
assignee:
  - '@myself'
created_date: '2026-09-06 17:16'
updated_date: '2026-09-06 17:17'
labels: []
dependencies: []
ordinal: 140000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove redundant teardown marker generations, optimize test fixtures across test_inplace_compilation and related tests, and address remaining test suite inefficiencies.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Audit and eliminate redundant teardown marker generation in test_inplace_compilation.py
- [x] #2 Optimize shared test environment setup across inplace tests
- [x] #3 Verify all pytests pass cleanly and measure improved suite duration
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed redundant marker generation in setup_inplace_env fixture teardown in tests/test_inplace_compilation.py. Wrapped legacy META_LABELS shim definition in parse_chr_dict/meta_label_compiler.py to suppress 42 internal deprecation warnings during module import while maintaining external caller deprecation notices. Confirmed all 428 pytests pass in 4.93s with zero warnings.
<!-- SECTION:FINAL_SUMMARY:END -->
