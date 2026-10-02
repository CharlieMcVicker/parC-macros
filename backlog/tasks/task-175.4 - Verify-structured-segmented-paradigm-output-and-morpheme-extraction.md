---
id: TASK-175.4
title: Verify structured segmented paradigm output and morpheme extraction
status: To Do
assignee: []
created_date: '2026-10-02 13:17'
labels:
  - fst
  - testing
  - segmentation
dependencies:
  - TASK-175.3
parent_task_id: TASK-175
type: feature
ordinal: 189000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add automated test coverage and validation utilities verifying that `get_open_inflect_graph(\"verb_segmented\")` outputs correct intermediate strings for Cherokee verbs across classes, with properly anchored feature tags, hyphens, and `[drop]` elision markers. Verify that both canonical roots and surface-aligned slices can be accurately extracted from the intermediate string.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Unit test verifies `inflect(\"verb_segmented\", ...)` outputs expected structured format: `[Pro=...]...-[Root]...[drop]...-[Aspect=...]...-[Tense=...]...`
- [ ] #2 Test verifies canonical dictionary root extraction by removing `[drop]` tags
- [ ] #3 Test verifies surface slice extraction by stripping elided characters and tags
- [ ] #4 Test verifies direct transduction from surface form to segmented string via composed parse/inflect graphs
<!-- AC:END -->
