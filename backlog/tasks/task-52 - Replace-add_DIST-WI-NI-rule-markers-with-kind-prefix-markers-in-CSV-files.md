---
id: TASK-52
title: 'Replace add_DIST/WI/NI rule-markers with kind:prefix markers in CSV files'
status: In Progress
assignee:
  - '@agent'
created_date: '2026-07-16 23:25'
updated_date: '2026-07-16 23:25'
labels: []
dependencies: []
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The two-stage dummy-token strategy fails because add_DIST/add_WI/add_NI use epsilon insertion ("" → "[DIST]") which creates cyclic FSTs when composed with the Kleene-star stems_domain_acceptor in the stage cascade. The fix is to replace the 'add_X' stage CSV rows (which emit kind:rule markers for $add_DIST etc.) with 'kind:prefix' markers that directly insert [DIST]/[WI]/[NI] at word start. prefix markers compile as [BOW]→[BOW][X], a proper non-epsilon substitution that avoids the cyclic FST problem.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Update verb-distributive.csv to use kind:prefix value:[DIST] instead of kind:rule value:$add_DIST
- [ ] #2 Update verb-wi.csv to use kind:prefix value:[WI] instead of kind:rule value:$add_WI
- [ ] #3 Update verb-partitive.csv to use kind:prefix value:[NI] instead of kind:rule value:$add_NI
- [ ] #4 Regenerate chr-generated configs
- [ ] #5 Update minimal-optional-test grammar to also use kind:prefix
- [ ] #6 Run tests to verify the fix
<!-- AC:END -->
