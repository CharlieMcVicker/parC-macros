---
id: TASK-175
title: >-
  Implement structured intermediate segmentation layer with morpheme anchors and
  semantic elision tagging
status: Done
assignee:
  - '@supervisor'
created_date: '2026-10-02 13:17'
updated_date: '2026-10-02 14:50'
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
- [x] #1 Morpheme replacement rules emit boundary hyphens `-` and preserve morpheme feature identity tags
- [x] #2 Phonological drop rules replace transient `[TEMP]` with semantic `[drop]` tags attached to dropped phones
- [x] #3 Dual paradigms `verb.yaml` (surface with cleanup) and `verb_segmented.yaml` (intermediate without cleanup) are generated in `chr-generated/Morphotactics/Paradigm/`
- [x] #4 All existing tests pass with 100% parity for surface `verb` paradigm
- [x] #5 Segmented paradigm output can be parsed to extract canonical roots, surface slices, and dropped phones
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented structured intermediate segmentation layer with dual surface and segmented paradigms across parc_macros:
- Clean Surface Codegen: Emits clean surface replacement and phonology rules for verb.yaml, ensuring 100% test parity and fast FST inversion with zero state space explosion.
- Segmented Intermediate Codegen: Emits annotated replacement rules (with boundary hyphens and retained tags like [Pro=1sg.A]tsi-) and semantic phonology rules with [drop] tags for verb_segmented.yaml.
- Dual Paradigm Generation: parc_macros/generate_markers.py emits both chr-generated/Morphotactics/Paradigm/verb.yaml and verb_segmented.yaml.
- Extraction and Transduction Verification: Verified in tests/test_segmented_paradigm.py that canonical dictionary roots, surface slices, and direct surface-to-segmented transduction (T_segment = PARSE(verb) o INFLECT(verb_segmented)) work cleanly across 171/171 passing tests.
<!-- SECTION:FINAL_SUMMARY:END -->
