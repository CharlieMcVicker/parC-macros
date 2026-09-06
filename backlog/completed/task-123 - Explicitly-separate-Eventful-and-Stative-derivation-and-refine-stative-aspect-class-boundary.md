---
id: TASK-123
title: >-
  Explicitly separate Eventful and Stative derivation and refine stative aspect
  class boundary
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 19:48'
updated_date: '2026-09-04 19:50'
labels: []
dependencies: []
priority: high
type: enhancement
ordinal: 133000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refine stative aspect class prefix filtering (stative aspect classes all begin 'stative'), separate _derive_eventful and _derive_stative in derive.py for transparent profiling, and prune non-matching aspect classes in Step 2 of derivation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Ensure get_specialized_parse_graph strictly checks c.startswith('[AspectClass=stative') for stative and excludes it for eventful
- [x] #2 Separate derivation into distinct _derive_eventful and _derive_stative functions in derive.py so profiling metrics accurately reflect category runtime
- [x] #3 Add Step 2 aspect class pre-filtering in derivation to skip parsing strings incompatible with candidate hypothesis aspect classes
- [x] #4 Verify all 421+ unit and regression tests pass with zero regressions
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 All 421+ pytest tests pass
- [x] #2 Zero regressions across baseline tests
- [x] #3 Profiler cleanly separates Eventful and Stative runtimes
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update parse.py get_specialized_parse_graph to use c.startswith('[AspectClass=stative') for Stative and exclude for Eventful.
2. Separate derivation into _derive_eventful and _derive_stative in derive.py.
3. Add Step 2 aspect class pre-filtering in derivation.
4. Run full pytest suite (421+ tests).
5. Run cProfile to confirm clean separation and further runtime reduction.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Strictly restricted stative aspect classes via c.startswith('[AspectClass=stative') in parse.py (and excluded all stative classes from Eventful FSTs). Separated derivation into distinct _derive_eventful and _derive_stative functions in derive.py, clarifying profiler output (showing _derive_stative only takes 1.19s across the entire corpus vs. 17.3s for _derive_eventful). Added Step 2 aspect class pre-filtering in derivation to prune strings incompatible with surviving candidate hypotheses, dropping read_inplace_parse calls further from 361,232 to 200,366 (total time 5.9s). All 421 tests pass with zero regressions.
<!-- SECTION:FINAL_SUMMARY:END -->
