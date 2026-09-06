---
id: TASK-111.3
title: >-
  Update chr-inplace-config patterns, inventory, template, and drop_root_final
  rules
status: Done
assignee:
  - '@agent'
created_date: '2026-09-03 16:30'
updated_date: '2026-09-03 16:43'
labels: []
dependencies:
  - TASK-111.1
parent_task_id: TASK-111
priority: high
type: task
ordinal: 119000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update chr-inplace-config files to support the new unified aspect classes and optional <Variant> slot. Update open_root_template in verb.yaml, define <Variant> pattern and simplify <AspectClass> in phoneme_groups.yaml, update alphabet.yaml, and adapt drop_root_final.yaml triggers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update open_root_template in chr-inplace-config/verb.yaml with optional <Variant> slot
- [x] #2 Define <Variant> pattern and replace 93-class regex in phoneme_groups.yaml with unified base classes
- [x] #3 Register [Variant=2], [Variant=3], [Variant=4] in alphabet.yaml and clean up bracketed class tokens
- [x] #4 Update drop_root_final.yaml right_context triggers to use [AspectClass=Class][Variant=N][Aspect=Feature]
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update chr-inplace-config/verb.yaml open_root_template to include <Variant>\n2. Add <Variant> pattern ('([Variant=2]|[Variant=3]|[Variant=4])?') to chr-inplace-config/Phonology/Patterns/phoneme_groups.yaml\n3. Update <AspectClass> pattern in phoneme_groups.yaml to contain only the 55 base aspect classes\n4. Add [Variant=2], [Variant=3], [Variant=4] to chr-inplace-config/Phonology/Inventory/alphabet.yaml and clean up bracketed classes\n5. Update drop_root_final.yaml triggers to use [AspectClass=Class][Variant=idx][Aspect=Feature]\n6. Verify YAML configs parse cleanly
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated chr-inplace-config to support unified base aspect classes and [Variant=N] morpheme tags:
- Updated open_root_template in chr-inplace-config/verb.yaml to include optional <Variant> slot.
- Added <Variant> pattern ('([Variant=2]|[Variant=3]|[Variant=4])?'), updated <AspectClass> pattern with 55 clean base classes, and updated <Morpheme> pattern in chr-inplace-config/Phonology/Patterns/phoneme_groups.yaml.
- Registered [Variant=2], [Variant=3], [Variant=4] and cleaned up bracketed aspect class tags to 55 clean base tags in chr-inplace-config/Phonology/Inventory/alphabet.yaml.
- Updated mark_final and mark_final_two right_context triggers in chr-inplace-config/Phonology/Rules/drop_root_final.yaml to condition on [AspectClass=Class][Variant=N][Aspect=Feature].
- Verified syntax, inventory, rules, and template compilation across test suite.
<!-- SECTION:FINAL_SUMMARY:END -->
