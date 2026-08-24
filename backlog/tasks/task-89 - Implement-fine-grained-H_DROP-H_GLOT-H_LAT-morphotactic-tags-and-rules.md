---
id: TASK-89
title: 'Implement fine-grained [H_DROP], [H_GLOT], [H_LAT] morphotactic tags and rules'
status: Done
assignee:
  - '@subagent'
created_date: '2026-08-24 16:31'
updated_date: '2026-08-24 16:34'
labels: []
dependencies: []
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure fine-grained H-alternation tags ([H_DROP], [H_GLOT], [H_LAT], [H_NONE]) in Inventory and Patterns, define deterministic context-sensitive rules in h_alternation.yaml, and regenerate chr-generated/.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add [H_DROP], [H_GLOT], [H_LAT], [H_NONE] to Inventory and <H_ALT> to Patterns
- [x] #2 Update chr-config/Phonology/Rules/h_alternation.yaml with tag-specific deterministic rules
- [x] #3 Update open_root_template in chr-config/verb.yaml and regenerate grammar assets
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add H_ALT tags to alphabet.yaml and phoneme_groups.yaml in chr-config, min-min-config, min-min-insertion-config.
2. Update h_alternation.yaml with tag-specific rules (drop, glot, lat, delete_h_alt_tags).
3. Update open_root_template in verb.yaml.
4. Regenerate markers and run tests.
5. Check ACs, add final summary, and mark Done.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Configured fine-grained H-alternation tags ([H_DROP], [H_GLOT], [H_LAT], [H_NONE]) in Inventory and Patterns across configs, defined deterministic context-sensitive rules in h_alternation.yaml (h_alternation_drop, h_alternation_glot, h_alternation_lat, delete_h_alt_tags), updated open_root_template in chr-config/verb.yaml, and regenerated grammar assets for chr-generated and min-min-insertion-generated.
<!-- SECTION:FINAL_SUMMARY:END -->
