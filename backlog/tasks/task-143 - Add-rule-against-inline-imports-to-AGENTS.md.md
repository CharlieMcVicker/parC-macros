---
id: TASK-143
title: Add rule against inline imports to AGENTS.md
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-08 13:09'
updated_date: '2026-09-08 13:09'
labels: []
dependencies: []
priority: low
type: docs
ordinal: 153000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add an explicit negative rule/anti-pattern forbidding inline function/method imports in AGENTS.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add rule forbidding inline imports to Anti-Patterns & Negative Rules section in AGENTS.md
- [x] #2 Verify AGENTS.md line count remains strictly under 250 lines
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a bullet in Section 4 (Anti-Patterns & Negative Rules) of AGENTS.md prohibiting inline imports inside functions or methods.
2. Verify total line count remains well under 250 lines.
3. Check acceptance criteria and mark task as Done in backlog.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added explicit anti-pattern rule to Section 4 of AGENTS.md prohibiting inline module imports within functions or methods, mandating top-of-file imports for explicit dependencies and predictable initialization. Document line count confirmed at 122 lines.
<!-- SECTION:FINAL_SUMMARY:END -->
