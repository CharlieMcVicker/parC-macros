---
id: TASK-102.4
title: Generate chr-inplace-generated and compile open inflect/parse FSTs
status: To Do
assignee: []
created_date: '2026-09-02 19:51'
labels: []
dependencies:
  - TASK-102.3
parent_task_id: TASK-102
priority: high
type: task
ordinal: 105000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the updated generator against chr-inplace-config to build chr-inplace-generated. Validate all output YAML files and verify that parC successfully compiles the open inflect graph and inverted open parse graph.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Execute generator to produce chr-inplace-generated/
- [ ] #2 Validate all generated YAML files against parc_macros schema suite
- [ ] #3 Compile open inflect graph with parC and verify zero errors
- [ ] #4 Compile open parse graph with parC and verify zero errors
<!-- AC:END -->
