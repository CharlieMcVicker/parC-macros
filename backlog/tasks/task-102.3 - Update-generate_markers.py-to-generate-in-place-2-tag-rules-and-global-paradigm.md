---
id: TASK-102.3
title: >-
  Update generate_markers.py to generate in-place 2-tag rules and global
  paradigm
status: In Progress
assignee:
  - '@subagent'
created_date: '2026-09-02 19:51'
updated_date: '2026-09-02 20:34'
labels: []
dependencies:
  - TASK-102.2
modified_files:
  - parc_macros/generate_morpheme_replace_rules.py
  - parc_macros/generate_markers.py
  - parc_macros/schemas/Paradigm.json
  - tests/conftest.py
  - tests/test_inplace_markers_generation.py
parent_task_id: TASK-102
priority: high
type: enhancement
ordinal: 104000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enhance parc_macros/generate_markers.py and generate_morpheme_replace_rules.py to generate in-place adjacent 2-tag string_map rules for pronominal, aspect, and tense slots, and generate a lean unified Paradigm using global_markers without ContingentFeatureMarkers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Support generating in-place 2-tag string_map rules ([PrefixClass=...][Pro=...], [AspectClass=...][Aspect=...], [TenseClass=...][Tense=...])
- [x] #2 Support generating Paradigm YAML with stage-ordered global_markers
- [x] #3 Ensure backwards compatibility with standard trailing-label configs
- [x] #4 Verify generated YAML configs pass JSON schema validation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement is_in_place_mode detector supporting open_root_template pattern detection and verb.yaml configuration.
2. Update generate_morpheme_replace_rules.py to generate in-place 2-tag string_map rules ([PrefixClass=...][Pro=...], [AspectClass=...][Aspect=...], [TenseClass=...][Tense=...]) when in in-place mode, preserving legacy behavior otherwise.
3. Update generate_markers.py to generate Paradigm YAML with stage-ordered global_markers and without ContingentFeatureMarkers in in-place mode.
4. Update parc_macros/schemas/Paradigm.json to support in-place paradigms (global_markers, open_root_template, optional feature_markers).
5. Ensure conftest sets default absolute YAML_DIR for seamless test execution across all environments.
6. Add comprehensive unit tests in tests/test_inplace_markers_generation.py covering 2-tag rules, global paradigm generation, backwards compatibility, and schema validation.
7. Verify all 351+ tests pass and commit incrementally.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
### Overview
Implemented support for generating in-place 2-tag replacement rules and global paradigm definitions directly from CSV data tables for Cherokee verb grammar optimization.

### Changes
1. **In-place 2-tag Rule Generation** (`parc_macros/generate_morpheme_replace_rules.py`):
   - Added automatic detection of in-place mode via `is_in_place_mode(config)` (checking `verb.yaml` in-place flag and `open_root_template` tag indicators).
   - Added `_generate_inplace_rules` that compiles adjacent 2-tag `string_map` rules (`[PrefixClass=...][Pro=...]`, `[AspectClass=...][Aspect=...]`, `[TenseClass=...][Tense=...]`) mapped directly from CSV rows and columns.
   - Preserved `_generate_legacy_rules` for 100% backwards compatibility when in trailing-label mode.

2. **Global Paradigm Generation** (`parc_macros/generate_markers.py`):
   - Added `generate_inplace_paradigm_config` to generate a lean Paradigm YAML using stage-ordered `global_markers` without `ContingentFeatureMarkers`.
   - Supports explicit `global_markers` from `verb.yaml` as well as automatic derivation from `stage_order` and phonological/morpheme rule definitions.
   - Preserved existing `generate_contingent_configs` and `generate_paradigm_configs` for trailing-label workflows.
   - Added programmatic entrypoint `generate_markers(config_path, output_dir, in_place=...)` and CLI `--in-place` flag.

3. **Schema Validation & Test Infrastructure**:
   - Updated `parc_macros/schemas/Paradigm.json` to properly validate in-place paradigms with `global_markers` and `open_root_template`.
   - Added `tests/conftest.py` ensuring `sys.path` and `YAML_DIR` defaults are properly configured for test execution.
   - Added unit test suite `tests/test_inplace_markers_generation.py` covering 2-tag rule generation, paradigm generation, backwards compatibility, and JSON schema validation.
   - Verified that all 358 tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
