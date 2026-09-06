---
id: TASK-128
title: Implement sibilant cluster degemination phonology rule for sk-s verbs
status: To Do
assignee: []
created_date: '2026-09-06 16:57'
labels: []
dependencies: []
priority: medium
type: enhancement
ordinal: 138000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement sibilant degemination / cluster reduction rule (s+s -> s, ts+s -> ts, lhs+s -> lhs) in Cherokee phonology to allow s-final roots to properly inflect and parse with sk-s aspect suffixes without gemination.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define sibilant degemination rule in chr-config/Phonology/Rules
- [ ] #2 Verify verbs like askitska, akalhska, atholhska derive properly under sk-s classes
<!-- AC:END -->
