---
id: TASK-175
title: >-
  Implement structured intermediate segmentation layer with morpheme anchors and
  semantic elision tagging
status: In Progress
assignee:
  - '@supervisor'
created_date: '2026-10-02 13:17'
updated_date: '2026-10-02 13:29'
labels:
  - fst
  - parc-macros
  - segmentation
dependencies: []
type: feature
ordinal: 185000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A downstream morpheme acquisition game requires structured prebuilt decks where learners tap morphemes in order to assemble a target word. To support this without altering CSV configurations or breaking existing dictionary parsing, we need an intermediate FST layer between abstract morphosyntactic tags and the surface phonetic form. This layer preserves morpheme boundary hyphens `-`, anchors morphemes with their feature tags (e.g. `[Pro=1sg]tsi-`), and marks non-concatenative edge drops with formal semantic tags (e.g. `a[drop]`). The system must compile both a surface `verb.yaml` paradigm (via auto-generated cleanup rules) and a segmented `verb_segmented.yaml` paradigm directly from `chr-config/`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Morpheme replacement rules emit boundary hyphens `-` and preserve morpheme feature identity tags
- [ ] #2 Phonological drop rules replace transient `[TEMP]` with semantic `[drop]` tags attached to dropped phones
- [ ] #3 Dual paradigms `verb.yaml` (surface with cleanup) and `verb_segmented.yaml` (intermediate without cleanup) are generated in `chr-generated/Morphotactics/Paradigm/`
- [ ] #4 All existing tests pass with 100% parity for surface `verb` paradigm
- [ ] #5 Segmented paradigm output can be parsed to extract canonical roots, surface slices, and dropped phones
<!-- AC:END -->
