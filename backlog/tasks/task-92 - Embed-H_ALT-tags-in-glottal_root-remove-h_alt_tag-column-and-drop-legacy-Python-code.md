---
id: TASK-92
title: >-
  Embed [H_ALT] tags in glottal_root, remove h_alt_tag column, and drop legacy
  Python code
status: Done
assignee:
  - '@myself'
created_date: '2026-08-24 16:53'
updated_date: '2026-08-24 16:57'
labels: []
dependencies: []
ordinal: 91000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update parse_chr_dict and reconstruct.py so glottal_root retains fine-grained [H_ALT] tags, replace grades_are_compatible with root equality check (strip_h_alt_tag(glottal_root) == h_root), remove h_alt_tag column/field from DerivationHypothesis and roots.csv, and delete legacy Python H-alternation code in h_alternation.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 glottal_root retains [H_DROP]/[H_GLOT]/[H_LAT] tags from parsing
- [x] #2 Root compatibility checks strip_h_alt_tag(glottal_root) == h_root
- [x] #3 Remove h_alt_tag from DerivationHypothesis, parse_chr_dict/__main__.py, and roots.csv
- [x] #4 Drop legacy Python string manipulation and grades_are_compatible from h_alternation.py
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Clean up parse_chr_dict/h_alternation.py: remove legacy Python functions, add strip_h_alt_tags, keep trigger validation helpers.\n2. Update DerivationHypothesis in meta_label_compiler.py: remove h_alt_tag field, keep glottal_root with tags.\n3. Update derive_hypotheses_for_forms: check strip_h_alt_tags(p_root) == hyp.h_root on glottal forms.\n4. Update reconstruct.py: inflect glottal forms with hyp.glottal_root directly.\n5. Update parse_chr_dict/__main__.py: remove h_alt_tag from roots_writer fieldnames.\n6. Update tests in tests/test_meta_label_compiler.py and test_h_alternation.py.\n7. Verify test suite and complete DoD.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Dropped legacy Python H-alternation string manipulation and compatibility functions in favor of config-driven FST and strip_h_alt_tags equality. Embedded fine-grained [H_ALT] tags directly in glottal_root without extra columns/fields in DerivationHypothesis and roots.csv. Updated reconstruct.py to inflect glottal forms directly with glottal_root. Verified all unit tests pass (344 passed).
<!-- SECTION:FINAL_SUMMARY:END -->
