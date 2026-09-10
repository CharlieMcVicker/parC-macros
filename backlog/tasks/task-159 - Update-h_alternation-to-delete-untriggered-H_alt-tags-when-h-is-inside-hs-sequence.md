---
id: TASK-159
title: >-
  Update h_alternation to delete untriggered H_alt tags when h is inside hs
  sequence
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 14:05'
updated_date: '2026-09-10 14:08'
labels: []
dependencies: []
ordinal: 169000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a verb root has an H_alt tag like [H_alt=glot], but a specific inflected form like future progressive has h inside an /hs/ cluster, the h is not an alternatable HTarget. Update h_alternation.yaml to delete untriggered <H_alt> tags so forms like hikeyuhsehsti transduce cleanly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update delete_h_none in chr-config/Phonology/Rules/h_alternation.yaml to consume untriggered <H_alt> tags
- [x] #2 Regenerate chr-generated assets
- [x] #3 Verify entry 1516 matches StativeFutProg and all tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update delete_h_none in chr-config/Phonology/Rules/h_alternation.yaml to target <H_alt> so any un-triggered H_alt tag is consumed as a no-op when h is in non-alternating contexts like /hs/.
2. Regenerate chr-generated assets via generate_markers.py.
3. Verify that entry 1516 matches StativeFutProg with hikeyuhsehsti and all test suites pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated h_alternation to handle /hs/ sequences by mapping [TEMP_GLOT_H]s -> hs and [TEMP_H]s -> hs, matching HTarget before s and vowels, and successfully verifying entry 1516 as StativeFutProg.
<!-- SECTION:FINAL_SUMMARY:END -->
