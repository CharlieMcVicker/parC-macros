---
id: TASK-96
title: Optimize dictionary parsing by using fast bare-surface linear FST parsing
status: Done
assignee:
  - '@agent-subagent'
created_date: '2026-08-28 20:27'
updated_date: '2026-08-28 20:34'
labels: []
dependencies: []
ordinal: 95000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace complex input query lattice tag-acceptor construction with fast linear bare-surface FST parsing in parse_chr_dict, performing feature and meta-label filtering in pure Python memory for a 2.2x speedup.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update parse_chr_dict and meta_label_compiler to parse bare surface forms
- [x] #2 Apply meta-label and feature constraints in Python post-parse filtering
- [x] #3 Verify 100% derivation parity and pass all pytest tests
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update `MetaConstraintCompiler.parse_with_lattice` or provide a specialized fast bare-surface parser `compiler.parse_surface(surface: str)`.
2. Update `derive_hypotheses_for_forms` in `parse_chr_dict/meta_label_compiler.py` to use bare surface linear parsing and perform meta-label matching (e.g. `[FORM=...]`, `[PRONOUN_SET=...]`, `[PLURAL=...]`, and dynamic feature constraints) directly in Python.
3. Update `parse_chr_dict/parse.py` or other dictionary pipeline callers to leverage bare-surface parsing where applicable.
4. Benchmark before & after end-to-end timing across corpus.
5. Verify 100% parity against baseline and pass all unit tests (`pytest`).
6. Update task ACs, DoD, final summary, and mark Done.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented fast bare-surface linear FST parsing in MetaConstraintCompiler.parse_surface and refactored derive_hypotheses_for_forms to parse bare surface forms and apply form specs, meta-labels, pronominal constraints, and H-alternation triggers in pure Python post-parse filtering. Verified 100% derivation parity across all corpus rows and entry types and passed 345/345 pytest tests.
<!-- SECTION:FINAL_SUMMARY:END -->
