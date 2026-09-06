---
id: TASK-113
title: 'Eliminate TenseClass: replace generic present with present_a and present_i'
status: In Progress
assignee:
  - '@subagent'
created_date: '2026-09-03 18:14'
updated_date: '2026-09-06 17:46'
labels: []
dependencies: []
modified_files:
  - tests/test_acceptors.py
  - tests/test_chr_wildcard_parse.csv
  - tests/test_chr_wildcard_parse.py
  - tests/test_clean_inplace_generation.py
  - tests/test_comparative_benchmark.py
  - tests/test_derive_pipeline.py
  - tests/test_h_alternation_targeted.py
  - tests/test_inplace_compilation.py
  - tests/test_inplace_config.py
  - tests/test_inplace_markers_generation.py
  - tests/test_lexical_verb_types.py
  - tests/test_verb_form_types.py
  - tests/test_yaml_validation.py
ordinal: 123000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Eliminate TenseClass entirely from grammar, phonology, and Python codebase. Replace generic present tense with present_a and present_i.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update chr-config/verb-tense.csv and chr-config/verb.yaml to remove class_feature/<TenseClass> and define present_a and present_i
- [x] #2 Regenerate / update phonology and morpheme replacement rules (tense_replace.yaml, etc.) eliminating TenseClass
- [x] #3 Update parse_chr_dict/types.py: eliminate generic present, support present_a and present_i in VerbForm.matches, move tense_present_class to VerbMetadata, update VerbTemplate and LexicalVerb
- [x] #4 Update parse_chr_dict/derive.py, parse.py, reconstruct.py: remove TenseClass parsing and use present_a/present_i directly
- [x] #5 Update test suite and ensure all pytest tests pass cleanly
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 All unit tests pass
- [x] #2 Clean git status and tracked modified files in backlog
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update chr-config/verb-tense.csv (remove class_feature, define present_a and present_i) and chr-config/verb.yaml (remove <TenseClass> from open_root_template, update tense features).
2. Update generator scripts in parc_macros (generate_inplace_phonology.py, generate_morpheme_replace_rules.py) and regenerate phonology/rules assets.
3. Update parse_chr_dict/types.py: eliminate generic present, support present_a/present_i matching in VerbForm, move tense_present_class/is_i_present to VerbMetadata, remove tense_present_class from VerbTemplate, update LexicalVerb.inflect_form and to_row_dict.
4. Update parse_chr_dict/derive.py, parse.py, reconstruct.py to remove TenseClass and parse present_a/present_i directly.
5. Update test suite (test_verb_form_types.py, test_lexical_verb_types.py, test_derive_pipeline.py, test_inplace_markers_generation.py, etc.) and verify all tests pass cleanly.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Eliminated TenseClass entirely from the Cherokee grammar, phonology, and Python codebase:
1. Updated chr-config/verb-tense.csv to remove class_feature and define present_a and present_i features. Updated chr-config/verb.yaml to remove <TenseClass> from open_root_template and update tense feature lists.
2. Updated feature acceptors (aspect_morphotactics.csv and dist_morphotactics.csv) to replace [Tense=present] with [Tense=present_a]|[Tense=present_i].
3. Updated parc_macros/generate_inplace_phonology.py to extract tenses without class features, omit TenseClass from alphabet.yaml and phoneme_groups.yaml, and regenerated all grammar assets. FST state count decreased from 940 to 932 states.
4. Updated parse_chr_dict/types.py: eliminated generic present tense; updated VerbForm.matches to support present_a and present_i; moved is_i_present / tense_present_class behavior to VerbMetadata; removed tense_present_class from VerbTemplate; updated LexicalVerb.inflect_form and preserved to_row_dict backward compatibility.
5. Updated parse_chr_dict/derive.py, parse.py, segment.py, reconstruct.py: removed TenseClass parsing and matched hypotheses across forms using aspect_class and present_a/present_i agreement.
6. Updated tests across the entire test suite. All 417 unit and integration tests pass cleanly with zero regressions.
<!-- SECTION:FINAL_SUMMARY:END -->
