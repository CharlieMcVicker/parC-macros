---
id: TASK-162
title: >-
  Support H-alternation phonological syncretism in forward inflection and
  multi-form derivation
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 14:49'
updated_date: '2026-09-10 14:51'
labels: []
dependencies: []
ordinal: 172000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable inflect_form to realize surface forms when an alternating verb inflects with non-alternating morphology (like -hs-) without polluting FST reverse parsing or creating spurious hypotheses
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Revert delete_h_none in h_alternation.yaml to only match [H_alt=none]
- [x] #2 Update LexicalVerb.inflect_form to support non-alternating surface realization fallback
- [x] #3 Ensure multi-form derivation accurately accepts entry 1516 as StativeFutProg with [H_alt=glot]
- [x] #4 Verify all unit tests pass with zero reverse parsing overgeneration
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Kept FST phonology strictly deterministic and unpolluted (HTarget only matches prevocalic h<V> and sonorants, delete_h_none only matches [H_alt=none]). Updated inflect_tag_str to reject incomplete transductions with unexpanded morpheme tags, and enabled LexicalVerb.inflect_form to fallback to unmutated [H_alt=none] realization when a specific inflected form lacks an alternating environment (such as -hs- in hikeyuhsehsti). Verified entry 1516 is derived as StativeFutProg with [H_alt=glot], all 144 unit tests pass, and total corpus hypotheses remain minimal (1156) with zero reverse-parsing overgeneration.
<!-- SECTION:FINAL_SUMMARY:END -->
