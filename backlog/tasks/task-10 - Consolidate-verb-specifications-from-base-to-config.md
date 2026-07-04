---
id: TASK-10
title: Consolidate verb specifications from base to config
status: Done
assignee:
  - '@agent'
created_date: '2026-07-04 20:49'
updated_date: '2026-07-04 20:50'
labels: []
dependencies: []
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move relevant verb info from spanish-base/Exponence/FeatureDefinitions/verb_features.yaml and spanish-base/Lexicon/PartOfSpeech/verb.yaml into spanish-config/verb_spec.yaml, renaming it to verb.yaml and slimming down spanish-base.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create/update verb.yaml in config with consolidated features and lexicon info
- [x] #2 Remove/slim down features in spanish-base
- [x] #3 Ensure tests still pass or adapt tests if needed
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Moved verb inflectional and lexical feature configurations to spanish-config/verb.yaml, removed spanish-base/Lexicon/PartOfSpeech/verb.yaml, slimmed down verb_features.yaml in base, updated the generation pipeline script to load verb.yaml and generate PartOfSpeech verb.yaml under the generated build output, and successfully verified everything with tests.
<!-- SECTION:FINAL_SUMMARY:END -->
