---
id: TASK-118
title: >-
  Define VerbForm, VerbEntryType, and integrate pronominal resolution into
  VerbMetadata
status: Done
assignee:
  - '@myself'
created_date: '2026-09-04 18:27'
updated_date: '2026-09-04 18:31'
labels: []
dependencies: []
priority: high
type: feature
ordinal: 128000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create VerbForm and VerbEntryType domain models to replace FormParsingSpec and MetaLabelDefinition. Move Pronominal and filter_pronominals into types/pronominals and add get_pronominal_candidates directly to VerbMetadata.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define VerbForm with aspect, tense, person, allows_set_a, and matches(p_data: ParseData) method
- [x] #2 Define VerbEntryType with name and tuple of VerbForm instances (EVENTFUL, STATIVE_FUT_PROG, STATIVE_NO_IMP)
- [x] #3 Integrate Pronominal, filter_pronominals, and VerbMetadata.get_pronominal_candidates without MetaLabel dependencies
- [x] #4 Add unit tests verifying VerbForm matching and VerbMetadata pronominal candidates
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Defined VerbForm, VerbEntryType, and integrated pronominal resolution into VerbMetadata in parse_chr_dict/types.py. Defined Pronominal, ALL_PRONOMINALS, and filter_pronominals in types.py (re-exported in meta_label_compiler.py). Added get_pronominal_candidates and get_pronominal to VerbMetadata matching MetaLabelCombination behavior. Defined standard VerbForm constants (PRES_3RD, PRES_1SG, HABITUAL_3RD, COMPLETIVE_3RD, INCOMPLETIVE_ASSERTIVE_3RD, IMPERATIVE_2ND, FUT_PROG_2ND, INFINITIVE_3RD) and VerbEntryType constants (EVENTFUL, STATIVE_FUT_PROG, STATIVE_NO_IMP). Created tests/test_verb_form_types.py verifying VerbForm matching, pronominal candidate equivalence, and paradigm schemas. All 419 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
