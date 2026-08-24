---
id: TASK-82
title: Create Near-Misses CSV Diagnostic for Single-Form Parsing Failures
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-24 15:49'
updated_date: '2026-08-24 15:52'
labels: []
dependencies: []
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate a diagnostic CSV (near_misses.csv) identifying all error corpus rows where omitting exactly one form produces a valid derivation hypothesis that reconstructs the remaining N-1 forms. Include the failing form slot name, corpus surface form, generated surface form, and derived root/classes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement near misses analysis script or function in parse_chr_dict
- [x] #2 Generate near_misses.csv for all failing corpus entries
- [x] #3 Output summary statistics of failing slots (e.g. counts by infinitive, perfective, etc.)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented parse_chr_dict/near_misses.py to diagnose single-form validation failures across error verbs. Evaluated all 216 error entries across all N-1 subsets of non-empty forms and generated near_misses.csv containing 399 near-miss hypotheses across 123 unique verbs (57% of failing verbs). Computed breakdown by failed slot: present_1sg (168), perfective (130), infinitive (79), imperative (17), present (3), imperfective (2).
<!-- SECTION:FINAL_SUMMARY:END -->
