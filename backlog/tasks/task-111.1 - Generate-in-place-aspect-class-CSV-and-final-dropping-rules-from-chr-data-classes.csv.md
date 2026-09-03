---
id: TASK-111.1
title: >-
  Generate in-place aspect class CSV and final-dropping rules from
  chr-data/classes.csv
status: Done
assignee:
  - '@agent'
created_date: '2026-09-03 16:30'
updated_date: '2026-09-03 16:38'
labels: []
dependencies: []
parent_task_id: TASK-111
priority: high
type: task
ordinal: 117000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a generator script to parse chr-data/classes.csv directly. Emits unified hyphenated aspect class names (sk-s-a, hvsk-nh, become, etc.), preserves multi-variant options per aspect cell, and outputs clean aspect suffix and final-dropping configuration tables without Cartesian class explosion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Read chr-data/classes.csv and generate clean hyphenated class identifiers without bracketed suffixes
- [x] #2 Extract aspect variations and represent variant 1 as default and variant N (N>=2) with variant metadata
- [x] #3 Generate final-dropping triggers correctly mapped to base class and variant indices
- [x] #4 Output to chr-inplace-config/verb-aspect.csv (and drop-final CSVs) formatted for in-place rule generation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect chr-data/classes.csv structure and subclasses\n2. Implement generator script to transform classes.csv into chr-inplace-config/verb-aspect.csv with semicolon-separated variants\n3. Respell consonants and strip * / @ prefixes from suffixes\n4. Map * and @ final dropping triggers to in-place tags and verify drop_root_final triggers\n5. Test and verify generated CSV
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented direct parsing of chr-data/classes.csv in parse_chr_dict/create_aspect_class_csv.py. Generated chr-inplace-config/verb-aspect.csv with 55 unified base aspect classes without Cartesian bracketed suffixes, preserving semicolon-separated variants and respelling consonants. Extracted and mapped final-dropping triggers (* for drop_final, @ for drop_final_two) with Variant=N indices for variant > 1 and default variant 1 unmarked. Produced drop-final CSV tables and added test suite in tests/test_aspect_class_csv.py.
<!-- SECTION:FINAL_SUMMARY:END -->
