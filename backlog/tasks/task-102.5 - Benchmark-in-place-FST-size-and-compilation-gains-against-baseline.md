---
id: TASK-102.5
title: Benchmark in-place FST size and compilation gains against baseline
status: To Do
assignee: []
created_date: '2026-09-02 19:51'
labels: []
dependencies:
  - TASK-102.4
parent_task_id: TASK-102
priority: high
type: task
ordinal: 106000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the benchmarking utility against chr-inplace-generated to extract states, arcs, compile times, and disk sizes. Compare directly against baseline metrics recorded in TASK-102.1 and produce a detailed comparative gain report.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Measure states, arcs, file size, and compilation time for chr-inplace-generated open inflect graph
- [ ] #2 Measure states, arcs, file size, and compilation time for chr-inplace-generated open parse graph
- [ ] #3 Measure 100-row parse runtime comparison
- [ ] #4 Generate comparative markdown report with percentage reductions in states, arcs, and time
<!-- AC:END -->
