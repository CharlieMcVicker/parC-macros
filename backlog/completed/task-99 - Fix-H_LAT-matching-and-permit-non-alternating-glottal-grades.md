---
id: TASK-99
title: Fix H_LAT matching and permit non-alternating glottal grades
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-29 18:37'
updated_date: '2026-08-29 18:40'
labels: []
dependencies: []
ordinal: 98000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure [H_LAT] is only accepted when the root contains 'lh', treating roots without required alternating consonants as non-alternating, and allow non-alternated glottal grades when trigger pronouns show no surface mutation effect.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Constrain [H_LAT] in determine_h_alt_glottal_root to roots containing 'lh', [H_DROP]/[H_GLOT] to roots containing 'h'
- [x] #2 Allow non-alternating glottal roots when alternation is unobserved or grades are identical
- [x] #3 Run pytest and verify dictionary parsing
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect roots.csv and determine_h_alt_glottal_root where H_LAT or other tags are applied.
2. In determine_h_alt_glottal_root, check specifically:
   - [H_LAT] is only valid if "lh" in stem
   - [H_DROP] and [H_GLOT] are only valid if "h" in stem
   - If not alternating (or if the trigger form does not alternate), fall back to clean_h without failing or overgenerating phantom mutation tags.
3. Check meta_label_compiler.py to ensure trigger pronouns that show no alternation are allowed to resolve to non-alternating glottal root (clean_h).
4. Run full pytest suite and full dictionary parse.
5. Check acceptance criteria and complete task.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Constrained [H_LAT] in determine_h_alt_glottal_root to roots strictly containing "lh", and [H_DROP]/[H_GLOT] to roots with initial "h" or alternating consonant clusters ("nh", "lh", "yh", "wh", "mh"). Roots without alternating consonants cleanly fall back to non-alternating glottal root (clean_h). All 346 tests pass with 100% success rate and roots.csv successfully regenerated with zero phantom H_LAT / H_ALT matches.
<!-- SECTION:FINAL_SUMMARY:END -->
