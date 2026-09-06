---
id: TASK-7
title: >-
  Create pipeline folders and generate paradigm/conjugation class configs from
  test.csv
status: Done
assignee:
  - '@myself'
created_date: '2026-07-04 20:19'
updated_date: '2026-07-04 20:21'
labels: []
dependencies: []
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design and implement the generating pipeline with spanish-reference, spanish-base, spanish-config, and spanish-generated folders. Parse metadata and rows in test.csv to generate FeatureMarkers, Paradigms (e.g. verb_a_stem_present.yaml), and conjugation_classes in FeatureDefinitions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create 4 folders: spanish-reference (copy of reference grammar), spanish-base (base grammar sans generated files), spanish-config (custom macro config/test.csv), spanish-generated (target folder generated from base and config)
- [x] #2 Generate FeatureMarkers (verb_a_stem.yaml, etc.) from test.csv
- [x] #3 Generate Paradigms (verb_a_stem_present.yaml, etc.) from test.csv
- [x] #4 Generate conjugation_classes list in FeatureDefinitions (verb_features.yaml) from test.csv paradigm names
- [x] #5 Ensure tests pass and validate generated YAML files against schemas
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Copy spanish-colang to spanish-reference to establish the reference grammar folder.\n2. Copy spanish-colang to spanish-base, removing the generated files (verb_a_stem.yaml, verb_e_stem.yaml, verb_i_stem.yaml under Exponence/FeatureMarkers, and verb_a_stem_present.yaml, verb_e_stem_present.yaml, verb_i_stem_present.yaml under Morphotactics/Paradigm), and strip the generated conjugation classes (a_stem, e_stem, i_stem) from Exponence/FeatureDefinitions/verb_features.yaml, keeping only 'diphthong'.\n3. Create spanish-config folder and place test.csv there with additional metadata comments to define the generation parameters for the paradigms (tense, mood, part_of_speech).\n4. Update parc_macros/generate_markers.py to:\n   - Copy the spanish-base folder to spanish-generated folder.\n   - Parse test.csv from spanish-config including the new paradigm metadata comments.\n   - Generate the FeatureMarkers under spanish-generated.\n   - Generate the Paradigms (e.g. verb_a_stem_present.yaml) under spanish-generated.\n   - Update Exponence/FeatureDefinitions/verb_features.yaml in spanish-generated to append the new conjugation classes (a_stem, e_stem, i_stem) to the 'conjugation_class' list.\n5. Update tests to validate that spanish-generated matches spanish-reference exactly, and run the validation checks on all generated YAML files.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created the four pipeline folders (spanish-reference, spanish-base, spanish-config, and spanish-generated). Modified generate_markers.py to copy spanish-base to spanish-generated, parse custom metadata comments in test.csv, generate FeatureMarkers, generate Paradigms (e.g. verb_a_stem_present.yaml), and update conjugation_class list in FeatureDefinitions/verb_features.yaml. Added tests to verify semantic equivalence against reference grammar.
<!-- SECTION:FINAL_SUMMARY:END -->
