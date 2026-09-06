---
id: TASK-54
title: 'Implement kind:morpheme_replace and rules generation'
status: Done
assignee:
  - '@myself'
created_date: '2026-07-17 16:42'
updated_date: '2026-07-17 16:44'
labels: []
dependencies: []
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a way to replace a prefix rule with a replace this tag rule by changing metadata on a CSV, generating corresponding rules for tags, and mapping them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create parc_macros/generate_morpheme_replace_rules.py
- [x] #2 Modify generate_markers.py to parse morpheme_tag and process kind:morpheme_replace
- [x] #3 Integrate morpheme replace rule generation in generate_markers pipeline
- [x] #4 Verify and test with existing and modified test cases
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create parc_macros/generate_morpheme_replace_rules.py to extract unique form values and map morpheme_tag to them.\n2. Update generate_markers.py to parse morpheme_tag metadata, replace kind:prefix output mapping with kind:rule output referencing the generated rules, and trigger generate_morpheme_replace_rules.\n3. Modify chr-config/verb-pronominal.csv to use kind:morpheme_replace and morpheme_tag: [Pro].\n4. Update chr-config/verb.yaml and relevant templates.\n5. Test and verify correct rule generation and FST integration.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully implemented kind:morpheme_replace. Added generate_morpheme_replace_rules.py to extract unique form values and map tags like [Pro] to them. Integrated with generate_markers.py so that morpheme replacement rules are automatically outputted and referenced via rules instead of prefixes. Updated chr-config/verb-pronominal.csv, chr-config/verb.yaml, and alphabet inventories, and verified behavior via automated tests.
<!-- SECTION:FINAL_SUMMARY:END -->
