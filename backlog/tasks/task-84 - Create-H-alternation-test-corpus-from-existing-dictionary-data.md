---
id: TASK-84
title: Create H-alternation test corpus from existing dictionary data
status: Done
assignee:
  - '@myself'
created_date: '2026-08-24 16:02'
updated_date: '2026-08-24 16:03'
labels: []
dependencies: []
ordinal: 83000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extract verbs with distinct /h/ grade and glottal grade forms from the existing Cherokee corpus and reconstructed roots to build a dedicated test corpus for the revised H-alternation system.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify all entries in existing corpus/roots data where /h/ grade differs from glottal grade
- [x] #2 Generate structured test corpus dataset (CSV/JSON/YAML) with surface forms, pronominals, h-grade, and glottal-grade roots
- [x] #3 Add test harness validating H-alternation compatibility across all test corpus entries
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect chr-corpus/corpus.csv and roots.csv to find all reconstructed verb entries that exhibit H-alternation where h_root != glottal_root.\n2. Extract the entries with their forms (infinitive, present, imperfective, perfective, etc.), surface strings, h-grade, and g-grade roots.\n3. Format the test corpus into a dedicated dataset file (e.g. tests/data/h_alternation_test_corpus.csv or tests/data/h_alt_corpus.json).\n4. Create tests in tests/test_h_alternation_corpus.py that test both the Python checker and FST port against this empirical Cherokee dataset.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Extracted 160 distinct Cherokee verbs from dictionary data (roots.csv / corpus.csv) exhibiting authentic /h/ grade and glottal grade alternations across 4 phonological categories (drop_h: 52, syncopation_restoration: 74, h_to_glottal: 28, lateral_deaffrication: 6). Generated tests/data/h_alternation_test_corpus.csv and tests/data/h_alternation_test_corpus.json using parse_chr_dict/build_h_alt_test_corpus.py. Implemented comprehensive test suite in tests/test_h_alternation_corpus.py validating both the Python consistency checker and the FST transducer port across all 160 real verb entries and negative control pairs. All 262 test cases pass.
<!-- SECTION:FINAL_SUMMARY:END -->
