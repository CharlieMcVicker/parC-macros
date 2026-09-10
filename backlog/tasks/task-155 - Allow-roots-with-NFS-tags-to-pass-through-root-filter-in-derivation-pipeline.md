---
id: TASK-155
title: Allow roots with NFS tags to pass through root filter in derivation pipeline
status: Done
assignee:
  - '@agent'
created_date: '2026-09-09 18:42'
updated_date: '2026-09-09 18:43'
labels: []
dependencies: []
ordinal: 165000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Root filter FSA in parse_chr_dict/parse.py stripped bracketed tags via get_just_root, causing candidate hypotheses containing non-final suffix tags (such as [NFS=AMB] in corpus entry 208) to be filtered out during multi-form derivation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update build_root_filter_fsa to tokenize roots preserving bracketed tags
- [x] #2 Verify entry 208 derives with [NFS=AMB] root into roots.csv
- [x] #3 Update test fixtures/counts if necessary and ensure tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update tokenize_root / build_root_filter_fsa in parse_chr_dict/parse.py so tags within roots are retained and properly tokenized into FST symbol sequences.
2. Update tests (test_config.py, test_markers_generation.py, test_nfs.py) to account for NFS tags and stages.
3. Verify full test suite and verify entry 208 derivation outputs [NFS=AMB].
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated tokenize_root and build_root_filter_fsa in parse_chr_dict/parse.py so roots containing embedded tags such as [NFS=AMB] are tokenized into valid symbol sequences rather than stripped by get_just_root. Updated test fixtures in test_config.py and test_markers_generation.py, and added full multi-form derivation test for entry 208 in test_nfs.py.
<!-- SECTION:FINAL_SUMMARY:END -->
