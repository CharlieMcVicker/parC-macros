---
id: TASK-94
title: >-
  Explore hypothesis-constrained output filter lattice optimization for
  dictionary parsing
status: Done
assignee:
  - '@agent-subagent'
created_date: '2026-08-28 19:33'
updated_date: '2026-08-28 20:05'
labels: []
dependencies: []
ordinal: 93000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate whether restricting/intersecting the output lattice of dictionary parsing with expected root hypotheses (derived from the 1st entry or earlier entries) and expected H-alternation tags/pronouns speeds up parsing time and reduces search space.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Benchmark current dictionary parsing time across forms 2-5
- [x] #2 Design and prototype hypothesis template lattice / output filter FST
- [x] #3 Evaluate whether FST compilation overhead is offset by inference speedup
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Unit tests pass (pytest tests/)
- [x] #2 Performance benchmark and memory profiling comparison completed
- [x] #3 Hypothesis filter FSA and Option A/Option B implementations documented
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Profile/Benchmark baseline timing for dictionary forms 2-5 parsing.
2. Implement a dedicated function `build_hypothesis_filter_fsa(hypothesis, ...)` that consumes a single root/H-alternation hypothesis and produces the constrained filter FSA.
3. Implement Option A (Union Template): Iterate through hypotheses in a loop, call `build_hypothesis_filter_fsa` for each, fold/union them into a single filter FSA, and compose with the parsing lattice/transducer.
4. Implement Option B (Per-Hypothesis Intersect): Loop through each hypothesis, call `build_hypothesis_filter_fsa` to build its individual filter FSA, intersect with the parse lattice, and evaluate.
5. Benchmark and compare Option A vs. Option B vs. Baseline (measuring FST compilation/union overhead vs. lattice pruning speedup and memory usage).
6. Verify correctness against the existing dictionary regression test suite.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Explored hypothesis-constrained output filter lattice optimization for dictionary parsing across Cherokee verb forms 2-5. Designed and implemented build_hypothesis_filter_fsa, Option A (Union Template: folding candidate hypothesis filters into a single union FSA), and Option B (Per-Hypothesis Intersect: intersecting candidate hypothesis filters individually against the surface parse lattice). Benchmarked Baseline (Dynamic Lattice) vs. Option A vs. Option B across dictionary corpus entries. Findings show Option A suffers severe FST compilation overhead (97.5% time spent in NFA union/compilation, resulting in 15x slowdown vs. baseline), whereas Option B achieves a 4.55x speedup over baseline with a 150x reduction in peak memory (0.08 MB vs 11.97 MB) when filtering with known/cached root constraints. Added regression unit tests in tests/test_hypothesis_filter_lattice.py and benchmark script in parse_chr_dict/benchmark_hypothesis_filter.py; all 347 test cases pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
