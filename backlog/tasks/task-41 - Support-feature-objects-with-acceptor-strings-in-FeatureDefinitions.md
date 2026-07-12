---
id: TASK-41
title: Support feature objects with acceptor strings in FeatureDefinitions
status: Done
assignee: []
created_date: '2026-07-12 22:55'
updated_date: '2026-07-12 22:57'
labels: []
dependencies: []
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Read and parse CSV files in {config_path}/feature_acceptors/ containing feature value to acceptor mappings, and populate them as structured objects in the generated FeatureDefinitions (e.g. prefix_class_features.yaml or verb_features.yaml).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Parse files under config/feature_acceptors/*.csv
- [x] #2 Map feature, acceptor rows to structured objects {name, acceptor} in FeatureDefinitions
- [x] #3 Preserve other string-based feature definitions
- [x] #4 Add/update tests to verify correct generation and validation
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented support for feature objects with acceptor strings parsed from CSV files under config/feature_acceptors/. The generator reads these mappings and outputs them as structured objects containing 'name' and 'acceptor' in the FeatureDefinitions file. Added test coverage validating parsing, generation, and YAML validation.
<!-- SECTION:FINAL_SUMMARY:END -->
