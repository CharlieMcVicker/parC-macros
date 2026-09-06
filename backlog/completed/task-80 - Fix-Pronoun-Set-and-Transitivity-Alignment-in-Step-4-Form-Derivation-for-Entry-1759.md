---
id: TASK-80
title: >-
  Fix Pronoun Set and Transitivity Alignment in Step 4 Form Derivation for Entry
  1759
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-24 14:29'
updated_date: '2026-08-24 14:31'
labels: []
dependencies: []
ordinal: 79000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When deriving and narrowing hypotheses across a row in derive_hypotheses_for_forms, transitive forms with animate objects (such as 1sg>3sg in Entry 1759 'uthvtasti') need to align properly with candidate hypotheses having set_a=False or transitive pronoun sets.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Transitive pronominals (e.g. 1sg>3sg) with animate_objects=True correctly match during form-by-form derivation when hyp.set_a is False
- [x] #2 Entry 1759 ('he/she is listening to him/her') parses and derives valid hypotheses
- [x] #3 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect derive_hypotheses_for_forms in parse_chr_dict/meta_label_compiler.py to see how set_a and transitive pronominals are checked during step 2 pruning.
2. Ensure transitive parses (1sg>3sg, 2sg>3sg) correctly match hypotheses that have animate_objects=True even if set_a is False, or adjust set_a filtering for transitive pronominals.
3. Write/update unit test in tests/test_meta_label_compiler.py for entry 1759 ('uthvtasti', 'he/she is listening to him/her').
4. Verify tests pass and check entry 1759 parsing and validation.
5. Re-run parse pipeline or tests to ensure no regressions.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed pronoun set pruning in `derive_hypotheses_for_forms` in `parse_chr_dict/meta_label_compiler.py` so transitive pronominals (e.g. `1sg>3sg` on `tsiyathvtasti`) are not discarded when `hyp.set_a` is False. Added unit test `test_entry_1759_derivation_and_validation` in `tests/test_meta_label_compiler.py` confirming Entry 1759 derives and validates correctly under `StativeFutProg`.
<!-- SECTION:FINAL_SUMMARY:END -->
