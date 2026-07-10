---
id: TASK-25
title: Move Phonology folder into config and copy deeply
status: Done
assignee: []
created_date: '2026-07-10 20:22'
updated_date: '2026-07-10 20:22'
labels: []
dependencies: []
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move the Phonology directory from both base folders into their respective config folders, and update generate_markers.py to copy the folder deeply as-is during generation, leaving the base folders empty of Phonology.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Move Spanish Phonology folder from base to config
- [x] #2 Move Cherokee Phonology folder from base to config
- [x] #3 Update build/copy logic to deeply copy Phonology folder as-is from config
- [x] #4 Add tests to verify Phonology is copied correctly
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Moved Phonology folders from spanish-base and chr-base to spanish-config and chr-config respectively, emptying both base folders. Updated generate_markers.py to deeply copy the Phonology folder as-is. Added tests verifying that Phonology is correctly copied during the generation process.
<!-- SECTION:FINAL_SUMMARY:END -->
