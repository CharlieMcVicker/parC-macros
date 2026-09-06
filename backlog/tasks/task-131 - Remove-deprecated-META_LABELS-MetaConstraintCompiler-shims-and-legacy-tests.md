---
id: TASK-131
title: 'Remove deprecated META_LABELS, MetaConstraintCompiler shims, and legacy tests'
status: To Do
assignee: []
created_date: '2026-09-06 17:19'
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
- [ ] #1 Remove deprecated META_LABELS, MetaConstraintCompiler, FeatureConstraint, MetaLabelDefinition, and MatchMode shims from parse_chr_dict/meta_label_compiler.py
- [ ] #2 Remove or migrate legacy shim test assertions in tests/test_meta_label_compiler.py and tests/test_parse_chr_dict_baseline.py
- [ ] #3 Verify all callers import directly from parse_chr_dict.types and parse_chr_dict.derive
- [ ] #4 Run full pytest suite and verify 100% tests pass cleanly with zero warnings
<!-- AC:END -->
