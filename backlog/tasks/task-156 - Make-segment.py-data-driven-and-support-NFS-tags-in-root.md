---
id: TASK-156
title: Make segment.py data-driven and support NFS tags in root
status: Done
assignee:
  - '@agent'
created_date: '2026-09-09 19:11'
updated_date: '2026-09-09 19:13'
labels: []
dependencies: []
ordinal: 166000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update segment.py to handle NFS tags in verb roots dynamically and make slot/tag categorization data-driven from verb configuration rather than hardcoded.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 segment.py correctly parses and categorizes NFS tags and roots
- [x] #2 segment.py categorization is data-driven from configuration where possible
- [x] #3 All tests pass
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored parse_chr_dict/segment.py to dynamically construct slot and tag category mappings from the slot manifest (slots.json). Updated arc categorization and morpheme segmentation to retain internal root tags such as Non-Final Suffixes ([NFS=...]) within the Root morpheme, while dynamically classifying prefix and suffix slot tags from grammar configuration. Added tests in tests/test_segment.py covering NFS verbs.
<!-- SECTION:FINAL_SUMMARY:END -->
