---
id: TASK-146
title: >-
  In-place slot-based grammar specification and language-agnostic generator
  refactor
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-08 14:56'
updated_date: '2026-09-08 15:09'
labels: []
dependencies: []
priority: high
type: spike
ordinal: 156000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Write policy/vision document for in-place slot-based grammar refactor
- [x] #2 Investigate non-programmatic assumptions about slots and verb templates across parc_macros and parse_chr_dict
- [x] #3 Design YAML data structures in verb.yaml parameterizing slots and their inner tag groups
- [x] #4 Create git branch and perform draft implementation/spike
- [x] #5 Verify test suite passes or documents expected behavior on spike branch
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Deep research across codebase for hardcoded slot and template assumptions
2. Draft and publish the policy/vision document in backlog/docs/specifications
3. Create spike git branch
4. Parameterize slots in chr-config/verb.yaml with inner structure TagGroups and optional flags
5. Refactor parc_macros to consume slot definitions generically without hardcoded Cherokee file names/tags
6. Update parse_chr_dict to programmatically derive slot mappings/acceptors where appropriate
7. Run verification suite and summarize findings
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed policy/vision specification (doc-2), investigated non-programmatic assumptions across parc_macros and parse_chr_dict, created spike branch 'feat/inplace-slots-spike', parameterized slots with inner TagGroup structures in chr-config/verb.yaml and Paradigm.json, refactored parc_macros to compile rules and slots.json generically, and updated parse_chr_dict with dynamic slot manifest and root boundary resolution. All 127 tests pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
