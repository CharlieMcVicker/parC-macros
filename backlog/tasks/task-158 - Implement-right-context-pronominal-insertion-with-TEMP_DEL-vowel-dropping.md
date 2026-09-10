---
id: TASK-158
title: Implement right-context pronominal insertion with TEMP_DEL vowel dropping
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 13:38'
updated_date: '2026-09-10 13:45'
labels: []
dependencies: []
ordinal: 168000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace prefix stem shape acceptor system with right-context pronominal insertion generated generically in parc_macros from prefix_class.csv, and implement the 3-step TEMP_DEL vowel dropping pattern.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 parc_macros generates right_context on pronominal replace rules based on prefix_class.csv
- [x] #2 Implement TEMP_DEL marking, pronominal insertion with right context, and context-free TEMP_DEL deletion
- [x] #3 Remove compile_prefix_stem_shape_acceptor from cascade domain pipeline
- [x] #4 Regenerate chr-generated assets and verify all tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update parc_macros/generate_morpheme_replace_rules.py to merge feature acceptor patterns as right_context for class-conditioned replace rules
2. Implement 3-step TEMP_DEL pattern for stem-initial vowel dropping in parc_macros/generate_phonology.py and chr-config/verb.yaml
3. Remove compile_prefix_stem_shape_acceptor from cascade domain pipeline in parse_chr_dict
4. Regenerate chr-generated assets and verify all unit tests and derivation pipelines pass
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the external prefix stem-shape acceptor with native right-context pronominal replacement rules generated generically in parc_macros from prefix_class.csv. Implemented the 3-step [TEMP] vowel dropping pattern (mark_stem_initial_vowel -> pronominal -> drop_stem_initial_vowel), removed compile_prefix_stem_shape_acceptor from cascade domain acceptors, and verified 100% test pass and derivation parity.
<!-- SECTION:FINAL_SUMMARY:END -->
