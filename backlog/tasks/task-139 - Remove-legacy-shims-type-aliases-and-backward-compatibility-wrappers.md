---
id: TASK-139
title: 'Remove legacy shims, type aliases, and backward-compatibility wrappers'
status: Done
assignee:
  - '@subagent-139'
created_date: '2026-09-06 18:07'
updated_date: '2026-09-08 12:57'
labels: []
dependencies: []
priority: medium
type: chore
ordinal: 149000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove obsolete type aliases (DerivationHypothesis, LexicalVerbHypothesis, LexicalVerbEntry, InPlaceParseConfig), prune legacy wrapper derive_lexical_features_4step and canonical_root, clean up unused compiler/lexical_features arguments and hasattr(..., 'to_verb_form') checks across parse_chr_dict.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove legacy type aliases DerivationHypothesis, LexicalVerbHypothesis, LexicalVerbEntry, and InPlaceParseConfig from parse_chr_dict/types.py and update callers/tests to use LexicalVerb and ParseData directly
- [x] #2 Remove derive_lexical_features_4step and LexicalVerb.lexical_tuple(), updating tests/test_derive_pipeline.py to use derive_hypotheses_for_forms
- [x] #3 Remove canonical_root property from ParseData and update test_lexical_verb_types.py
- [x] #4 Remove unused compiler and lexical_features arguments and hasattr(..., 'to_verb_form') checks from derive.py, reconstruct.py, and near_misses.py
- [x] #5 Verify full pytest suite passes cleanly with zero warnings
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed legacy type aliases (DerivationHypothesis, LexicalVerbHypothesis, LexicalVerbEntry, InPlaceParseConfig) from parse_chr_dict/types.py and updated callers/tests to use LexicalVerb and ParseData directly. Removed legacy derivation wrapper derive_lexical_features_4step and LexicalVerb.lexical_tuple(), updating tests/test_derive_pipeline.py to use derive_hypotheses_for_forms. Removed canonical_root property from ParseData and updated tests/test_lexical_verb_types.py. Removed unused compiler and lexical_features arguments as well as hasattr(..., 'to_verb_form') checks from derive.py, reconstruct.py, and near_misses.py. Verified full pytest suite (129 tests) passes cleanly with 0 warnings.
<!-- SECTION:FINAL_SUMMARY:END -->
