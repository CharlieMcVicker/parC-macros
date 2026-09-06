---
id: TASK-67
title: Unify MetaLabelDerivation object across parsing and reconstruction
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 21:44'
updated_date: '2026-08-23 21:45'
labels: []
dependencies: []
ordinal: 66000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create MetaLabelDerivation state object tracking active meta labels ([PRONOUN_SET=...], [PLURAL=...], [OBJECT_ANIMACY=...]) during 4-step derivation and reuse directly during reconstruction.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add [OBJECT_ANIMACY=ANIMATE] and [OBJECT_ANIMACY=INANIMATE] meta labels
- [x] #2 Create MetaLabelDerivation state object tracking meta-label candidates across forms
- [x] #3 Unify reconstruct_row to use MetaLabelDerivation directly instead of separate iteration logic
- [x] #4 All unit tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add [OBJECT_ANIMACY=ANIMATE] and [OBJECT_ANIMACY=INANIMATE] definitions to META_LABELS in parse_chr_dict/meta_label_compiler.py.
2. Create MetaLabelDerivation dataclass (root, lexical_features, meta_labels, set_a, plural, animate_objects).
3. Update derive_lexical_features_4step to return derived MetaLabelDerivation state objects containing all inferred meta-labels.
4. Refactor parse_chr_dict/reconstruct.py and parse_chr_dict/__main__.py to validate forward inflection using the derived MetaLabelDerivation objects directly.
5. Run unit tests and verify 100% pass rate.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added [OBJECT_ANIMACY=ANIMATE] and [OBJECT_ANIMACY=INANIMATE] meta labels in parse_chr_dict/meta_label_compiler.py. Updated derive_lexical_features_4step and MetaLabelCombination in reconstruct.py to propagate and track object animacy meta-labels directly across parsing and reconstruction steps. All 19 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
