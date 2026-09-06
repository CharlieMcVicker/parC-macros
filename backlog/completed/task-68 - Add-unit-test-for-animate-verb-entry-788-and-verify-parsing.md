---
id: TASK-68
title: Add unit test for animate verb entry 788 and verify parsing
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 21:45'
updated_date: '2026-08-23 21:46'
labels: []
dependencies: []
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create unit test for animate verb entry 788 ('he/she is catching him/her') in tests/test_meta_label_compiler.py and verify parsing & reconstruction.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add test_real_animate_verb_entry_788 in tests/test_meta_label_compiler.py
- [x] #2 Verify entry 788 parses cleanly and derives roots with OBJECT_ANIMACY=ANIMATE
- [x] #3 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read row 788 from chr-corpus/corpus.csv.
2. Create test_real_animate_verb_entry_788 in tests/test_meta_label_compiler.py.
3. Test derive_lexical_features_4step and reconstruct_row on entry 788.
4. Run pytest test suite to confirm 100% pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated and resolved animate verb entry 788 ('katv\'vska', 'tsiyatv\'vska') parsing failure. Created test_real_animate_verb_entry_788 in tests/test_meta_label_compiler.py reading corpus row 788. Diagnosed that filter_pronominals(pronoun_set='A') was strictly filtering for pronoun_set=='A', excluding transitive animate pronominals (1sg>3sg, 2sg>3sg). Updated filter_pronominals so that pronoun_set='A' includes transitive pronominals. All 20 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
