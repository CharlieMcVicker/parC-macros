---
id: TASK-119
title: >-
  Implement pure LexicalVerb forward inflection and validation, retiring
  MetaLabelCombination
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 18:27'
updated_date: '2026-09-04 18:38'
labels: []
dependencies:
  - TASK-118
priority: high
type: feature
ordinal: 129000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add inflect_form and validate_form directly to LexicalVerb using VerbForm and VerbMetadata.get_pronominal_candidates. Refactor validate_hypothesis in reconstruct.py to validate directly via LexicalVerb and retire MetaLabelCombination, ReconstructionSpec, to_meta_combination, get_dynamic_constraints, and get_meta_label_ids.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement LexicalVerb.inflect_form(form: VerbForm) and LexicalVerb.validate_form(form: VerbForm, reference_form: str)
- [x] #2 Refactor validate_hypothesis to validate all forms directly using LexicalVerb and VerbEntryType without MetaConstraintCompiler
- [x] #3 Remove MetaLabelCombination, ReconstructionSpec, ALL_META_COMBINATIONS, to_meta_combination, get_dynamic_constraints, and get_meta_label_ids
- [x] #4 Verify unit tests for forward inflection and hypothesis validation pass cleanly
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented pure LexicalVerb forward inflection and validation directly via LexicalVerb.inflect_form and LexicalVerb.validate_form in parse_chr_dict/types.py using VerbForm and VerbMetadata. Refactored validate_hypothesis in parse_chr_dict/reconstruct.py to accept VerbEntryType, EntryTypeSpec, and string entry type names, validating non-empty forms without MetaConstraintCompiler. Retired MetaLabelCombination, ReconstructionSpec, ALL_META_COMBINATIONS, to_meta_combination, get_dynamic_constraints, and get_meta_label_ids, replacing legacy row reconstruction logic with VerbMetadata.all_combinations. Updated tests/test_meta_label_compiler.py, tests/test_parse_chr_dict_baseline.py, tests/test_verb_form_types.py, and tests/test_lexical_verb_types.py to test LexicalVerb forward inflection and validation directly. All 422 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
