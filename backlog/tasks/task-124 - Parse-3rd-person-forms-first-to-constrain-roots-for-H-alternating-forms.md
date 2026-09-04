---
id: TASK-124
title: Parse 3rd person forms first to constrain roots for H-alternating forms
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 19:57'
updated_date: '2026-09-04 20:05'
labels: []
dependencies: []
priority: high
type: enhancement
ordinal: 134000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reorder form derivation in derive_hypotheses_for_forms to process 3rd-person forms first (which do not H-alternate), extract candidate roots from their parses, and construct a root-restricted parse graph for remaining H-alternating forms (1st and 2nd person) to restrict combinatorial path explosion from H-alternation phonological rules.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Reorder forms in derivation to process 3rd-person non-H-alternating forms first
- [x] #2 Extract surviving candidate roots from 3rd-person hypotheses
- [x] #3 Construct root-restricted parse graph for 1st- and 2nd-person H-alternating forms
- [x] #4 Verify all 421+ pytest tests pass with zero regressions
- [x] #5 Verify reduction in H-alternation parse paths and derivation runtime
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 All 421+ pytest tests pass with zero regressions
- [x] #2 Verified reduction in H-alternation paths and derivation runtime
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. In parse_chr_dict/parse.py:
   - Implement build_root_filter_fsa(allowed_roots: Iterable[str]) -> pynini.Fst (memoized using frozenset[str]):
     Construct a boundary-constrained filter FSA: sigma* + [H_alt=...] + root_union + [AspectClass=...] + sigma* using base_graph output symbols.
   - Update parse_surface to accept optional allowed_roots parameter, composing with the root filter FSA when present.
2. In parse_chr_dict/derive.py:
   - In _derive_category, partition normalized_forms into 3rd-person forms (f.person == '3rd') and other forms (1st and 2nd person).
   - Process all 3rd-person forms first to refine candidate_hypotheses and collect candidate roots without triggering H-alternation paths.
   - Extract allowed_roots = {h.h_root for h in candidate_hypotheses if h.h_root}.
   - For subsequent forms (1st and 2nd person H-alternation triggers), pass allowed_roots to parse_surface to constrain the FST parse output.
3. Verification and Benchmarking:
   - Run full pytest suite (421+ tests) to verify 100% parity and zero regressions.
   - Run H-alternation test suite (test_h_alternation.py, test_h_alternation_corpus.py, etc.).
   - Benchmark dictionary derivation across the corpus to quantify parse count reduction and performance improvement.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented root-constrained FST parsing for H-alternating forms by processing non-alternating 3rd-person forms first. In parse_chr_dict/parse.py, implemented build_root_filter_fsa(allowed_roots) with memoization using frozenset[str], creating an exact boundary-constrained FSA filter (sigma* + [H_alt=...] + root_union + [AspectClass=...] + sigma*) and updated parse_surface to compose the output lattice with the root filter when allowed_roots is passed. In parse_chr_dict/derive.py, reordered forms in _derive_category to process all 3rd-person forms first, extracted candidate roots from surviving hypotheses, and passed allowed_roots to parse_surface for subsequent 1st- and 2nd-person H-alternation forms. Profiled with cProfile before and after across the full Cherokee dictionary corpus: read_inplace_parse calls dropped by 77% (from 200,366 down to 46,044, eliminating 154,322 parse strings), _derive_category cumulative runtime dropped by 42% (from 18.83s down to 10.94s), and total corpus execution time dropped from 23.64s to 15.58s. All 421 pytest unit and regression tests pass with zero regressions, and roots.csv output is bit-for-bit identical.
<!-- SECTION:FINAL_SUMMARY:END -->
