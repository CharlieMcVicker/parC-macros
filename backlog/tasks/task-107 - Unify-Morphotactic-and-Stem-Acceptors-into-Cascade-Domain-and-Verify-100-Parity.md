---
id: TASK-107
title: >-
  Unify Morphotactic and Stem Acceptors into Cascade Domain and Verify 100%
  Parity
status: To Do
assignee: []
created_date: '2026-09-03 13:35'
updated_date: '2026-09-03 13:36'
labels:
  - morphotactics
  - fst
  - verification
dependencies:
  - TASK-105
  - TASK-106
priority: high
ordinal: 112000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate both the morphotactic co-occurrence acceptors (from TASK-105) and stem-shape constraint acceptors (from TASK-106) into parC's initial cascade domain construction. Re-generate chr-inplace-generated and run the full 912-row dictionary verification to assert 100% corpus parity against roots.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Integrate morphotactic and stem-shape constraint acceptors into initial cascade domain compilation in parC
- [ ] #2 Re-generate chr-inplace-generated with unified morphotactic and stem-shape constraints
- [ ] #3 Verify that total FST states remain minimal without Cartesian bloat
- [ ] #4 Run verify_roots_compatibility across all 912 rows in roots.csv and assert 100% pass rate
- [ ] #5 Verify zero regressions across pytest unit test suites
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Integration & Parity Verification Plan

### Integration Architecture:
In parC's paradigm_compilation.py, the initial cascade domain is compiled:
CascadeDomain = open_root_template_fsa ∩ MorphotacticAcceptor ∩ StemShapeAcceptor

1. **MorphotacticAcceptor (TASK-105)**:
   Constrains [DIST=de] to indicative tenses, and [DIST=di] to immediate/infinitive tenses.
2. **StemShapeAcceptor (TASK-106)**:
   Constrains the initial phoneme of <Root> based on [PrefixClass=...], replacing legacy Cartesian feature_acceptors.

### Verification Benchmark:
- Current state: 826 / 912 rows passed (90.6%), 4,566 / 4,738 forms passed (96.4%).
- All 86 failing rows are [DIST] verbs where imperative/infinitive allomorphs (th-, tsu-) failed due to lack of [DIST=di].
- Expected outcome after integration: 912 / 912 rows passed (100.0%), 4,738 / 4,738 forms passed (100.0%).
- Execute via: python scratch/verify_roots_compatibility.py --jobs 8
<!-- SECTION:NOTES:END -->
