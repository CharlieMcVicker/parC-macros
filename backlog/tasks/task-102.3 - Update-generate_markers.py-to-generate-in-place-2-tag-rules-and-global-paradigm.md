---
id: TASK-102.3
title: >-
  Update generate_markers.py to generate in-place 2-tag rules and global
  paradigm
status: To Do
assignee: []
created_date: '2026-09-02 19:51'
labels: []
dependencies:
  - TASK-102.2
parent_task_id: TASK-102
priority: high
type: enhancement
ordinal: 104000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enhance parc_macros/generate_markers.py and generate_morpheme_replace_rules.py to generate in-place adjacent 2-tag string_map rules for pronominal, aspect, and tense slots, and generate a lean unified Paradigm using global_markers without ContingentFeatureMarkers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Support generating in-place 2-tag string_map rules ([PrefixClass=...][Pro=...], [AspectClass=...][Aspect=...], [TenseClass=...][Tense=...])
- [ ] #2 Support generating Paradigm YAML with stage-ordered global_markers
- [ ] #3 Ensure backwards compatibility with standard trailing-label configs
- [ ] #4 Verify generated YAML configs pass JSON schema validation
<!-- AC:END -->
