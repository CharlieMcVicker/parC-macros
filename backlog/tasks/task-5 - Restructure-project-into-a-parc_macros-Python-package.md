---
id: TASK-5
title: Restructure project into a parc_macros Python package
status: Done
assignee:
  - '@myself'
created_date: '2026-07-04 19:28'
updated_date: '2026-07-04 20:13'
labels: []
dependencies: []
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Restructure the codebase into a standard package structure under parc_macros/. Move yaml_validation.py and generate_markers.py inside the package, set up __init__.py, update imports, and configure entry points or wrapper scripts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create parc_macros/ package directory with __init__.py
- [x] #2 Move yaml_validation.py and generate_markers.py into parc_macros/
- [x] #3 Update python imports and ensure scripts execute correctly from new location
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Restructured the codebase into a standard package structure under parc_macros/. Moved yaml_validation.py, generate_markers.py, and schemas into parc_macros/ with a proper __init__.py. Updated tests to use the new package imports.
<!-- SECTION:FINAL_SUMMARY:END -->
