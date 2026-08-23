---
id: TASK-71
title: Investigate overgeneration of roots for entry 44 it's twisting
status: Done
assignee:
  - '@agent'
created_date: '2026-08-23 22:39'
updated_date: '2026-08-23 22:41'
labels: []
dependencies: []
ordinal: 70000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate why entry 44 ('it is twisting') overgenerates roots in roots.csv for different infinitive aspect class variants.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Inspect roots.csv output for entry 44
- [x] #2 Identify why multiple infinitive aspect class variants pass forward inflection validation for entry 44
- [x] #3 Fix reconstruct validation logic or constraint compiler so only the exact matching aspect class passes
- [x] #4 All tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read entry 44 ('it is twisting') from chr-corpus/corpus.csv.
2. Inspect derived roots in roots.csv for corpus_id 44.
3. Test inflect() forward generation for each aspect_class variant of entry 44 against the infinitive surface form.
4. Update validation logic in reconstruct.py or meta_label_compiler.py so over-generated aspect_class variants are rejected.
5. Verify pytest tests pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated overgeneration of roots for entry 44 ('it is twisting'). Reverted temporary reconstruct validation changes and enforced the required stative aspect_class filtering rule (get_label(labels, 'aspect_class').startswith('stative')) when entry_type starts with Stative in parse_chr_dict/__main__.py. Non-stative aspect classes like oh-ol and be-at are now excluded under StativeNoImp for entry 44. All 21 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
