---
id: TASK-51
title: Diagnose and test two-stage optional morpheme rule strategy (DIST/WI/NI)
status: Done
assignee:
  - '@agent'
created_date: '2026-07-16 23:12'
updated_date: '2026-07-16 23:22'
labels: []
dependencies: []
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current strategy for optional morphemes (DIST, WI, NI) uses a two-stage approach: (1) add_X stage inserts a dummy token [DIST]/[WI]/[NI] unconditionally for both + and - feature values; (2) insert_X stage does a context-sensitive rewrite to either realize the morpheme (for +) or drop the token (for -). This strategy is causing the state space to collapse. This task involves creating a minimal self-contained test that isolates this behavior pattern, running it to observe the failure mode, and diagnosing the root cause.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create a minimal parC grammar config that reproduces the two-stage dummy-token strategy
- [x] #2 Write unit tests that test all combinations of the optional feature being + and -
- [x] #3 Run the tests and capture the failure output
- [x] #4 Identify the root cause of the state space collapse
- [x] #5 Document the diagnosis in the task notes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Diagnosis

### Root Cause: Epsilon Insertion + Kleene-Star Domain = Cyclic FST

The two-stage dummy-token strategy fails because of an interaction between:

1. The 'add_X' rules use cdrewrite with epsilon insertion:
   - string_map: [("", "[DIST]")] means "insert [DIST] at every position"  
   - left_context: "#" restricts insertion to word boundary
   - This creates a cdrewrite(""→"[DIST]", "#", "{^[DIST]}") transducer

2. The stage cascade's trigger_fsa uses a Kleene-star domain:
   - stems_domain_acceptor = (phone | boundary | word_edge)*
   - This is a cyclic (infinite-path) acceptor

3. When trigger_fsa (cyclic) is composed with the epsilon-insertion cdrewrite transducer:
   - The composition produces an infinite/cyclic FST
   - When .optimize() is called on this cyclic composition, pynini cannot enumerate paths
   - The overall gated_fst becomes degenerate

4. The _compile_stage_cascade function then composes cascade_domain with the degenerate gated_fst, yielding zero paths after optimization.

### Evidence
- Direct application of add_PRE to a bare word_fsa works correctly: [BOW]stem[EOW] → [BOW][PRE]stem[EOW]
- The tag_domain, constraint_fsas, and trigger_tags all look correct (4 valid combos, correct constraints)
- The trigger_fsa (stems_domain_acceptor · trigger_tags) composes correctly with add_PRE to produce a cyclic/infinite FST  
- The error message 'PathIterator: Cyclic FSTs have an infinite number of paths' appears when trying to inspect this composed FST
- All 4 inflectional combinations produce empty output ([] results)

### The Fundamental Mismatch
The stage cascade was designed for 'suffix' and 'prefix' markers of the form:
  kind: suffix, value: "pre"  (inserts a fixed string at word boundary)
The cdrewrite for these markers is compiled differently - they operate on [BOW] directly.

But the two-stage strategy uses rules as markers, which produces a different composition chain that interacts badly with the Kleene-star-shaped trigger domain.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created a minimal self-contained parC grammar config in minimal-optional-test/ that exactly mirrors the DIST/WI/NI two-stage dummy-token strategy. Wrote unit tests in tests/test_optional_morpheme_strategy.py. Ran diagnostics to pinpoint the root cause.

ROOT CAUSE: The add_X rules use epsilon insertion via cdrewrite("","[X]","#","{^[X]}"). The stage cascade in paradigm_compilation.py builds a trigger_fsa = stems_domain_acceptor · trigger_tags, where stems_domain_acceptor is a Kleene-star acceptor (phone|boundary|word_edge)*. Composing a Kleene-star acceptor with an epsilon-insertion cdrewrite transducer produces a cyclic/infinite-path FST. When pynini optimizes the subsequent cascades, the composition collapses to 0 states (empty FST) at stage 2, making all inflectional combinations produce empty output.

EVIDENCE: The compose log shows '6=>(after stage 1) 0 states/arcs' immediately after stage 2 — complete state collapse. Directly listing paths on the trigger·add_PRE composition raises 'PathIterator: Cyclic FSTs have an infinite number of paths'. Individual rules (add_PRE, drop_PRE, insert_PRE) work correctly on bare word_fsa inputs.

TESTS: 5 passing / 4 xfailed (all correctly documenting the broken state).
<!-- SECTION:FINAL_SUMMARY:END -->
