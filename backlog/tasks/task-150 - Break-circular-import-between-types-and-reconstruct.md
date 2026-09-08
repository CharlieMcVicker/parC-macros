---
id: TASK-150
title: Break circular import between types and reconstruct
status: To Do
assignee: []
created_date: '2026-09-08 16:24'
labels: []
dependencies: []
ordinal: 160000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix import cycle causing ImportError for VerbForm. Use lazy imports in types.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create task, edit types.py with lazy imports, run test suite, close task.
<!-- AC:END -->
