---
id: TASK-98
title: Refactor H-alternation resolution to rely purely on parC FST tags
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-29 18:06'
updated_date: '2026-08-29 18:10'
labels: []
dependencies: []
ordinal: 97000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update h_alternation.py to eliminate fallback calls to local FST phonology rules, relying strictly on parC H-alternation tags embedded in parsed roots, keeping h_alternation_fst.py intact until full validation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update determine_h_alt_glottal_root in h_alternation.py to check only whether glottal root differs by an H_ALT tag
- [x] #2 Remove reliance on local h_alternation_fst functions in determine_h_alt_glottal_root while preserving h_alternation_fst.py
- [x] #3 Run dictionary and meta_label_compiler regression tests to verify parC FST handling
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect determine_h_alt_glottal_root in parse_chr_dict/h_alternation.py.
2. Simplify determine_h_alt_glottal_root to verify strip_h_alt_tags(h_root) == strip_h_alt_tags(p_root) without calling parse_chr_dict.h_alternation_fst.
3. Return p_root (or clean_h) directly if valid, keeping h_alternation_fst.py intact for now as requested.
4. Run full test suite (pytest) to test for regressions against parC FST.
5. Check acceptance criteria, write final summary, and complete task.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored determine_h_alt_glottal_root in parse_chr_dict/h_alternation.py to rely purely on parC native H-alternation resolution and embedded [H_ALT] tags, eliminating local FST compositions (build_drop_first_h_fst, fst_grades_are_compatible, etc.) while keeping parse_chr_dict/h_alternation_fst.py intact. Verified 100% test pass rate across all 346 pytest tests and successful execution of the full dictionary parsing pipeline.
<!-- SECTION:FINAL_SUMMARY:END -->
