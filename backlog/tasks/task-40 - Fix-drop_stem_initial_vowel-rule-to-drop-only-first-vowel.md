---
id: TASK-40
title: Fix drop_stem_initial_vowel rule to drop only first vowel
status: Done
assignee:
  - '@agent'
created_date: '2026-07-12 04:05'
updated_date: '2026-07-12 04:15'
labels: []
dependencies: []
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure the drop_stem_initial_vowel rule in drop_stem_initial_vowel.yaml drops only the first 'a' or 'v' of a stem, avoiding subsequent deletions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Configure drop_stem_initial_vowel.yaml to target only the first occurrence of a or v
- [x] #2 Ensure all unit tests pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified the issue where cdrewrite was deleting all adjacent initial vowels. Refactored drop_stem_initial_vowel.yaml to use a two-step rule sequence mapping vowels to a temporary tag [TEMP] first, and then deleting the tag. Registered [TEMP] in alphabet.yaml.

Resolved models.py mismatch where RuleSequence name resolution failed with list index out of range/KeyError because the '$' prefix was not stripped during YAML loading of rule_sequence. Refactored resolve_rule in models.py.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored drop_stem_initial_vowel rule to drop only the first vowel of a stem by using a temporary tag to mark and delete it sequentially, preventing subsequent vowel deletions. Registered the new tag in the inventory configuration.

Additionally resolved a schema mismatch by patching parC's resolve_rule to properly convert YAML's rule_sequence to python's rules field and strip '$' prefixes.
<!-- SECTION:FINAL_SUMMARY:END -->
