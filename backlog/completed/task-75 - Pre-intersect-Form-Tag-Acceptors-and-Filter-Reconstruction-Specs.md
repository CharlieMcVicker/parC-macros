---
id: TASK-75
title: Pre-intersect Form Tag Acceptors and Filter Reconstruction Specs
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-23 23:20'
updated_date: '2026-08-23 23:20'
labels: []
dependencies: []
ordinal: 74000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Pre-intersect static FORM tag acceptors in MetaConstraintCompiler and filter MetaLabelCombinations in reconstruct.py based on active form specifications to eliminate redundant inflect() and compile_restricted_tag_acceptor() calls.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Pre-compile static FORM acceptors in MetaConstraintCompiler
- [x] #2 Filter valid MetaLabelCombination candidates in reconstruct.py
- [x] #3 Verify all test suites pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Pre-compile static [FORM=...] meta-label acceptors in MetaConstraintCompiler during initialization.\n2. Filter MetaLabelCombination candidates in reconstruct.py based on form capabilities (allows_set_a) before calling validate/inflect.\n3. Run test suite to verify correctness.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Pre-compiled static [FORM=...] meta-label acceptors in MetaConstraintCompiler.__init__ so single-form acceptors are warmed up during initialization. Verified all test suites pass.
<!-- SECTION:FINAL_SUMMARY:END -->
