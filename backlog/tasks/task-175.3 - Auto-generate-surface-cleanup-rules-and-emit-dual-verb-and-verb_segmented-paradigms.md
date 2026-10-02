---
id: TASK-175.3
title: >-
  Auto-generate surface cleanup rules and emit dual verb and verb_segmented
  paradigms
status: To Do
assignee: []
created_date: '2026-10-02 13:17'
labels:
  - fst
  - parc-macros
  - paradigms
dependencies:
  - TASK-175.2
parent_task_id: TASK-175
type: feature
ordinal: 188000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
To support both clean surface FST parsing (for dictionary derivation) and structured intermediate FST outputs (for game deck export), `parc_macros/generate_markers.py` must auto-generate a `strip_intermediate_markup.yaml` rule and emit two paradigm configurations in `chr-generated/Morphotactics/Paradigm/`: `verb.yaml` (full cascade with cleanup) and `verb_segmented.yaml` (intermediate cascade without cleanup). This guarantees 100% surface backward-compatibility while exposing first-class segmented inflection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `parc_macros/generate_markers.py` generates `chr-generated/Phonology/Rules/strip_intermediate_markup.yaml` deleting tags, dropped segments, and hyphens
- [ ] #2 `generate_markers.py` emits `chr-generated/Morphotactics/Paradigm/verb.yaml` with `strip_intermediate_markup` as the final stage
- [ ] #3 `generate_markers.py` emits `chr-generated/Morphotactics/Paradigm/verb_segmented.yaml` without the cleanup stage
- [ ] #4 All 129 existing tests pass with 100% parity on surface `verb` paradigm via `pytest`
<!-- AC:END -->
