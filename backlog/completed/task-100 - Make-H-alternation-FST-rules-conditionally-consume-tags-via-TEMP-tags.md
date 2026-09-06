---
id: TASK-100
title: Make H-alternation FST rules conditionally consume tags via TEMP tags
status: Done
assignee:
  - '@antigravity'
created_date: '2026-08-29 18:47'
updated_date: '2026-08-29 18:52'
labels: []
dependencies: []
ordinal: 99000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update h_alternation phonology rules in chr-config and min-min-config so that [H_DROP], [H_GLOT], and [H_LAT] are only converted to [TEMP] when their phonological mutation applies, and only [H_NONE] and [TEMP] are deleted, preventing vacuous mutation parses.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update h_alternation.yaml rules to consume mutation tags into [TEMP] upon mutation
- [x] #2 Update delete rules so only [TEMP] and [H_NONE] are deleted
- [x] #3 Regenerate grammar assets and verify parsing in parse_chr_dict and pytest
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect current h_alternation.yaml in chr-config and min-min-config and how parC compiles rules.
2. Formulate the conditional consumption of [H_DROP], [H_GLOT], [H_LAT] using [TEMP] / TempTags.
3. Update delete rules to delete [TEMP] and [H_NONE], while leaving unmutated [H_DROP], [H_GLOT], [H_LAT] unconsumed (so they fail compilation/alphabet checks).
4. Run parC generator/compiler to rebuild chr-generated/ and min-min-insertion-generated/.
5. Simplify determine_h_alt_glottal_root in parse_chr_dict/h_alternation.py to purely check strip_h_alt_tags without any hardcoded consonant sets.
6. Run full pytest suite and verify dictionary parsing.
7. Complete task acceptance criteria and summary.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated h_alternation.yaml rules in chr-config/ to conditionally mark [H_LAT], [H_DROP], and [H_GLOT] as [TEMP] only when their respective phonological mutation triggers fire. Updated cleanup rules to delete only [H_NONE] and [TEMP], preventing vacuous mutation tags from surviving on non-alternating roots. Regenerated chr-generated/ assets, simplified determine_h_alt_glottal_root in parse_chr_dict/h_alternation.py to eliminate hardcoded consonant heuristics, and verified 100% test pass rate across all 346 pytest tests and successful dictionary corpus parsing.
<!-- SECTION:FINAL_SUMMARY:END -->
