---
id: TASK-140
title: Clean up legacy trailing-tag phonology markers and update documentation
status: To Do
assignee: []
created_date: '2026-09-06 18:07'
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
- [ ] #1 Remove <LegacyTags> injection and generate_inplace_inventory alias from parc_macros/generate_inplace_phonology.py
- [ ] #2 Regenerate chr-generated/Phonology/Inventory/alphabet.yaml without <LegacyTags>
- [ ] #3 Update README.md to remove references to deleted meta_label_compiler.py and update derive_lexical_features_4step references
- [ ] #4 Verify all tests pass and repository is clean
<!-- AC:END -->
