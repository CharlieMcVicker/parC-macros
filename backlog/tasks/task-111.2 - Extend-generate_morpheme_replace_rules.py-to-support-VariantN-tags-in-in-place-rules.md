---
id: TASK-111.2
title: >-
  Extend generate_morpheme_replace_rules.py to support [Variant=N] tags in
  in-place rules
status: Done
assignee:
  - '@agent'
created_date: '2026-09-03 16:30'
updated_date: '2026-09-03 16:41'
labels: []
dependencies:
  - TASK-111.1
parent_task_id: TASK-111
priority: high
type: task
ordinal: 118000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update generate_morpheme_replace_rules.py to recognize variant specifications in CSV rows/columns and emit [AspectClass=Class][Variant=N][Aspect=Feature] -> surface string_map rules alongside default [AspectClass=Class][Aspect=Feature] rules.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Support variant annotations or multi-row variant definitions in morpheme_replace CSVs
- [x] #2 Emit string_map entries [AspectClass=Class][Variant=N][Aspect=Feature] for N>=2
- [x] #3 Emit string_map entries [AspectClass=Class][Aspect=Feature] for default variant 1 and non-varying features
- [x] #4 Preserve 2-tag rules for non-varying features and prefix/tense classes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect generate_morpheme_replace_rules.py in-place rule generation logic\n2. Update _generate_inplace_rules to split cell values on ';' and generate [AspectClass=Class][Variant=idx][Aspect=Feature] for idx >= 2, and default 2-tag for idx == 1\n3. Preserve 2-tag rules for non-varying features and other classes\n4. Add unit test in tests/test_inplace_markers_generation.py to verify rule generation with variants
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Extended _generate_inplace_rules in parc_macros/generate_morpheme_replace_rules.py to support semicolon-delimited variant specifications in morpheme replace CSVs. For cells containing ';', values are split into variants: default variant 1 emits clean 2-tag [AspectClass=Class][Aspect=Feature] rules, while variant N >= 2 emits 3-tag [AspectClass=Class][Variant=N][Aspect=Feature] rules. Non-varying classes and features (such as prefix_class and tense_class) remain clean 2-tag rules. Added unit test test_inplace_aspect_variants_generation_task_111_2 in tests/test_inplace_markers_generation.py verifying variant and non-variant rule generation.
<!-- SECTION:FINAL_SUMMARY:END -->
