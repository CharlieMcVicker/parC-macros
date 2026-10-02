---
id: TASK-175.2
title: 'Implement semantic [drop] tagging in phonology rule generators'
status: To Do
assignee: []
created_date: '2026-10-02 13:17'
labels:
  - fst
  - parc-macros
  - phonology
dependencies:
  - TASK-175.1
parent_task_id: TASK-175
type: feature
ordinal: 187000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Non-concatenative edge drops (stem-initial vowel dropping and final root dropping) currently mark segments with transient `[TEMP]` and then erase them to empty string. To allow downstream consumers to recognize both the canonical root and the elided phone, update `parc_macros/generate_phonology.py` to replace `[TEMP]` with a semantic `[drop]` tag attached to the elided phone (e.g. `a[drop]`, `v[drop]`, `<Phone>[drop]`).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `generate_phonology.py` generates `mark_stem_initial_vowel.yaml` using `[drop]` instead of `[TEMP]` (e.g. `a` -> `a[drop]`, `v` -> `v[drop]`)
- [ ] #2 `generate_phonology.py` updates `drop_stem_initial_vowel.yaml` to retain elided characters in the intermediate representation
- [ ] #3 `generate_phonology.py` generates `drop_root_final.yaml` retaining the dropped phone before `[drop]` (e.g. `<Phone>[drop]`)
- [ ] #4 Generated phonology YAML rules pass `python parc_macros/yaml_validation.py chr-generated/`
<!-- AC:END -->
