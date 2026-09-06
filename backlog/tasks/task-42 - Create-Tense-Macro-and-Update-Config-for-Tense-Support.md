---
id: TASK-42
title: Create Tense Macro and Update Config for Tense Support
status: Done
assignee:
  - '@agent'
created_date: '2026-07-15 16:02'
updated_date: '2026-09-06 17:21'
labels: []
dependencies: []
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add Tense support to Cherokee configuration, create a simple two-row CSV for Tense, and update the generator code if necessary.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create a two-row CSV verb-tense.csv with tense features and surface values
- [x] #2 Update chr-config/verb.yaml with tense features
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented verb-tense.csv with a_present and i_present classes across tense features, updated chr-config/verb.yaml to include the tense stage and template, and verified tense replace rules generate and pass tests.
<!-- SECTION:FINAL_SUMMARY:END -->
