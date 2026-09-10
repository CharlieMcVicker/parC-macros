---
id: TASK-171
title: Make phonology rule generation language-agnostic in parc_macros
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 17:29'
updated_date: '2026-09-10 17:31'
labels: []
dependencies: []
ordinal: 181000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove hardcoded Cherokee-specific vowels (a, v), rule fallbacks, and tag triggers from parc_macros/generate_phonology.py and parc_macros/generate_morpheme_replace_rules.py. Parameterize phonology rule triggers purely through verb.yaml and config CSV tables.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove hardcoded Cherokee vowels ('a', 'v') and tag triggers ([PrefixClass=a_stem][Pro=3sg.A], etc.) from parc_macros/generate_phonology.py
- [x] #2 Ensure stem-initial vowel dropping and other phonological effects are driven generically from phonology_effects config in verb.yaml
- [x] #3 Make class acceptor loading in parc_macros/generate_morpheme_replace_rules.py generic without hardcoded column names
- [x] #4 All pytest tests pass and generated files in chr-generated remain valid and verified
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Made phonology rule generation language-agnostic in parc_macros: parameterized stem-initial vowel dropping dynamically from phonology_effects (e.g. drop_stem_initial_<vowel> / drop_stem_initial_vowels) without hardcoded Cherokee vowels or triggers, made _load_class_acceptors generic with header skipping, regenerated all grammar YAML assets in chr-generated, and verified full test suite passes cleanly with 160 tests.
<!-- SECTION:FINAL_SUMMARY:END -->
