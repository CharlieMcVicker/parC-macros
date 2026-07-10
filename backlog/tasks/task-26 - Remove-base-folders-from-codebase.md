---
id: TASK-26
title: Remove base folders from codebase
status: Done
assignee: []
created_date: '2026-07-10 20:22'
updated_date: '2026-07-10 20:23'
labels: []
dependencies: []
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Completely remove the concept of 'base' folders from the codebase. The generator should only use config and generated (and reference folders in tests). Delete empty base folders, and update python arguments, tests, and generation scripts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Delete base folders (chr-base, spanish-base)
- [x] #2 Update generate_markers.py arguments to remove base_dir
- [x] #3 Remove base directory copying logic in generate_markers.py
- [x] #4 Update tests to reflect the removal of base folders
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed base folder arguments and copying logic from generate_markers.py. Updated test suites in test_generation.py to call generate_markers_main without the base folder arguments. Deleted chr-base and spanish-base directories.
<!-- SECTION:FINAL_SUMMARY:END -->
