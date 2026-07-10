---
id: TASK-24
title: Create config wordlists subfolder and move wordlists there
status: Done
assignee: []
created_date: '2026-07-10 20:20'
updated_date: '2026-07-10 20:20'
labels: []
dependencies: []
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a subfolder under the config directory to house wordlists that are copied as-is, and move the Cherokee (chr) and Spanish wordlists into their respective config folders.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create subfolder under config for wordlists
- [x] #2 Move Spanish and Cherokee wordlists into the new config subfolder
- [x] #3 Update build/copy logic to copy wordlists as-is from their new locations
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Moved Cherokee and Spanish wordlists to their respective config/wordlists subdirectories, and updated generate_markers.py to copy the wordlists as-is. Updated pytest tests to verify correct copy behavior.
<!-- SECTION:FINAL_SUMMARY:END -->
