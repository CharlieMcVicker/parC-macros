---
id: TASK-65
title: Investigate and fix plural verb form parsing failures
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 21:29'
updated_date: '2026-08-23 21:31'
labels: []
dependencies: []
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a unit test reading a real plural verb entry from chr-corpus/corpus.csv and investigate why plural forms are failing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create unit test in tests/test_plural_verb_parsing.py for a real plural corpus row
- [x] #2 Investigate root cause of plural verb parsing failures and fix meta-label compiler/acceptor logic
- [x] #3 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read chr-corpus/corpus.csv to find a real plural verb entry (e.g. entry with plural pronominals or plural markers).
2. Create unit test tests/test_plural_verb_parsing.py that loads that corpus entry and runs derive_lexical_features_4step / reconstruct_row.
3. Diagnose why plural forms fail (e.g., pronominal tag definitions for 3ns.A, 3ns.B, 1pl, 2pl, or [PLURAL=TRUE] filter definition).
4. Fix meta_label_compiler.py / pronominal definitions.
5. Run pytest test suite to confirm 100% pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated and resolved plural verb form parsing failures. Added test_real_plural_verb_entry_355 in tests/test_meta_label_compiler.py loading real plural entry 355 ('anatalhisiha', 'otsatalhisiha'). Fixed 3rd person pronominal filters in META_LABELS to allow all 3rd person pronominals (3sg and 3ns). Fixed Pronominal.from_tag to categorize exclusive 1st person plural tags (Epl.A, Epl.B, E.A, E.B) as 1st person. Fixed derive_lexical_features_4step to propagate only unambiguous meta-labels common across candidate parse paths. All 18 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
