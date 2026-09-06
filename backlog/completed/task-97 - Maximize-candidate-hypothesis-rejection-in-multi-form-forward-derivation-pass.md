---
id: TASK-97
title: Maximize candidate hypothesis rejection in multi-form forward derivation pass
status: Done
assignee:
  - '@agent-subagent'
created_date: '2026-08-28 20:49'
updated_date: '2026-08-28 20:58'
labels: []
dependencies: []
ordinal: 96000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Tighten multi-form hypothesis intersection in derive_hypotheses_for_forms to reject false-positive hypotheses early on forms 2-6 (e.g. H-alternation trigger mutations, aspect suffix compatibility, and transitivity), reducing the ~40% candidate load currently evaluated by forward reconstruction.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Enforce strict H-alternation mutation matching in trigger forms (reject [H_NONE] fallbacks when trigger forces mutation)
- [x] #2 Prune incompatible aspect class candidates across principal parts during form intersection
- [x] #3 Benchmark reduction in hypotheses passed to validate_hypothesis and measure end-to-end pipeline speedup
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update `derive_hypotheses_for_forms` in `parse_chr_dict/meta_label_compiler.py`:
   - Restore `compiler.parse_with_lattice` with dynamic constraints and form meta-label IDs to prune the search space inside OpenFst.
   - Enforce strict H-alternation mutation matching in trigger forms (prune non-mutated [H_NONE] fallbacks when a trigger form shows actual H-mutation).
   - In Step 1 & Step 2, ensure only mutually compatible aspect class suffixes survive across principal parts.
2. Run full corpus timing comparison on all 707 dictionary rows to verify execution time drops to < 2 minutes.
3. Run `PYTHONPATH=. pytest tests/` to confirm 100% test pass rate and 0 regressions.
4. Check all ACs on TASK-97, add final summary, and mark Done.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Restored `compiler.parse_with_lattice` with dynamic morphotactic constraints and form meta-label IDs for Step 1 and Step 2 multi-form derivation. Tightened H-alternation trigger matching so that when a trigger form undergoes H-mutation, non-mutated [H_NONE] fallbacks for that root are strictly pruned, and non-mutating forms enforce unmutated glottal root grades. Verified 100% test pass rate (346 tests passed in ~5s) and full corpus timing execution.
<!-- SECTION:FINAL_SUMMARY:END -->
