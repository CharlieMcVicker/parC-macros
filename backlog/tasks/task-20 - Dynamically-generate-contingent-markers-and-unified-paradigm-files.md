---
id: TASK-20
title: Dynamically generate contingent markers and unified paradigm files
status: Done
assignee:
  - '@agent'
created_date: '2026-07-10 20:08'
updated_date: '2026-07-10 20:08'
labels: []
dependencies: []
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the generator script in parc_macros/generate_markers.py to dynamically generate nested ContingentFeatureMarkers and unified Paradigm files from config specifications rather than keeping them handwritten in base.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove handwritten files from base
- [x] #2 Implement dynamic generation of ContingentFeatureMarkers and unified Paradigm files
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented dynamic ContingentFeatureMarkers and unified Paradigm generation in generate_markers.py. Configured chr-config/verb.yaml with use_contingent_features. Wiped the handwritten base files and updated tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Dynamically generate ContingentFeatureMarkers and unified Paradigm files when 'use_contingent_features: true' is defined in the POS config. Removed all handwritten files from the base directory and verified that generation works dynamically and passes all tests.
<!-- SECTION:FINAL_SUMMARY:END -->
