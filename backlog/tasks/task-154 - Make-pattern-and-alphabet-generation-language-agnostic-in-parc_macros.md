---
id: TASK-154
title: Make pattern and alphabet generation language-agnostic in parc_macros
status: Done
assignee:
  - '@agent'
created_date: '2026-09-09 14:32'
updated_date: '2026-09-09 14:51'
labels: []
dependencies: []
ordinal: 164000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor generate_patterns and generate_alphabet in parc_macros/generate_phonology.py to eliminate hardcoded Cherokee tags and patterns. All language-specific tags and patterns must be read from config (slots in verb.yaml, base alphabet.yaml, base phoneme_groups.yaml, and CSVs). Move language-specific patterns (<PrepronominalPrefixes>, <Root>) into chr-config/Phonology/Patterns/phoneme_groups.yaml. Generate morpheme patterns dynamically by iterating over slot TagGroups, and compose <Morpheme> dynamically from slot TagGroups and base alphabet tags.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Move <PrepronominalPrefixes> and <Root> patterns to chr-config/Phonology/Patterns/phoneme_groups.yaml
- [x] #2 Refactor generate_patterns to dynamically build TagGroup patterns from verb_config slots without hardcoding Cherokee names
- [x] #3 Refactor generate_alphabet to dynamically build inventory tag groups from verb_config slots without hardcoding Cherokee names
- [x] #4 Generate <Morpheme> pattern dynamically from slot TagGroups and pre-declared inventory tags
- [x] #5 Verify 100% parity of generated grammar assets, clean YAML validation, and all test suite passes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extract slot tag groups dynamically in extract_phonology_data:
   - Iterate over verb_config['slots'] and their CSV sources.
   - Extract tag values for each TagGroup (e.g. PrefixClass, Pro, AspectClass, Aspect, TenseClass, Tense).
   - Detect variant counts from semicolon-separated cells and populate 'Variant' tags ([Variant=2], etc.).
   - Return generic 'tag_groups: dict[str, list[str]]' and 'slot_tag_groups: list[str]' while retaining existing legacy keys for backward-compatibility.

2. Refactor generate_alphabet to be language-agnostic:
   - Read base alphabet.yaml.
   - Filter out any inventory items whose 'ref' is <TagGroup> for any TagGroup defined in slots.
   - Dynamically append inventory nodes for all slot TagGroups with their tags.

3. Refactor generate_patterns to be language-agnostic:
   - Read base phoneme_groups.yaml.
   - Retain all base patterns from phoneme_groups.yaml (such as <C>, <PrepronominalPrefixes>, <Root>, <H_alt>, <NotLarC>, etc.) except dynamic slot TagGroups and <Morpheme>.
   - Dynamically build regex patterns for each slot TagGroup.
   - Dynamically compose <Morpheme> pattern from all slot TagGroup refs, optional variant tags, and pre-declared inventory tag groups/tags (e.g. <PPP>, <H_alt>, [WI], [DIST], etc.) present in base alphabet.yaml.

4. Clean up any obsolete/transient backwards-compat test cases if applicable, verify 100% parity of generated assets against chr-generated/, and ensure all 136 tests pass.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Eliminated hardcoded Cherokee tags and patterns in parc_macros/generate_phonology.py. Refactored extract_phonology_data, generate_alphabet, and generate_patterns to dynamically build inventory tag groups, TagGroup patterns, and <Morpheme> unions parameterized strictly by verb_config slots and base configuration files. Added comprehensive unit tests and verified 100% clean YAML validation and 137 passing tests across the test suite.
<!-- SECTION:FINAL_SUMMARY:END -->
