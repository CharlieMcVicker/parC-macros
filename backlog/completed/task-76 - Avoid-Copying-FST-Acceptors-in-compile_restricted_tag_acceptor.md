---
id: TASK-76
title: Avoid Copying FST Acceptors in compile_restricted_tag_acceptor
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-23 23:29'
updated_date: '2026-08-23 23:29'
labels: []
dependencies: []
ordinal: 75000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Return immutable cached FST references from compile_restricted_tag_acceptor and build_slot_mask without calling .copy(), since Pynini operations produce new FST objects during composition.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove unnecessary .copy() calls on cached FST acceptors in MetaConstraintCompiler
- [x] #2 Verify test suite passes without side effects
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify compile_restricted_tag_acceptor, build_slot_mask, and build_query_lattice to return cached FST references directly without .copy().\n2. Run pytest suite to confirm FST operations remain pure and tests pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed unnecessary .copy() calls in build_slot_mask, compile_restricted_tag_acceptor, and build_query_lattice. Direct references to cached immutable FST acceptors are returned directly, saving allocation/copy time. Verified all baseline dictionary parse tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
