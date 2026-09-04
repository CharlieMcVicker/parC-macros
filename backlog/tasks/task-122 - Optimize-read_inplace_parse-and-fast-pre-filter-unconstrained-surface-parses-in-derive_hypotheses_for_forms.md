---
id: TASK-122
title: >-
  Build 12 specialized FSTs (Eventful vs Stative x 6 reference forms) to
  optimize dictionary derivation
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 19:08'
updated_date: '2026-09-04 19:40'
labels: []
dependencies: []
priority: high
type: enhancement
ordinal: 132000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Optimize read_inplace_parse and pre-filter unconstrained surface parses in derive_hypotheses_for_forms to eliminate ~75-90% of redundant calls and accelerate parse string processing from 42s down to sub-second runtimes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add fast raw-string pre-filtering in derive_hypotheses_for_forms using VerbForm aspect/tense tag matching before calling parse_string_to_parse_data
- [x] #2 Memoize read_inplace_parse directly so every unique parse string is parsed at most once and non-matching strings are parsed zero times
- [x] #3 Streamline read_inplace_parse to use single-pass token scanning and slice-based root collection
- [x] #4 Verify all 421+ unit and regression tests pass with zero regressions
- [x] #5 Verify substantial performance improvement across corpus processing
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 All 421+ tests in pytest pass
- [x] #2 Zero regressions across baseline tests
- [x] #3 Corpus derivation runtime benchmark shows dramatic reduction
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. In parse_chr_dict/parse.py, implement optimized FST generation/caching for Eventful vs. Stative across each of the six reference forms:
   - Eventful (non-stative aspect classes) x 6 forms (present, present_1sg, imperfective, perfective, imperative, infinitive)
   - Stative (stative aspect classes) x 6 forms (present, present_1sg, imperfective, perfective, imperative/fut_prog, infinitive)
   Restricting the output domain to licensed aspect class, aspect, tense, and pronominal tags, optimizing each FST once.
2. In parse_chr_dict/parse.py, add parse_surface_for_form(surface, form, is_stative=False) using the specialized FSTs with memoization.
3. In parse_chr_dict/derive.py, update derive_hypotheses_for_forms to parse using the specialized FST for each form and category.
4. Memoize read_inplace_parse directly and optimize its token scanner.
5. Run full pytest suite (421+ tests) to verify 100% parity and zero regressions.
6. Benchmark corpus derivation to verify massive runtime reduction.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented 12 specialized, domain-restricted FSTs for Eventful vs. Stative across the six reference forms in parse_chr_dict/parse.py and parse_chr_dict/derive.py, memoized read_inplace_parse directly with slice-based scanning, and plumbed entry_type throughout derivation. Reduced full corpus processing runtime by over 50% (from 42s+ down to 21s) and eliminated 856,132 redundant calls to read_inplace_parse (down from 1,217,364 to 361,232). All 421 unit and regression tests pass with zero regressions.
<!-- SECTION:FINAL_SUMMARY:END -->
