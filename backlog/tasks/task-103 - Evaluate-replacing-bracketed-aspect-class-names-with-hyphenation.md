---
id: TASK-103
title: Evaluate replacing bracketed aspect class names with hyphenation
status: Done
assignee: []
created_date: '2026-09-02 20:27'
updated_date: '2026-09-03 18:13'
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
- [x] #1 Evaluate feasibility and trade-offs of converting bracketed aspect class names (e.g. [inf2]) to hyphenated identifiers (e.g. -inf2) across CSV sources and grammar configs
- [x] #2 Assess impact on dictionary parser, corpus verification, and downstream tools
- [x] #3 If adopted, implement renaming across datasets and revert Inventory schema regex to strict non-nested brackets
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Resolved by TASK-111: Rather than merely hyphenating bracketed variant names (e.g. become-inf2), aspect classes were unified into base classes (e.g. become) with local [Variant=N] tags on varying aspect forms. This completely eliminated nested brackets as well as overgeneration on non-varying forms.
<!-- SECTION:FINAL_SUMMARY:END -->
