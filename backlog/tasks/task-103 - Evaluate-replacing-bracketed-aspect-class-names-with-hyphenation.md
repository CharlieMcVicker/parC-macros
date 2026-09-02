---
id: TASK-103
title: Evaluate replacing bracketed aspect class names with hyphenation
status: To Do
assignee: []
created_date: '2026-09-02 20:27'
labels: []
dependencies: []
priority: medium
type: task
ordinal: 108000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Evaluate whether allowing nested brackets in Inventory.json schema (e.g. [AspectClass=become[inf2]]) was strictly necessary or if standardizing aspect class names to use hyphenation (e.g. 'become-inf2', 'apl-imp2') is preferable. Hyphenation would eliminate bracket ambiguity in tag parsing and allow restoring the strict non-nested tag schema regex (^\[[^\]]+\]$).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Evaluate feasibility and trade-offs of converting bracketed aspect class names (e.g. [inf2]) to hyphenated identifiers (e.g. -inf2) across CSV sources and grammar configs
- [ ] #2 Assess impact on dictionary parser, corpus verification, and downstream tools
- [ ] #3 If adopted, implement renaming across datasets and revert Inventory schema regex to strict non-nested brackets
<!-- AC:END -->
