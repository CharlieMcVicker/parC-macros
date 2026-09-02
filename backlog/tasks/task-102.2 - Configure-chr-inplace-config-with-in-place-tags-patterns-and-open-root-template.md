---
id: TASK-102.2
title: >-
  Configure chr-inplace-config with in-place tags, patterns, and open root
  template
status: To Do
assignee: []
created_date: '2026-09-02 19:51'
labels: []
dependencies:
  - TASK-102.1
parent_task_id: TASK-102
priority: high
type: feature
ordinal: 103000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Clone verified chr-config to chr-inplace-config, declare pattern definitions for <PrepronominalPrefixes> and <Root>, define in-place tags in Inventory and Patterns, update open_root_template in verb.yaml, and adapt drop_root_final and drop_stem_initial_vowel to use local contexts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Clone clean chr-config/ to chr-inplace-config/
- [ ] #2 Define <PrepronominalPrefixes> and <Root> in chr-inplace-config/Phonology/Patterns/phoneme_groups.yaml
- [ ] #3 Define in-place tags in Inventory/alphabet.yaml and Patterns/phoneme_groups.yaml
- [ ] #4 Update open_root_template in chr-inplace-config/verb.yaml to <PrepronominalPrefixes><PrefixClass><Pro><H_ALT>?<Root><AspectClass><Aspect><TenseClass><Tense>
- [ ] #5 Adapt drop_root_final.yaml and drop_stem_initial_vowel.yaml to use local trigger contexts
<!-- AC:END -->
