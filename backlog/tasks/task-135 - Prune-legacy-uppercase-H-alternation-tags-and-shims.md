---
id: TASK-135
title: Prune legacy uppercase H-alternation tags and shims
status: To Do
assignee: []
created_date: '2026-09-06 18:02'
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
- [ ] #1 Remove LEGACY_H_ALT_TAGS and references from parse_chr_dict/h_alternation.py
- [ ] #2 Remove legacy uppercase tag fallbacks from parse_chr_dict/parse.py
- [ ] #3 Update unit tests in tests/test_derive_pipeline.py and test fixtures to remove legacy uppercase tags
- [ ] #4 Consolidate NEW_H_ALT_TAGS and ALL_H_ALT_TAGS into a single canonical H_ALT_TAGS set
- [ ] #5 Verify 100% pytest pass rate with zero regressions
<!-- AC:END -->
