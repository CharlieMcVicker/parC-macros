---
id: TASK-149
title: Remove inline imports and fix Any types across codebase
status: In Progress
assignee:
  - '@self'
created_date: '2026-09-08 15:59'
updated_date: '2026-09-08 16:00'
labels: []
dependencies: []
ordinal: 159000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Find all inline imports matching '\s+import' in the codebase, hoist them to the top of their respective files, and replace Any types with specific annotations where possible.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All inline imports are hoisted to the top-level of module files
- [ ] #2 Remove or tighten Any type annotations where possible
- [ ] #3 Full test suite passes without regressions
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect all files with inline imports: parse_chr_dict/reconstruct.py, parse_chr_dict/segment.py, parse_chr_dict/types.py, and tests/*.py.
2. Hoist all inline imports to the top level, avoiding circular dependencies.
3. Replace loose Any types in parse_chr_dict (reconstruct.py, derive.py, types.py, near_misses.py, parse.py) with specific types (VerbForm, CandidateHypothesis, VerbMetadata, etc.).
4. Run full pytest suite and py_compile to verify zero regressions.
<!-- SECTION:PLAN:END -->
