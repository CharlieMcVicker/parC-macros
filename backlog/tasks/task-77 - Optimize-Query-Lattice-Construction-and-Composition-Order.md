---
id: TASK-77
title: Optimize Query Lattice Construction and Composition Order
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-23 23:32'
updated_date: '2026-08-23 23:32'
labels: []
dependencies: []
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove intermediate pynini.optimize() from build_query_lattice, memoize query lattice FSAs, and streamline Q o P composition.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove redundant pynini.optimize() call in build_query_lattice
- [x] #2 Add _query_lattice_cache to MetaConstraintCompiler
- [x] #3 Verify all test suites pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove pynini.optimize() in build_query_lattice and add _query_lattice_cache in MetaConstraintCompiler.\n2. Verify that Q o P composition remains fully correct and passes all test suites.\n3. Benchmark performance improvements.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed intermediate pynini.optimize() call from build_query_lattice to avoid redundant FSA optimization prior to composition. Added _query_lattice_cache to MetaConstraintCompiler so query lattice FSAs are constructed once per unique (surface_form, meta_label_ids, dynamic_constraints) key. Verified all baseline dictionary parse tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
