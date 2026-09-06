---
id: TASK-109
title: 'morphotactic filtering on [H_ALT] slot'
status: Done
assignee:
  - '@myself'
created_date: '2026-09-03 15:21'
updated_date: '2026-09-03 15:57'
labels: []
dependencies: []
ordinal: 114000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
1sg.A and 1sg>3sg, 2sg>3sg to be followed by alternating morpheme (possibly [H_NONE])
other pro cannot.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Standardize H-alternation tags to [H_alt=none], [H_alt=drop], [H_alt=glot], [H_alt=lat], [H_alt=vowel] across alphabet, phonology rules, parse logic, test suite, and roots data
- [x] #2 Update open_root_template in chr-inplace-config/verb.yaml to make <H_alt> a mandatory slot (<Pro><H_alt><Root>...)
- [x] #3 Refactor morphotactic licensing into modular CSVs (e.g. aspect_morphotactics.csv, dist_morphotactics.csv, pro_morphotactics.csv) and support '*' / 'elsewhere' fallback
- [x] #4 Define pro_morphotactics.csv specifying triggers (1sg.A, 1sg>3sg, 2sg>3sg) license [H_alt=none]|[H_alt=drop]|[H_alt=glot]|[H_alt=lat]|[H_alt=vowel], and elsewhere (*) licenses [H_alt=none]
- [x] #5 Update compile_morphotactic_acceptor to compile all modular morphotactic rule CSVs and verify all tests pass cleanly
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Refactor morphotactic CSVs in chr-inplace-config/feature_acceptors/ into modular single-trigger files (aspect_morphotactics.csv, dist_morphotactics.csv, pro_morphotactics.csv) with frontmatter declaring '# trigger_slot: <Slot>' and support for '*' elsewhere rows.
2. Extend compile_morphotactic_acceptor in parse_chr_dict/acceptors.py to read modular morphotactic CSVs, extract '# trigger_slot: <Slot>' from frontmatter, and expand '*' / elsewhere rules across unmentioned slot values.
3. Rename H-alternation tags to [H_alt=none], [H_alt=drop], [H_alt=glot], [H_alt=lat], [H_alt=vowel] across alphabet.yaml, phoneme_groups.yaml, h_alternation.yaml, parse_chr_dict/h_alternation.py, parse_chr_dict/parse.py, and parse_chr_dict/acceptors.py.
4. Update open_root_template in chr-inplace-config/verb.yaml to make <H_alt> mandatory (<Pro><H_alt><Root>...).
5. Update test files and roots.csv with standardized tag format and regenerate chr-inplace-generated config.
6. Verify full test suite passes.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Standardized H-alternation tags to [H_alt=none], [H_alt=drop], [H_alt=glot], [H_alt=lat], [H_alt=vowel] and made <H_alt> a mandatory slot in open_root_template. Refactored morphotactic licensing into modular CSV files (aspect_morphotactics.csv, dist_morphotactics.csv, pro_morphotactics.csv) with frontmatter '# trigger_slot: <Slot>' and '*' elsewhere fallback. Pronominal triggers (1sg.A, 1sg>3sg, 2sg>3sg) license all H_alt allomorphs, while elsewhere (*) restricts other pronominals strictly to [H_alt=none]. Preserved roots.csv via backup roots.csv.bak and created substituted copy roots_inplace.csv. All 392 tests in the test suite pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
