---
id: TASK-121
title: Retire MetaConstraintCompiler and clean up test suite for 100% parity
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 18:27'
updated_date: '2026-09-04 18:56'
labels: []
dependencies:
  - TASK-120
priority: high
type: chore
ordinal: 131000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove MetaConstraintCompiler, MetaLabelDefinition, FeatureConstraint, MatchMode, and META_LABELS. Clean up or migrate tests in test_meta_label_compiler.py to test the new VerbForm and derivation pipeline. Confirm 100% unit and regression test suite passes cleanly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Delete or deprecate MetaConstraintCompiler, MetaLabelDefinition, FeatureConstraint, MatchMode, and META_LABELS
- [x] #2 Update test_meta_label_compiler.py and test_parse_chr_dict_baseline.py to test VerbForm and new derivation
- [x] #3 Ensure all unit tests in tests/ pass without errors
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Retired MetaConstraintCompiler, MetaLabelDefinition, FeatureConstraint, MatchMode, and META_LABELS with explicit DeprecationWarning shims and clean re-exports. Created parse_chr_dict/derive.py to house the pure derive_hypotheses_for_forms and derive_lexical_features_4step multi-form derivation logic directly using VerbForm, ParseData, VerbTemplate, VerbMetadata, and LexicalVerb. Updated tests/test_meta_label_compiler.py and tests/test_parse_chr_dict_baseline.py to test the new pure VerbForm / VerbEntryType / parse_surface / derive_hypotheses_for_forms pipeline, validating plural (entries 355, 598) and animate (entries 776, 788) verbs. Confirmed 100% of the unit and regression test suite (421/421 tests) passes cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
