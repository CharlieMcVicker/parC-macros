---
id: TASK-62
title: >-
  Implement Pronominal struct and functional filter constraint helpers in
  MetaLabel system
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 20:45'
updated_date: '2026-08-23 20:46'
labels: []
dependencies: []
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create Pronominal dataclass with person, number, and set attributes, and implement helper filter functions for dynamic one_of pronominal constraints in MetaConstraintCompiler.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create Pronominal struct with person, number, set parsing and matching
- [x] #2 Add helper filter functions for pronominal matching (e.g. filter by set, number, person)
- [x] #3 Update META_LABELS definitions and reconstruct/parsing functions to use Pronominal helpers
- [x] #4 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Design Pronominal dataclass in parse_chr_dict/meta_label_compiler.py with person, number, set attributes and parse() / to_tag() methods.
2. Implement filter functions (filter_pronominals(person=..., number=..., pronoun_set=..., animate_object=...)).
3. Refactor META_LABELS definitions to use Pronominal filter helpers for one_of constraints.
4. Refactor reconstruct.py to use Pronominal struct and filter logic instead of string hacking.
5. Run unit tests and confirm 100% pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented Pronominal struct and filter_pronominals functional filter helpers in parse_chr_dict/meta_label_compiler.py. Added [PLURAL=TRUE] and [PLURAL=FALSE] meta labels. Updated META_LABELS definitions and reconstruct.py get_pronominal to use filter_pronominals. All 16 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
