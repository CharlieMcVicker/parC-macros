---
id: TASK-135
title: Prune legacy uppercase H-alternation tags and shims
status: Done
assignee:
  - '@subagent-135'
created_date: '2026-09-06 18:02'
updated_date: '2026-09-08 12:49'
labels: []
dependencies: []
priority: medium
type: chore
ordinal: 145000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Prune obsolete uppercase H-alternation tags ([H_DROP], [H_GLOT], [H_LAT], [H_NONE], [H_VOWEL]) and legacy tag sets (LEGACY_H_ALT_TAGS) from parse_chr_dict and test fixtures, standardizing exclusively on key-value [H_alt=...] tags.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove LEGACY_H_ALT_TAGS and references from parse_chr_dict/h_alternation.py
- [x] #2 Remove legacy uppercase tag fallbacks from parse_chr_dict/parse.py
- [x] #3 Update unit tests in tests/test_derive_pipeline.py and test fixtures to remove legacy uppercase tags
- [x] #4 Consolidate NEW_H_ALT_TAGS and ALL_H_ALT_TAGS into a single canonical H_ALT_TAGS set
- [x] #5 Verify 100% pytest pass rate with zero regressions
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Pruned legacy uppercase H-alternation tags ([H_DROP], [H_GLOT], [H_LAT], [H_NONE], [H_VOWEL]) and legacy tag sets (LEGACY_H_ALT_TAGS, NEW_H_ALT_TAGS, ALL_H_ALT_TAGS) across parse_chr_dict, tests, and test fixtures. Consolidated H-alternation tags into a canonical H_ALT_TAGS set in parse_chr_dict/h_alternation.py. Removed legacy uppercase tag fallbacks and shims from parse_chr_dict/parse.py. Updated unit tests in tests/test_derive_pipeline.py and tests/test_lexical_verb_types.py as well as min-min test fixtures to use canonical key-value tags. Verified 100% pytest pass rate (129 passed) with zero regressions.
<!-- SECTION:FINAL_SUMMARY:END -->
