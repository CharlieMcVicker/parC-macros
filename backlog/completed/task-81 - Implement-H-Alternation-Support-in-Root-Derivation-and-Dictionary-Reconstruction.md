---
id: TASK-81
title: >-
  Implement H Alternation Support in Root Derivation and Dictionary
  Reconstruction
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-24 14:57'
updated_date: '2026-08-24 15:14'
labels: []
dependencies: []
ordinal: 80000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Support Cherokee H-alternation across dictionary parsing, derivation hypothesis tracking, and forward reconstruction. Create h_alternation phonology compatibility module, restrict triggers to 1sg>3sg, 2sg>3sg, and 1sg.A, delete hallucinated E.A/E.B pronominals, track h_root and optional glottal_root in DerivationHypothesis, update validate_hypothesis and reconstruct.py, and verify with tests and full parse_chr_dict run.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement parse_chr_dict/h_alternation.py with grades_are_compatible and is_h_alternation_trigger
- [x] #2 Remove E.A and E.B from ALL_PRONOMINALS in meta_label_compiler.py
- [x] #3 Update DerivationHypothesis to store h_root (str) and glottal_root (Optional[str]) and update all call sites
- [x] #4 Update derive_hypotheses_for_forms to support H-alternating root consistency checking
- [x] #5 Update reconstruct.py to forward-inflect with glottal_root on trigger pronominals and h_root otherwise
- [x] #6 Update roots.csv header and parse_chr_dict/__main__.py
- [x] #7 Pass all automated unit tests and show increased matched rows / decreased errors in parse_chr_dict
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create parse_chr_dict/h_alternation.py with phonological helpers and trigger predicates.\n2. Remove hallucinated E.A/E.B from meta_label_compiler.py.\n3. Update DerivationHypothesis struct to hold h_root (str) and glottal_root (Optional[str]) and update all call sites.\n4. Update derive_hypotheses_for_forms to handle root alternation compatibility.\n5. Update reconstruct.py validate logic and reconstruct_row.\n6. Update parse_chr_dict/__main__.py for CSV serialization.\n7. Create unit tests in tests/test_h_alternation.py and update existing tests.\n8. Run parse_chr_dict and verify errors.csv strictly decreases and roots.csv increases.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented Cherokee H-alternation support across root derivation, dictionary parsing, and forward reconstruction. Created parse_chr_dict/h_alternation.py with grades_are_compatible and is_h_alternation_trigger (strictly for 1sg>3sg, 2sg>3sg, and 1sg.A). Removed hallucinated E.A/E.B pronominals. Updated DerivationHypothesis to store non-optional h_root (str) and optional glottal_root (Optional[str]) and updated all call sites. Updated derive_hypotheses_for_forms to track and check root grade compatibility across forms. Updated reconstruct.py to inflect using glottal_root on trigger pronominals and h_root otherwise. Created unit tests in tests/test_h_alternation.py and verified all 46 test cases pass. Ran full dictionary parsing on chr-corpus/corpus.csv: matched rows increased from 704 to 903 (+199 valid reconstructed roots), and errors strictly decreased from 364 down to 217 (-147 error rows).
<!-- SECTION:FINAL_SUMMARY:END -->
