---
id: TASK-90
title: Update parse_chr_dict and reconstruct to use fine-grained H-alternation tags
status: Done
assignee:
  - '@subagent'
created_date: '2026-08-24 16:32'
updated_date: '2026-08-24 16:41'
labels: []
dependencies: []
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update derive_hypotheses_for_forms and reconstruct_row to parse and propagate fine-grained H-alternation tags, validate triggers, and forward inflect deterministically.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Extract fine-grained H-alternation tag during form parsing
- [x] #2 Update DerivationHypothesis to store h_alt_tag, h_root, and glottal_root
- [x] #3 Update reconstruct.py to inflect trigger forms using h_alt_tag with the FST
- [x] #4 Verify with unit tests in tests/test_meta_label_compiler.py
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect current h_alternation.py, meta_label_compiler.py, reconstruct.py, and tests\n2. Add H_ALT_TAGS and validate_h_alternation_trigger to h_alternation.py\n3. Update DerivationHypothesis and derivation logic in meta_label_compiler.py to handle fine-grained h_alt_tag\n4. Update reconstruct.py to incorporate h_alt_tag into forward inflection queries for trigger pronominals\n5. Update and run test suite\n6. Complete all ACs, DoD, final summary, and mark task Done
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated parse_chr_dict and reconstruct pipeline to support fine-grained H-alternation tags ([H_DROP], [H_GLOT], [H_LAT], [H_NONE]). Defined H_ALT_TAGS and enhanced validate_h_alternation_trigger in parse_chr_dict/h_alternation.py. Added fine-grained tag extraction helper and updated DerivationHypothesis and derive_hypotheses_for_forms in parse_chr_dict/meta_label_compiler.py to parse, store, validate, and propagate h_alt_tag across candidate rows. Updated reconstruct.py to incorporate h_alt_tag into forward inflection queries for trigger pronominals. Added comprehensive unit tests in tests/test_meta_label_compiler.py covering tag extraction, validation, dataclass serialization, and row reconstruction. All 344 test cases pass with 100% success rate.
<!-- SECTION:FINAL_SUMMARY:END -->
