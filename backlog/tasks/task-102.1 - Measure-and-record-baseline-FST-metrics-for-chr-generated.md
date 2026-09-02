---
id: TASK-102.1
title: Measure and record baseline FST metrics for chr-generated
status: To Do
assignee: []
created_date: '2026-09-02 19:51'
labels: []
dependencies: []
parent_task_id: TASK-102
priority: high
type: task
ordinal: 102000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a benchmarking utility to measure and document the baseline FST metrics (state count, arc count, graph compilation time, FST file size on disk, and corpus parse time) for the existing chr-generated grammar.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create a benchmarking script in scratch/ to extract FST statistics from parC compiled graphs
- [ ] #2 Measure open inflect graph states, arcs, file size, and compilation time for chr-generated
- [ ] #3 Measure open parse graph states, arcs, file size, and compilation time for chr-generated
- [ ] #4 Measure 100-row parse runtime on chr-corpus/corpus.csv
- [ ] #5 Save baseline results as reference JSON/Markdown
<!-- AC:END -->
