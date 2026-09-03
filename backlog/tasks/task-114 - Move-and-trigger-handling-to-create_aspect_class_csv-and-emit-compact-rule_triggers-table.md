---
id: TASK-114
title: >-
  Move * and @ trigger handling to create_aspect_class_csv and emit compact
  rule_triggers table
status: Done
assignee:
  - '@agent'
created_date: '2026-09-03 18:29'
updated_date: '2026-09-03 18:38'
labels: []
dependencies:
  - TASK-112
priority: high
type: enhancement
ordinal: 124000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor Cherokee rule trigger handling to maintain clean separation of concerns, language agnosticism, and pure value-driven configuration without low-level symbols or redundant form columns:
1. In parse_chr_dict/create_aspect_class_csv.py, parse Cherokee dictionary notation (* for drop_final, @ for drop_final_two) from chr-data/classes.csv.
2. Emit a clean verb-aspect.csv containing strictly phonological morphemes without * or @ symbols.
3. Emit a compact value-driven effect table (e.g. aspect_effects.csv or rule_effects.csv) with columns (aspect_class, aspect, variant, effect). Omit the 'form' column to eliminate redundancy with verb-aspect.csv.
4. Update parc_macros to consume this value-driven table generically: it groups entries by 'effect' and maps feature coordinates into slot contexts without knowing about Cherokee notation or low-level symbol syntax.
5. Verify 100% parity across generated YAMLs and parC FST compilation (983 states).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 create_aspect_class_csv.py parses * and @ from chr-data/classes.csv and outputs clean verb-aspect.csv without * or @ characters
- [x] #2 Verify 100% parity across generated YAMLs and FST compilation
- [x] #3 create_aspect_class_csv.py outputs a compact, value-driven effect table (aspect_class, aspect, variant, effect) omitting redundant morpheme forms
- [x] #4 parc_macros is completely language-agnostic: contains zero references to * or @ and derives rule contexts generically from the effect table
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update parse_chr_dict/create_aspect_class_csv.py to emit clean verb-aspect.csv (no * or @) and emit aspect_effects.csv with columns (aspect_class, aspect, variant, effect).
2. Generate updated verb-aspect.csv and aspect_effects.csv in chr-clean-inplace-config.
3. Update parc_macros/generate_inplace_phonology.py and generate_morpheme_replace_rules.py to read aspect_effects.csv / rule_effects.csv generically, removing Cherokee-specific * and @ parsing from parc_macros.
4. Verify complete parity against chr-inplace-generated (983 states) and run test suite.
5. Check all acceptance criteria and close task.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored rule trigger handling to maintain pure separation of concerns and value-driven configuration. parse_chr_dict/create_aspect_class_csv.py handles * and @ symbols from chr-data/classes.csv, outputting clean verb-aspect.csv and compact aspect_effects.csv (aspect_class, aspect, variant, effect). parc_macros/generate_inplace_phonology.py consumes aspect_effects.csv generically. Verified 100% test pass and FST compilation parity (983 states).
<!-- SECTION:FINAL_SUMMARY:END -->
