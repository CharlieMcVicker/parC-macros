---
id: TASK-136
title: Delete dead and unreferenced standalone scripts in parse_chr_dict
status: To Do
assignee: []
created_date: '2026-09-06 18:07'
labels: []
dependencies: []
priority: low
type: chore
ordinal: 146000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Delete obsolete, broken, and unreferenced standalone Python scripts in parse_chr_dict/ (build_h_alt_test_corpus.py, test_glasses.py, fix_corpus.py).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Delete parse_chr_dict/build_h_alt_test_corpus.py (broken imports, unused)
- [ ] #2 Delete parse_chr_dict/test_glasses.py (ad-hoc scratch script, unused)
- [ ] #3 Delete parse_chr_dict/fix_corpus.py (one-off legacy migration script, unused)
- [ ] #4 Verify pytest suite passes cleanly with zero errors or warnings
<!-- AC:END -->
