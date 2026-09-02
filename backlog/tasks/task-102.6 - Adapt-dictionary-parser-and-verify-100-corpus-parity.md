---
id: TASK-102.6
title: Adapt dictionary parser and verify 100% corpus parity
status: To Do
assignee: []
created_date: '2026-09-02 19:51'
labels: []
dependencies:
  - TASK-102.5
parent_task_id: TASK-102
priority: high
type: task
ordinal: 107000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Adapt parse string extraction and hypothesis filtering in parse_chr_dict to read in-place tags and use output-acceptor constraints. Run full dictionary parsing on chr-corpus/corpus.csv and verify 100% parity with baseline roots.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Adapt read_labels / parse regexes to extract in-place slot tags ([PrefixClass], [Pro], [AspectClass], [Aspect], [TenseClass], [Tense])
- [ ] #2 Implement output-acceptor composition for candidate hypothesis constraint filtering
- [ ] #3 Run full dictionary parse on chr-corpus/corpus.csv using chr-inplace-generated
- [ ] #4 Assert 100% lexical hypothesis parity (h_root, glottal_root, classes) against baseline roots.csv
- [ ] #5 Verify zero regressions across all pytest test suites
<!-- AC:END -->
