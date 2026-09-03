---
id: TASK-111.5
title: 'Adapt parse_chr_dict to extract and process [Variant=N] tags'
status: Done
assignee:
  - '@agent'
created_date: '2026-09-03 16:30'
updated_date: '2026-09-03 18:12'
labels: []
dependencies:
  - TASK-111.4
parent_task_id: TASK-111
priority: high
type: task
ordinal: 121000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update parse_chr_dict modules (parse.py, meta_label_compiler.py, reconstruct.py) to extract [Variant=N] tags in InPlaceParseConfig, enforce present variant consistency between 1st and 3rd present, trust forms on their own variants for non-shared aspects, and verify regression tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update InPlaceParseConfig and read_inplace_parse to extract Variant tag
- [x] #2 Update derive_hypotheses_for_forms to enforce present variant match between 1st and 3rd present
- [x] #3 Allow independent variant selection on other aspects (imperfective, completive, immediate, infinitive)
- [x] #4 Verify all unit and regression tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. In parse_chr_dict/parse.py, add Variant to INPLACE_SLOT_TAG_MAP and add variant field to InPlaceParseConfig\n2. In read_inplace_parse, extract [Variant=N] into cfg.variant\n3. In meta_label_compiler.py, update DerivationHypothesis to track present_variant and enforce consistency between 1st and 3rd present\n4. In derive_hypotheses_for_forms, constrain subsequent non-shared forms by base aspect_class while allowing independent variants\n5. Run test suite to verify zero regressions
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated parse.py (INPLACE_SLOT_TAG_MAP, InPlaceParseConfig, read_inplace_parse, to_labels_dict) and meta_label_compiler.py (DerivationHypothesis, derive_hypotheses_for_forms) to support the [Variant=N] tag. Enforced present variant consistency across 1st and 3rd present while trusting non-shared aspect forms on their own variants. Verified 46 unit and regression tests pass with zero regressions.
<!-- SECTION:FINAL_SUMMARY:END -->
