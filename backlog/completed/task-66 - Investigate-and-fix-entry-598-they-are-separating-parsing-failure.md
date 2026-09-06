---
id: TASK-66
title: Investigate and fix entry 598 they are separating parsing failure
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 21:38'
updated_date: '2026-08-23 21:39'
labels: []
dependencies: []
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add unit test for entry 598 ('they are separating'), investigate why it fails parsing or reconstruction, and fix.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add test_entry_598 in tests/test_meta_label_compiler.py reading corpus row 598
- [x] #2 Diagnose root cause of parsing/reconstruction failure for entry 598 and fix
- [x] #3 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read row 598 from chr-corpus/corpus.csv.
2. Create test_entry_598 in tests/test_meta_label_compiler.py to test parsing each surface form and running derive_lexical_features_4step / reconstruct_row.
3. Diagnose why entry 598 fails (check open parse graph outputs, pronominal set, aspect class, or reconstruction).
4. Apply fix to meta_label_compiler or reconstruct module.
5. Confirm pytest tests pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated and resolved entry 598 ('they are separating') parsing failure. Created test_real_plural_verb_entry_598 in tests/test_meta_label_compiler.py reading corpus row 598 ('tanakaleniha', 'tostakaleniha', 'tistakalena'). Identified that dual pronominal tags (2dl.A, 2dl.B, 1dl.A, 1dl.B, Edl.A, Edl.B, 3dl.A, 3dl.B) were missing from ALL_PRONOMINALS inventory. Added dual tags to ALL_PRONOMINALS, updated Pronominal.from_tag to categorize dual numbers (dl), and added number='dl' to [PLURAL=TRUE]. All 19 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
