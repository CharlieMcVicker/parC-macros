---
id: TASK-111
title: >-
  Refactor In-Place Aspect Classes to Unified Base Classes with [Variant=N]
  Morpheme Tags
status: Done
assignee: []
created_date: '2026-09-03 16:30'
updated_date: '2026-09-03 18:13'
labels: []
dependencies: []
priority: high
type: enhancement
ordinal: 116000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Migrate aspect class representation in chr-inplace-config from Cartesian expanded bracketed classes (e.g. [AspectClass=become[inf2]]) to unified base aspect classes (e.g. [AspectClass=become]) accompanied by local [Variant=N] tags on varying aspect forms. This eliminates overgeneration on non-varying aspects (e.g. present) and removes nested bracket syntax.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Base aspect classes generated from chr-data/classes.csv without bracketed variant suffixes
- [x] #2 [Variant=N] tags emitted only on varying aspect forms (with N>=2, default variant 1 unmarked)
- [x] #3 chr-inplace-config templates and patterns updated to support optional <Variant> slot
- [x] #4 generate_morpheme_replace_rules.py emits [AspectClass=...][Variant=N][Aspect=...] string maps
- [x] #5 chr-inplace-generated compiles cleanly with zero FST errors or regressions
- [x] #6 parse_chr_dict extracts and processes [Variant=N] tags without cross-aspect overgeneration
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully refactored in-place aspect classes from Cartesian expanded bracketed classes to unified base classes with local [Variant=N] tags. Generated chr-inplace-config/verb-aspect.csv directly from chr-data/classes.csv with 55 clean base classes and semicolon-separated variants. Updated generate_morpheme_replace_rules.py, open_root_template, alphabet.yaml, phoneme_groups.yaml, drop_root_final.yaml, parse.py, and meta_label_compiler.py. Verified that non-varying aspect forms (e.g. present) have zero overgeneration, FSTs compile cleanly with zero errors, and all 46 unit and regression tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
