---
id: TASK-140
title: Clean up legacy trailing-tag phonology markers and update documentation
status: Done
assignee:
  - '@subagent-140'
created_date: '2026-09-06 18:07'
updated_date: '2026-09-08 12:44'
labels: []
dependencies: []
priority: low
type: chore
ordinal: 150000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove <LegacyTags> injection ([Pro], [Aspect], [Tense]) and generate_inplace_inventory alias from parc_macros/generate_inplace_phonology.py, regenerate alphabet.yaml, and update README.md to remove references to deleted modules and outdated function names.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove <LegacyTags> injection and generate_inplace_inventory alias from parc_macros/generate_inplace_phonology.py
- [x] #2 Regenerate chr-generated/Phonology/Inventory/alphabet.yaml without <LegacyTags>
- [x] #3 Update README.md to remove references to deleted meta_label_compiler.py and update derive_lexical_features_4step references
- [x] #4 Verify all tests pass and repository is clean
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove LegacyTags injection and generate_inplace_inventory alias from parc_macros/generate_inplace_phonology.py\n2. Regenerate chr-generated/Phonology/Inventory/alphabet.yaml using python parc_macros/generate_inplace_phonology.py\n3. Update README.md to remove deleted meta_label_compiler.py references and update derive_lexical_features_4step references\n4. Run pytest test suite and verify clean git status
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed <LegacyTags> injection ([Pro], [Aspect], [Tense]) and generate_inplace_inventory alias from parc_macros/generate_inplace_phonology.py, updating parc_macros/generate_markers.py to use generate_inplace_alphabet directly. Cleaned up legacy trailing-tag marker [Pro] from left_context in chr-config/Phonology/Rules/h_alternation.yaml and regenerated chr-generated/ grammar assets (including alphabet.yaml without <LegacyTags>). Updated README.md to remove all references to deleted meta_label_compiler.py and test_meta_label_compiler.py, documented active modules and test suites, and updated derivation engine references to derive_hypotheses_for_forms (noting derive_lexical_features_4step as a backwards compatibility wrapper). Updated test_inplace_config.py tag count expectation (135 tags). Verified that all 129 pytest unit tests pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
