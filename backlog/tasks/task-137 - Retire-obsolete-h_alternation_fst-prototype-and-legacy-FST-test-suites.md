---
id: TASK-137
title: Retire obsolete h_alternation_fst prototype and legacy FST test suites
status: To Do
assignee: []
created_date: '2026-09-06 18:07'
labels: []
dependencies: []
priority: medium
type: chore
ordinal: 147000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Retire standalone Pynini prototype module parse_chr_dict/h_alternation_fst.py, remove determine_h_alt_glottal_root and prototype re-exports from parse_chr_dict/h_alternation.py, and remove obsolete test suites (tests/test_h_alternation.py, tests/test_h_alternation_corpus.py, and tests/data/) now that parC FST grammar rules in chr-config/chr-generated are natively validated by tests/test_h_alternation_targeted.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Remove parse_chr_dict/h_alternation_fst.py
- [ ] #2 Remove unused determine_h_alt_glottal_root and h_alternation_fst re-exports from parse_chr_dict/h_alternation.py
- [ ] #3 Remove obsolete test suites tests/test_h_alternation.py and tests/test_h_alternation_corpus.py along with tests/data/ CSVs
- [ ] #4 Verify full pytest suite passes cleanly and parC grammar H-alternation tests in test_h_alternation_targeted.py pass
<!-- AC:END -->
