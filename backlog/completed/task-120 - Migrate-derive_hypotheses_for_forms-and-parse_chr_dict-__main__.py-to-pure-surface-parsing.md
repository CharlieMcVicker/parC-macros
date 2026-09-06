---
id: TASK-120
title: >-
  Migrate derive_hypotheses_for_forms and parse_chr_dict/__main__.py to pure
  surface parsing
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 18:27'
updated_date: '2026-09-04 18:50'
labels: []
dependencies:
  - TASK-119
priority: high
type: feature
ordinal: 130000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor derive_hypotheses_for_forms to take forms: list[tuple[str, VerbForm]], replace compiler.parse_with_lattice with direct parse_surface calls, filter ParseData via VerbForm.matches and pure Python candidate pruning, and update parse_chr_dict/__main__.py to remove MetaConstraintCompiler.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Refactor derive_hypotheses_for_forms to use parse_surface and VerbForm without MetaConstraintCompiler
- [x] #2 Enforce all candidate pruning in pure Python: prefix_compat, present variant equality, plurality, animacy, base root equality, and H-alternation
- [x] #3 Update parse_chr_dict/__main__.py and near_misses.py to use the new VerbForm and derivation pipeline
- [x] #4 Verify parse_chr_dict runs and generates identical roots.csv and errors.csv
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect parse_chr_dict/meta_label_compiler.py, __main__.py, parse.py, and near_misses.py
2. Refactor derive_hypotheses_for_forms to pure surface parsing using parse_surface and VerbForm
3. Update parse_chr_dict/__main__.py and near_misses.py to remove MetaConstraintCompiler
4. Run tests and verify dictionary parsing results
5. Complete task
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Migrated derive_hypotheses_for_forms, parse_chr_dict/__main__.py, and near_misses.py to pure surface parsing and VerbForm:
- Implemented memoized parse_surface and parse_string_to_parse_data in parse_chr_dict/parse.py with singleton parse graph caching.
- Refactored derive_hypotheses_for_forms to accept VerbForm as primary (supporting FormParsingSpec and legacy strings gracefully) and perform pure bare-surface FST parsing without MetaConstraintCompiler.
- Implemented full candidate hypothesis generation and pruning in pure Python: prefix compatibility, present-tense variant consistency, plurality, animacy, base root equality, and H-alternation trigger validation.
- Updated parse_chr_dict/__main__.py and parse_chr_dict/near_misses.py to use PRIMARY_VERB_ENTRY_TYPES and removed MetaConstraintCompiler along with dead helper functions.
- Verified 100% derivation parity: diff -u on full dictionary corpus execution showed identical roots.csv and errors.csv, and all 422 test suite tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
