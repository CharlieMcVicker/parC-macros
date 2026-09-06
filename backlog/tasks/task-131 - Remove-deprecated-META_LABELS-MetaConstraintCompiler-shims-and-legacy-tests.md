---
id: TASK-131
title: 'Remove deprecated META_LABELS, MetaConstraintCompiler shims, and legacy tests'
status: Done
assignee:
  - '@myself'
created_date: '2026-09-06 17:19'
updated_date: '2026-09-06 17:30'
labels: []
dependencies: []
ordinal: 141000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Complete the retirement of the deprecated meta_label_compiler module. Remove META_LABELS, MetaConstraintCompiler, FeatureConstraint, MetaLabelDefinition, and MatchMode shims now that the active pipeline purely uses VerbForm and VerbEntryType in parse_chr_dict.types and parse_chr_dict.derive. Clean up legacy tests in test_meta_label_compiler.py and test_parse_chr_dict_baseline.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove deprecated META_LABELS, MetaConstraintCompiler, FeatureConstraint, MetaLabelDefinition, and MatchMode shims from parse_chr_dict/meta_label_compiler.py
- [x] #2 Remove or migrate legacy shim test assertions in tests/test_meta_label_compiler.py and tests/test_parse_chr_dict_baseline.py
- [x] #3 Verify all callers import directly from parse_chr_dict.types and parse_chr_dict.derive
- [x] #4 Run full pytest suite and verify 100% tests pass cleanly with zero warnings
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove deprecated META_LABELS, MetaConstraintCompiler, FeatureConstraint, MetaLabelDefinition, and MatchMode shims from parse_chr_dict/meta_label_compiler.py\n2. Update callers in parse_chr_dict/__main__.py, parse_chr_dict/near_misses.py, and parse_chr_dict/reconstruct.py to import directly from parse_chr_dict.types and parse_chr_dict.derive\n3. Clean up legacy shim test assertions in tests/test_meta_label_compiler.py and tests/test_parse_chr_dict_baseline.py, updating imports to parse_chr_dict.types and parse_chr_dict.derive\n4. Run full pytest suite (including with -W error) to ensure 100% tests pass cleanly with zero warnings
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Retired the deprecated META_LABELS, MetaConstraintCompiler, FeatureConstraint, MetaLabelDefinition, and MatchMode shims from parse_chr_dict/meta_label_compiler.py. Migrated all pipeline callers (parse_chr_dict/__main__.py, parse_chr_dict/near_misses.py, parse_chr_dict/reconstruct.py) and legacy test suites (tests/test_meta_label_compiler.py, tests/test_parse_chr_dict_baseline.py) to pure domain imports in parse_chr_dict.types and parse_chr_dict.derive. Verified 100% test pass rate with zero warnings across 427 tests via pytest -W error.
<!-- SECTION:FINAL_SUMMARY:END -->
