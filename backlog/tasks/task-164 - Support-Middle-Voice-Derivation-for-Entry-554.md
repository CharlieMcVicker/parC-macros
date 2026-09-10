---
id: TASK-164
title: Support Middle Voice Derivation for Entry 554
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 15:49'
updated_date: '2026-09-10 15:49'
labels: []
dependencies: []
ordinal: 174000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix stage ordering to expand voice before h_alternation and update derivation hypothesis pruning to support middle voice [VoiceInfix=ali]nho on entry 554 (he/she is conversing).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Reorder expand_voice before h_alternation in chr-config/verb.yaml
- [x] #2 Update LexicalVerb.build_tag_str and derive.py to account for h_alt dropping target h when expecting h_metathesis
- [x] #3 Verify entry 554 derives [VoiceInfix=ali]nho with aspect_class apl-active-h and reconstructs all 6 forms
- [x] #4 Add test_middle_voice_entry_554_conversing to tests/test_derive_pipeline.py and pass all tests
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reordered expand_voice before h_alternation in chr-config/verb.yaml and regenerated chr-generated/ assets so H-alternation can see through expanded voice infixes (e.g. H-drop in tekalinoheha). Updated LexicalVerb.build_tag_str and derive.py candidate validation so active metathesis is not expected on forms undergoing mutating H-alternation. Verified that corpus entry 554 ('he/she is conversing') derives middle voice hypothesis [VoiceInfix=ali]nho (a_stem, apl-active-h, is_h_metathesis=True, h_alt_tag=[H_alt=drop]) and reconstructs all 6 forms. Added unit test test_middle_voice_entry_554_conversing in tests/test_derive_pipeline.py; all 147 tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
