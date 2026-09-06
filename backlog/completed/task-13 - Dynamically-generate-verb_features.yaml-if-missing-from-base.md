---
id: TASK-13
title: Dynamically generate verb_features.yaml if missing from base
status: Done
assignee:
  - '@myself'
created_date: '2026-07-04 20:54'
updated_date: '2026-07-04 20:54'
labels: []
dependencies: []
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update pipeline to construct verb_features.yaml programmatically when it is absent from the base template, allowing the base to be slimmed down further by removing Exponence/FeatureDefinitions entirely.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update generate_markers.py to initialize and save verb_features.yaml if not present in spanish-base
- [x] #2 Remove Exponence directory and its files from spanish-base
- [x] #3 Verify that tests pass successfully
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify generate_markers.py to initialize fd_content with kind=FeatureDefinitions and features={conjugation_class: []} if fd_file does not exist.\n2. Delete the Exponence/FeatureDefinitions directory and its contents from spanish-base.\n3. Run pytest to confirm the generated output matches spanish-reference exactly.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated generate_markers.py to dynamically initialize and write verb_features.yaml if it is missing in the base directory. Removed the Exponence/FeatureDefinitions folder and files from spanish-base, successfully verified that tests pass, and ran code generation correctly.
<!-- SECTION:FINAL_SUMMARY:END -->
