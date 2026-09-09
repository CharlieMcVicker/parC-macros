---
id: TASK-151
title: Implement h-metathesis phonology rules and patterns
status: In Progress
assignee:
  - '@agent'
created_date: '2026-09-08 19:02'
updated_date: '2026-09-08 19:59'
labels: []
dependencies: []
ordinal: 161000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement h-metathesis phonological rewrite rules in chr-config/Phonology/Rules/h_metathesis.yaml and supporting phoneme groups in chr-config/Phonology/Patterns/phoneme_groups.yaml to support leftward h-movement across consonants to the preceding vowel (e.g. kanho -> khano).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define <NotLarC> pattern in phoneme_groups.yaml to represent non-laryngeal consonants without hardcoding phone sets in rules
- [x] #2 Update h_metathesis.yaml to correctly move h leftward before the preceding vowel
- [x] #3 Validate YAML assets and verify rule compilation
- [x] #4 Create tests/test_h_metathesis.py with parameterized test cases for easy editing
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add <NotLarC> pattern to chr-config/Phonology/Patterns/phoneme_groups.yaml to represent non-laryngeal consonants cleanly without hardcoding phone sets.\n2. Update chr-config/Phonology/Rules/h_metathesis.yaml using <NotLarC> for intervening consonants and <V> for vowels.\n3. Validate rules via yaml_validation.py and verify phonological rewrite behaviour.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Moved <H_metathesis> to the right side of slot:pronominal in chr-config/verb.yaml. Eliminated [TEMP_META_VOWEL] and [TEMP_META_H_INS] completely. Stage 1 directly tags [TEMP_META_H_DEL] and drops [H_metathesis=...] tags immediately. Stage 2 inserts h before <V><NotLarC>*[TEMP_META_H_DEL]<V> and deletes [TEMP_META_H_DEL]. All tests in tests/test_h_metathesis.py pass.
<!-- SECTION:NOTES:END -->
