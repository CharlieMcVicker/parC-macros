---
id: TASK-148
title: >-
  Order tense stage before h_alternation to enable H-alternation in aspect
  suffixes
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-08 15:53'
updated_date: '2026-09-08 15:54'
labels: []
dependencies: []
ordinal: 158000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move the tense replacement stage before h_alternation in chr-config/verb.yaml so that tense vowels are present when h_alternation rules evaluate right-context vowels on aspect suffixes. Regenerate chr-generated assets and update test_h_alt_in_aspect_suffix.py to assert boundary-wrapped parse targets.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Move tense stage before h_alternation in chr-config/verb.yaml
- [x] #2 Regenerate chr-generated grammar assets via parc_macros/generate_markers.py
- [x] #3 Update test_h_alt_in_aspect_suffix.py to check f'[BOW]{target}[EOW]' in parses
- [x] #4 Verify test_h_alt_in_aspect_suffix.py and full pytest suite pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Edit chr-config/verb.yaml to place 'tense' stage immediately before 'h_alternation'
2. Regenerate chr-generated assets using python parc_macros/generate_markers.py chr-config chr-generated
3. Clear .cache directories to ensure clean graph recompilation
4. Update tests/test_h_alt_in_aspect_suffix.py to assert f'[BOW]{target}[EOW]' in parses
5. Run pytest on tests/test_h_alt_in_aspect_suffix.py and the full pytest suite
6. Complete task criteria and DoD
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reordered stage cascade in chr-config/verb.yaml to place the tense replacement stage immediately after aspect_suffix and before h_alternation. This ensures that following tense vowels are realized in the morph string before h_alternation rules match on right-context vowels, enabling H-alternation on aspect suffixes (such as ih -> i'). Regenerated grammar YAMLs, updated test_h_alt_in_aspect_suffix.py to wrap target in [BOW]...[EOW], and refreshed graph state counts from 1102 to 1312. All 129 tests pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
