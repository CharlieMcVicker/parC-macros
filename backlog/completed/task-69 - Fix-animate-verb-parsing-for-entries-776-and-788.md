---
id: TASK-69
title: Fix animate verb parsing for entries 776 and 788
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 21:57'
updated_date: '2026-08-23 21:58'
labels: []
dependencies: []
ordinal: 68000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Revert narrow fix for entry 788 and apply comprehensive fix for both entry 776 ('he/she is dropping him/her') and entry 788.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add test_real_animate_verb_entry_776 in tests/test_meta_label_compiler.py
- [x] #2 Apply comprehensive fix so both entry 776 and 788 parse cleanly and derive roots
- [x] #3 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read row 776 from chr-corpus/corpus.csv.
2. Add test_real_animate_verb_entry_776 to tests/test_meta_label_compiler.py alongside entry 788.
3. Investigate open parse graph and meta-label outputs for entry 776 and entry 788.
4. Apply comprehensive fix to meta_label_compiler.py handling 3rd person animate/transitive pronominal forms.
5. Run pytest test suite to confirm 100% pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated and resolved animate verb parsing for entries 776 ('katonhtiha', 'tsiyatonhtiha', 'hiyatonhta') and 788 ('katv\'vska', 'tsiyatv\'vska'). Added test_real_animate_verb_entry_776 in tests/test_meta_label_compiler.py alongside entry 788. Diagnosed that k_a_stem verbs (which use ka- in present forms and u-/a-stem in Set B completive/infinitive forms) were failing cross-form derivation due to strict prefix_class equality filtering. Added prefix_class compatibility between k_a_stem and a_stem in derive_lexical_features_4step dynamic constraint compilation. All 21 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
