---
id: TASK-153
title: Replace resolve_phones_for_pattern with parC fsa in prefix stem shape acceptor
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 13:37'
updated_date: '2026-09-09 13:42'
labels: []
dependencies: []
ordinal: 163000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace custom resolve_phones_for_pattern with parC's fsa function in acceptors.py, supporting multi-phone sequences such as (lh)|(yh) in prefix_class.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Delete resolve_phones_for_pattern from parse_chr_dict/acceptors.py and tests
- [x] #2 Refactor compile_prefix_stem_shape_acceptor to use parC.grammar.acceptor_compilation.fsa directly
- [x] #3 Update tests in tests/test_acceptors.py to validate updated prefix_class patterns
- [x] #4 Verify all tests pass in pytest test suite
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect compile_prefix_stem_shape_acceptor and test_acceptors.py
2. Delete resolve_phones_for_pattern from parse_chr_dict/acceptors.py
3. Update compile_prefix_stem_shape_acceptor to compile patterns with fsa() and compute invalid prefix sequences via pynini
4. Update tests/test_acceptors.py to test the prefix classes and multi-phone patterns
5. Run pytest across the entire suite to verify no regressions
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced bespoke resolve_phones_for_pattern in parse_chr_dict/acceptors.py with parC's built-in fsa and fsm_strings compiler. Updated compile_prefix_stem_shape_acceptor to support multi-phone sequences such as (lh)|(yh) in prefix_class.csv, cleanly constructing disallowed phone prefix automata. Updated test suites across tests/test_acceptors.py, tests/test_clean_generation.py, tests/test_compilation.py, tests/test_config.py, tests/test_segment.py, and tests/test_yaml_validation.py to align with the 8th prefix class (long_stem). Full test suite (136 tests) passing.
<!-- SECTION:FINAL_SUMMARY:END -->
