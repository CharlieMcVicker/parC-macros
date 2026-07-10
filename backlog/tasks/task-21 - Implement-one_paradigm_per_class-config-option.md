---
id: TASK-21
title: Implement one_paradigm_per_class config option
status: Done
assignee:
  - '@agent'
created_date: '2026-07-10 20:09'
updated_date: '2026-07-10 20:12'
labels: []
dependencies: []
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename and invert the paradigm configuration flag to one_paradigm_per_class, defaulting to true to preserve the behavior of generating one paradigm per class (like Spanish), while setting it to false for Cherokee to generate unified contingent paradigms.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement one_paradigm_per_class flag in generator
- [x] #2 Update chr-config/verb.yaml with one_paradigm_per_class set to false
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added one_paradigm_per_class config option defaulting to true. Configured Cherokee to false. Ensured Exponence/FeatureMarkers is always created.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Renamed and inverted the configuration flag to one_paradigm_per_class, defaulting to true to preserve the default behavior of generating one paradigm per class (like Spanish). Configured Cherokee's verb.yaml to set this to false to generate unified contingent paradigms. Also, ensured the Exponence/FeatureMarkers directory is always created in the output directory even when empty to satisfy parC path requirements.
<!-- SECTION:FINAL_SUMMARY:END -->
