---
id: TASK-161
title: Optimize H-alternation phonology to eliminate redundant hs matching
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 14:27'
updated_date: '2026-09-10 14:30'
labels: []
dependencies: []
ordinal: 171000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Restrict H-alternation rules to true alternating contexts (h<V> and sonorants), removing identity hs mappings to eliminate duplicate hypothesis explosion across words with hs clusters.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Revert h_alternation right_context to <V> and remove hs identity realization rules
- [x] #2 Verify atananehsv and similar words only parse with [H_alt=none]
- [x] #3 Ensure entries 1516, 821, 825, 1045 and entire test suite pass
- [x] #4 Verify full dictionary derivation performance and hypothesis reduction
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reverted H-alternation phonology to true prevocalic/sonorant context (h<V>|<SonH>) and eliminated redundant [TEMP_*_H]s -> hs identity mapping rules. Fixed 2nd person Set A candidate resolution in get_pronominal_candidates so imperative/future prog uses Set A 2sg.A cleanly on Stative verbs without needing H-alternation shims. Total derived hypotheses dropped from 1555 to 1154 with zero regressions.
<!-- SECTION:FINAL_SUMMARY:END -->
