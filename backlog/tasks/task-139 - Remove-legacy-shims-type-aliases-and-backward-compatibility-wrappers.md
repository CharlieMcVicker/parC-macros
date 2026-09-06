---
id: TASK-139
title: 'Remove legacy shims, type aliases, and backward-compatibility wrappers'
status: To Do
assignee: []
created_date: '2026-09-06 18:07'
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
- [ ] #1 Remove legacy type aliases DerivationHypothesis, LexicalVerbHypothesis, LexicalVerbEntry, and InPlaceParseConfig from parse_chr_dict/types.py and update callers/tests to use LexicalVerb and ParseData directly
- [ ] #2 Remove derive_lexical_features_4step and LexicalVerb.lexical_tuple(), updating tests/test_derive_pipeline.py to use derive_hypotheses_for_forms
- [ ] #3 Remove canonical_root property from ParseData and update test_lexical_verb_types.py
- [ ] #4 Remove unused compiler and lexical_features arguments and hasattr(..., 'to_verb_form') checks from derive.py, reconstruct.py, and near_misses.py
- [ ] #5 Verify full pytest suite passes cleanly with zero warnings
<!-- AC:END -->
