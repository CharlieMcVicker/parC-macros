---
id: TASK-44
title: Support Middle Voice as a Lexical Feature
status: Done
assignee:
  - '@agent'
created_date: '2026-07-15 21:25'
updated_date: '2026-07-15 21:26'
labels: []
dependencies: []
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update generate_markers.py to correctly parse and process middle_voice when it is defined under lexical_features in verb.yaml.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Ensure middle_voice defined in lexical_features is correctly parsed
- [x] #2 Verify middle_voice is written to FeatureDefinitions with values and optional key
- [x] #3 Verify generate_part_of_speech_config outputs a flat list of strings for lexical_features in PartOfSpeech
- [x] #4 Write a new test file validating these behaviors
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated generate_markers.py to support lexical_features defined as complex structures/dictionaries (like middle_voice) under lexical_features in verb.yaml. Built robust support to handle both standard nested dict representations and flatter indentation variations seamlessly. Updated generate_part_of_speech_config to generate a flat string list for lexical_features in the output PartOfSpeech YAML, and added a new unit test validating these updates.
<!-- SECTION:FINAL_SUMMARY:END -->
