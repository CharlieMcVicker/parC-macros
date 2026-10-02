---
id: TASK-176
title: >-
  End-to-end regression review of dictionary derivation pipeline after Voice and
  NFS slot promotions
status: Done
assignee:
  - '@supervisor'
created_date: '2026-10-02 15:04'
updated_date: '2026-10-02 15:35'
labels: []
dependencies:
  - TASK-167
  - TASK-168
ordinal: 190000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run full parse_chr_dict batch derivation across chr-corpus/corpus.csv following the completion and merging of TASK-167 (Voice slot promotion) and TASK-168 (NFS slot promotion), ensuring zero regressions in errors.csv and verifying exact roots.csv consistency.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Run full dictionary derivation (YAML_DIR=chr-generated/ python -u -m parse_chr_dict) on main branch after TASK-167 and TASK-168 merges
- [x] #2 Confirm zero unexpected regressions in errors.csv
- [x] #3 Verify that roots.csv has clean stems, voice_infix, and nfs columns properly populated
- [x] #4 Verify all pytest unit tests pass cleanly
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Recompile markers and validate YAML schemas to ensure build artifacts are up to date.\n2. Run full pytest suite.\n3. Run parse_chr_dict batch derivation workflow against chr-corpus/corpus.csv.\n4. Verify git status and diff on roots.csv and errors.csv to ensure no regressions and expected schema changes.\n5. Complete final summary and close task.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Executed full end-to-end regression validation on main branch after merging TASK-167 and TASK-168. Re-generated markers and validated YAML schemas with zero errors. Verified 171/171 pytest unit tests pass. Executed parse_chr_dict batch derivation workflow across all 707 corpus entries, verifying zero regressions in errors.csv and exact clean output in roots.csv with voice_infix and nfs columns properly populated.
<!-- SECTION:FINAL_SUMMARY:END -->
