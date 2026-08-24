---
id: TASK-87
title: 'Implement external [H_ALT] validation with trigger prefixes in parse_chr_dict'
status: Done
assignee:
  - '@subagent'
created_date: '2026-08-24 16:06'
updated_date: '2026-08-24 16:13'
labels: []
dependencies: []
ordinal: 86000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Validate outside of the FST that [H_ALT] is present only on H-alternating trigger prefixes (1sg>3sg, 2sg>3sg, 1sg.A) in derive_hypotheses_for_forms and reconstruct.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement external validation in parse_chr_dict to ensure [H_ALT] co-occurs strictly with trigger pronominals
- [x] #2 Update derive_hypotheses_for_forms and reconstruct_row to enforce [H_ALT] trigger validation
- [x] #3 Verify with unit tests in tests/test_meta_label_compiler.py
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review existing H-alternation logic, meta_label_compiler, reconstruct.py, and test files.
2. Implement external validation helper function/logic for [H_ALT] trigger prefixes (1sg>3sg, 2sg>3sg, 1sg.A).
3. Integrate external validation into derive_hypotheses_for_forms, reconstruct_row / validate_hypothesis.
4. Run tests and add test cases for [H_ALT] trigger validation.
5. Update task DoD, check acceptance criteria, add final summary, mark Done.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented external [H_ALT] validation to ensure H-alternation phonological rule application is strictly validated outside of the FST to co-occur only on H-alternating trigger prefixes (1sg>3sg, 2sg>3sg, 1sg.A). Added validate_h_alternation_trigger helper in parse_chr_dict/h_alternation.py, ensured integration across derive_hypotheses_for_forms in parse_chr_dict/meta_label_compiler.py and validate_hypothesis / reconstruct_row in parse_chr_dict/reconstruct.py. Added comprehensive unit tests in tests/test_meta_label_compiler.py (test_h_alternation_trigger_external_validation) and confirmed all 319 dictionary and H-alternation tests pass without regressions.
<!-- SECTION:FINAL_SUMMARY:END -->
