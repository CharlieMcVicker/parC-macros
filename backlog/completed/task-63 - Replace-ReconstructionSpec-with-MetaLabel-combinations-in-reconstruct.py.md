---
id: TASK-63
title: Replace ReconstructionSpec with MetaLabel combinations in reconstruct.py
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 20:48'
updated_date: '2026-08-23 20:48'
labels: []
dependencies: []
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Eliminate ReconstructionSpec class and replace custom pronominal string generation in parse_chr_dict/reconstruct.py with MetaLabel combinations ([PRONOUN_SET=...], [PLURAL=...]).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove ReconstructionSpec class from reconstruct.py
- [x] #2 reconstruct_row uses MetaLabel combinations for forward inflection validation
- [x] #3 Update __main__.py roots CSV fields to output set_a, plural, animate_objects derived from meta labels
- [x] #4 All unit tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Replace ReconstructionSpec in parse_chr_dict/reconstruct.py with MetaLabelCombination dataclass (meta_labels, set_a, plural, animate_objects).
2. Update reconstruct_row to use MetaConstraintCompiler for forward inflection validation.
3. Update parse_chr_dict/__main__.py to fix root diff issue by running per-form 4-step derivation matching baseline logic.
4. Run unit tests and confirm 100% pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced ReconstructionSpec in parse_chr_dict/reconstruct.py with MetaLabelCombination using meta-label flags ([PRONOUN_SET=...], [PLURAL=...]). Refactored reconstruct_row to use MetaConstraintCompiler for forward inflection validation. Fixed form_parses derivation loop in parse_chr_dict/__main__.py matching baseline EntryType form intersection rules. All 16 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
