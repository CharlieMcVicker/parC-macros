---
id: TASK-142
title: Condense file tree in AGENTS.md to high-signal core files
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-08 13:07'
updated_date: '2026-09-08 13:08'
labels: []
dependencies: []
priority: medium
type: docs
ordinal: 152000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Shorten and prune the source file tree in AGENTS.md to eliminate anti-pattern bait and focus strictly on high-signal core files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Prune generated directory tree and redundant sub-generators from AGENTS.md
- [x] #2 Highlight key core architecture files in parse_chr_dict and parc_macros
- [x] #3 Verify total line count of AGENTS.md remains strictly under 250 lines
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update Section 6 of AGENTS.md to replace the 35-line verbose tree with the 16-line high-density core tree.
2. Update tree maintenance instructions to reflect the focused view.
3. Verify line count and format of AGENTS.md.
4. Mark acceptance criteria and complete task in backlog.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Condensed Section 6 file tree in AGENTS.md from 35 lines to 16 lines, pruning anti-pattern bait (chr-generated subdirectories) and secondary sub-generators to highlight the core architecture files across parc_macros and parse_chr_dict. Reduced total AGENTS.md line count from 145 to 121 lines.
<!-- SECTION:FINAL_SUMMARY:END -->
