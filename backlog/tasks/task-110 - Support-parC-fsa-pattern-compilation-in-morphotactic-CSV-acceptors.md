---
id: TASK-110
title: Support parC fsa pattern compilation in morphotactic CSV acceptors
status: Done
assignee:
  - '@myself'
created_date: '2026-09-03 15:58'
updated_date: '2026-09-03 16:01'
labels: []
dependencies: []
ordinal: 115000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use parC's fsa and fsm_strings in compile_morphotactic_acceptor to support pattern expressions (such as alternations '|' and class/pattern references like '<H_alt>') in both trigger and licensed columns of morphotactic CSVs, and simplify pro_morphotactics.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update compile_morphotactic_acceptor in parse_chr_dict/acceptors.py to evaluate pattern expressions via parC fsa and fsm_strings
- [x] #2 Simplify chr-inplace-config/feature_acceptors/pro_morphotactics.csv to use [Pro=1sg.A]|[Pro=1sg>3sg]|[Pro=2sg>3sg],H_alt,<H_alt>
- [x] #3 Ensure '*' elsewhere fallback continues to correctly restrict unmentioned triggers
- [x] #4 Verify all 392 tests across the test suite continue to pass cleanly
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. In parse_chr_dict/acceptors.py, import fsa and fsm_strings from parC.grammar.acceptor_compilation.
2. In compile_morphotactic_acceptor, use fsm_strings(fsa(...)) to expand trigger patterns (including alternations like [Pro=1sg.A]|[Pro=1sg>3sg]|[Pro=2sg>3sg]) and target licensed patterns (including class refs like <H_alt>).
3. Simplify chr-inplace-config/feature_acceptors/pro_morphotactics.csv to the 2-row pattern with [Pro=1sg.A]|[Pro=1sg>3sg]|[Pro=2sg>3sg],H_alt,<H_alt> and *,H_alt,[H_alt=none].
4. Run tests/test_acceptors.py and the full pytest suite to verify all 392 tests pass cleanly.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored compile_morphotactic_acceptor in parse_chr_dict/acceptors.py to compile trigger, target_slot, and licensed pattern expressions directly using parC's fsa. Replaced string manipulation with native FST operations: unlicensed targets are computed via pynini.difference(target_slot_fsa, licensed_fsa), and elsewhere (*) triggers are computed via pynini.difference(all_trigger_fsa, explicit_triggers_fsa). Simplified pro_morphotactics.csv to a concise 2-row specification: [Pro=1sg.A]|[Pro=1sg>3sg]|[Pro=2sg>3sg],H_alt,<H_alt> and *,H_alt,[H_alt=none]. Verified with all 392 unit and integration tests passing cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
