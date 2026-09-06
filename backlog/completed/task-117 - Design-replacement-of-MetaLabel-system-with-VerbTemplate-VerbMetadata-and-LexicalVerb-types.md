---
id: TASK-117
title: >-
  Design replacement of MetaLabel system with VerbTemplate, VerbMetadata, and
  LexicalVerb types
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 18:13'
updated_date: '2026-09-04 18:27'
labels: []
dependencies: []
priority: high
type: task
ordinal: 127000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Analyze the existing MetaLabel system across parse_chr_dict, reconstruct.py, and meta_label_compiler.py, and determine how to completely replace it with VerbTemplate, VerbMetadata, and LexicalVerb types.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Audit all usages of MetaLabel and related data structures across parse_chr_dict
- [x] #2 Determine how LexicalVerb, VerbTemplate, and VerbMetadata can fully replace MetaLabel in parsing, candidate generation, and reconstruction
- [x] #3 Provide an architectural migration design
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit MetaLabel usage across parse_chr_dict, reconstruct.py, and types.py.\n2. Define domain replacement types (VerbForm, VerbEntryType) and identify how VerbTemplate, VerbMetadata, and LexicalVerb subsume MetaLabel capabilities.\n3. Present comprehensive architectural analysis and replacement blueprint to the user.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Audited all MetaLabel and MetaConstraintCompiler usages across parse_chr_dict, reconstruct.py, and types.py. Produced a comprehensive architectural design replacing the obsolete FST meta-label system with pure domain models: VerbForm, VerbEntryType, and enhanced VerbMetadata/LexicalVerb.
<!-- SECTION:FINAL_SUMMARY:END -->
