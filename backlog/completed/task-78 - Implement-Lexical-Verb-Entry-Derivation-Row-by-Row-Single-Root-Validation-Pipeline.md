---
id: TASK-78
title: >-
  Implement Lexical Verb Entry Derivation & Row-by-Row Single-Root Validation
  Pipeline
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-24 00:55'
updated_date: '2026-08-24 01:01'
labels: []
dependencies: []
ordinal: 77000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Re-implement the dictionary parsing pipeline: parse form-by-form per hypothesis (starting from initial form, refining/branching hypotheses across subsequent forms), validate/reconstruct the complete row for each surviving hypothesis against the original surface forms, and write all valid derivations/hypotheses to roots.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create/refactor Lexical Verb Entry / Derivation hypothesis dataclass
- [x] #2 Implement hypothesis-driven multi-form parsing that evaluates and narrows hypotheses form-by-form
- [x] #3 Implement full-row reconstruction validation step for each hypothesis against surface forms
- [x] #4 Write all valid, fully-reconstructed derivations to roots.csv and non-reconstructing/failed rows to errors.csv
- [x] #5 Ensure all unit and dictionary regression tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect and design the Derivation / Lexical Verb Entry hypothesis model in meta_label_compiler.py / reconstruct.py.
2. Implement the form-by-form hypothesis parser: start with initial form meta-labels, spawn candidate hypotheses, and sequentially parse each subsequent form restricted by each hypothesis.
3. Implement full row reconstruction validation: for each surviving hypothesis, regenerate all row forms and assert exact match with surface forms.
4. Update __main__.py to run the derivation pipeline and write all valid verified hypotheses to roots.csv.
5. Run test suite and verify dictionary parsing on corpus.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented Lexical Verb Entry Derivation & Row-by-Row Single-Root Validation Pipeline:
- Created DerivationHypothesis (with aliases LexicalVerbHypothesis and LexicalVerbEntry) representing candidate lexical verb entries with morphological root, inflection classes, and meta-label traits.
- Implemented derive_hypotheses_for_forms which parses the initial form to spawn concrete candidate hypotheses and narrows/prunes candidate hypotheses form-by-form using aggregated dynamic constraints and lattice composition.
- Implemented full-row reconstruction validation (validate_hypothesis in reconstruct.py) that validates all surviving candidate hypotheses against all non-empty forms in the row using forward inflection.
- Updated parse_chr_dict/__main__.py to execute the derivation and validation pipeline row-by-row, writing all verified derivations to roots.csv and non-reconstructing rows to errors.csv.
- Updated and added comprehensive unit and regression tests in test_meta_label_compiler.py and test_parse_chr_dict_baseline.py; all 25 tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
