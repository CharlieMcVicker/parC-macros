---
id: TASK-19
title: Create Cherokee contingent inflection paradigm
status: Done
assignee:
  - '@agent'
created_date: '2026-07-10 19:57'
updated_date: '2026-07-10 20:00'
labels: []
dependencies: []
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate a complex single paradigm using contingent feature classes for both lexical aspect and lexical pronominal paradigm inflections in Cherokee using the new Nested Class Sub-Mappings feature.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement ContingentFeatureMarkers for Cherokee lexical aspect and pronominal paradigms
- [x] #2 Define a single Paradigm file referencing the ContingentFeatureMarkers
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Handwrote contingent markers and paradigm files in chr-base and verified they compile and validate against schemas.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented Cherokee contingent inflections for both lexical aspect and pronominal paradigms using the new nested class sub-mapping feature. The aspect and pronominal configurations are written to ContingentFeatureMarkers files under chr-base/Exponence/ContingentFeatureMarkers, and a single main Paradigm verb.yaml file has been created in chr-base/Morphotactics/Paradigm to import both contingent configurations.
<!-- SECTION:FINAL_SUMMARY:END -->
