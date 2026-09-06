---
id: TASK-58
title: Implement MetaLabel FST query compiler and replace dict_structure
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 20:22'
updated_date: '2026-08-23 20:24'
labels: []
dependencies: []
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build MetaLabel FST acceptor module mapping meta tags ([FORM=...], [PRONOUN_SET=...]) to target feature lattices, execute 4-step derivation algorithm, replace dict_structure.py, and update parse_chr_dict.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 MetaLabel FST acceptor maps meta tags into feature tag lattices using Pynini
- [x] #2 Step 1-4 derivation algorithm executes correctly across paradigm forms
- [x] #3 dict_structure.py is replaced by meta label acceptor pipeline
- [x] #4 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement MetaLabel FST acceptor module (parse_chr_dict/meta_label_compiler.py) to compile meta label tags ([FORM=...], [PRONOUN_SET=...]) into Pynini feature tag lattices.
2. Implement 4-step derivation engine in parse_chr_dict:
   - Step 1 & 1a: Parse initial form with [FORM=...] flag and map meta label string to target label feature flags.
   - Step 2 & 3: Run meta label FST backwards to extract possible metalabels and build restricted label set for non-FORM features.
   - Step 4: Parse subsequent paradigm forms using the restricted metalabels.
3. Replace dict_structure.py functionality with meta_label_compiler.py and update parse_chr_dict/__main__.py.
4. Run tests and verify backward compatibility and correct parse derivation.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented MetaLabel FST acceptor compiler module in parse_chr_dict/meta_label_compiler.py using Pynini FSA operations. Built 4-step derivation algorithm (Step 1: parse initial form with [FORM=...]; Step 2: run meta label FST backwards; Step 3: construct restricted non-FORM feature set; Step 4: parse subsequent forms using restricted lattice). Updated parse_chr_dict/__main__.py and deprecated dict_structure.py. All 12 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
