---
id: TASK-95
title: >-
  Adopt Option B per-hypothesis filter intersection as default parsing path and
  clean up Option A
status: Done
assignee:
  - '@agent-subagent'
created_date: '2026-08-28 20:10'
updated_date: '2026-08-28 20:13'
labels: []
dependencies: []
ordinal: 94000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate Option B (per-hypothesis output filter FSA intersection) as the default derivation path in parse_chr_dict and meta_label_compiler to achieve the ~4.5x speedup across dictionary forms 2-5. Remove experimental Option A union code and update all callers and tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Make Option B the default implementation in derive_hypotheses_for_forms
- [x] #2 Remove Option A union template code and unused artifacts
- [x] #3 Ensure full regression test suite passes cleanly
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update `parse_chr_dict/meta_label_compiler.py`: replace the legacy/fallback logic in `derive_hypotheses_for_forms` with the optimized Option B per-hypothesis filter intersection path.
2. Remove `derive_hypotheses_option_a` and any Option A specific helpers or dead code.
3. Keep and streamline `build_hypothesis_filter_fsa` as the single hypothesis filter builder function.
4. Update `tests/test_hypothesis_filter_lattice.py` and `parse_chr_dict/benchmark_hypothesis_filter.py` to test the default pipeline and Option B cleanly without referencing Option A.
5. Run full test suite `pytest` to confirm 100% pass rate.
6. Check all ACs, DoDs, add final summary, and mark TASK-95 Done.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored derive_hypotheses_for_forms in parse_chr_dict/meta_label_compiler.py to use Option B (per-hypothesis filter intersection against surface parse lattice) as canonical default derivation path. Removed Option A union logic and experimental duplicate functions (derive_hypotheses_option_a and derive_hypotheses_option_b). Updated tests in tests/test_hypothesis_filter_lattice.py and benchmark script in parse_chr_dict/benchmark_hypothesis_filter.py. All 347 pytest tests pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
