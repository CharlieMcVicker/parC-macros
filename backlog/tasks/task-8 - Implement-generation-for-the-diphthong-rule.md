---
id: TASK-8
title: Implement generation for the diphthong rule
status: Done
assignee:
  - '@myself'
created_date: '2026-07-04 20:26'
updated_date: '2026-07-04 20:43'
labels: []
dependencies: []
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add generation for the diphthong rule: 1. Add diphthong endings row to suffix table, 2. Create new verb_diphthong CSV, 3. Add verb_spec.yaml for stage order and stage definitions. When generating, look at verb_spec.yaml, read CSVs, collect paradigms, and write files with appropriate stages in sequence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add row for diphthong endings to suffix table
- [x] #2 Create verb_diphthong.csv with one row for diphthong and Y/N
- [x] #3 Create/modify verb_spec.yaml to specify stages and order
- [x] #4 Update python generation code to read verb_spec.yaml and CSVs, collect paradigms, and output files with stages in sequence
- [x] #5 Validate that tests pass and generation functions correctly with new diphthong rule
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented multi-stage paradigm generation to support the diphthong vowel-alternation rule. Added diphthong suffixes to verb-suffix.csv. Created verb_diphthong.csv specifying the rule name in metadata (# rule: $diphthongization) and mapping its application with Y/N values. Created verb_spec.yaml for phase/stage order. Updated parc_macros/generate_markers.py to parse rule metadata, map 'Y' entries to the rule, and skip 'N'/empty entries. Cleaned up the 'spanish-base' folder by removing files that are now generated dynamically (verb_diphthong.yaml and verb_diphthong_present.yaml). All validation tests pass successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
