---
id: TASK-64
title: >-
  Implement Verb Pronoun Set and Plurality Meta-Label Propagation in 4-Step
  Derivation
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 20:55'
updated_date: '2026-08-23 20:56'
labels: []
dependencies: []
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update derive_lexical_features_4step to derive underlying verb pronoun set ([PRONOUN_SET=A/B]) and plurality ([PLURAL=TRUE/FALSE]) from parsing forms, propagating these meta-labels dynamically to restrict subsequent form parsing lattices.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Derive underlying verb pronoun set from forms with allows_set_a=True
- [x] #2 Propagate derived [PRONOUN_SET=...] and [PLURAL=...] meta-labels into subsequent form Pynini FSA tag acceptors
- [x] #3 Form-specific allows_set_a=False correctly overrides to Set B pronominals
- [x] #4 All unit tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update derive_lexical_features_4step in parse_chr_dict/meta_label_compiler.py:
   - Extract derived pronominal set (Set A vs Set B) and plurality (plural vs singular) from parses.
   - For subsequent forms, check FormParsingSpec.allows_set_a: if True and verb pronoun set is derived, include [PRONOUN_SET=A/B] in meta_label_ids for lattice compilation.
   - Include [PLURAL=TRUE/FALSE] in meta_label_ids if derived.
2. Update unit tests in tests/test_meta_label_compiler.py to verify pronoun set and plurality propagation.
3. Run pytest test suite to confirm 100% pass rate.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented underlying verb pronoun set ([PRONOUN_SET=A/B]) and plurality ([PLURAL=TRUE/FALSE]) derivation and dynamic meta-label propagation in derive_lexical_features_4step. When parsing subsequent forms, if allows_set_a=True, the derived verb [PRONOUN_SET=...] meta-label is passed directly into compile_restricted_tag_acceptor, while forms with allows_set_a=False correctly override to Set B pronominals. All 17 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
