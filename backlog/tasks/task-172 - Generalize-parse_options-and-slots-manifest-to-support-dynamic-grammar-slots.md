---
id: TASK-172
title: Generalize parse_options and slots manifest to support dynamic grammar slots
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 17:29'
updated_date: '2026-09-10 17:36'
labels: []
dependencies: []
ordinal: 182000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor parse_options.py, segment.py, and slots.py to eliminate hardcoded Cherokee tag literals and rigid dataclass fields. Remove object.__setattr__ mutation in frozen dataclasses and ensure new slots like VoiceInfix or NFS are cleanly supported.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Eliminate object.__setattr__ mutation pattern on frozen RootParseOptions dataclass
- [x] #2 Generalize PrefixBundle, SuffixBundle, and RootParseOptions to dynamically represent all slots present in slot manifest
- [x] #3 Update FALLBACK_MANIFEST in parse_chr_dict/slots.py to match latest template and slot definitions
- [x] #4 Replace hardcoded prepronominal tag literals in parse_options.py and segment.py with manifest-driven lookups
- [x] #5 All pytest test suites pass without regression
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored parse_options.py, segment.py, and slots.py to eliminate hardcoded Cherokee prefix literals and object.__setattr__ mutations. Added RootParseOptions.create factory, PrefixBundle/SuffixBundle .slots properties and .get() lookups, dynamic prepronominal tag discovery in slots.py and segment.py, and comprehensive test coverage. All 163 pytest tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
