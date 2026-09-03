---
id: TASK-107
title: >-
  Unify Morphotactic and Stem Acceptors into Cascade Domain and Verify 100%
  Parity
status: Done
assignee:
  - '@subagent'
created_date: '2026-09-03 13:35'
updated_date: '2026-09-03 15:03'
labels:
  - morphotactics
  - fst
  - verification
dependencies:
  - TASK-105
  - TASK-106
priority: high
ordinal: 112000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Compose the compiled cascade domain acceptor (from TASK-106) with the open parse graph inside parse_chr_dict/parse.py with persistent disk caching. Update scratch/verify_roots_compatibility.py to strictly enforce prefix class matching, and verify 100% dictionary parsing parity across all 912 rows (4,738 reference forms) of roots.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update get_parse_graph() in parse_chr_dict/parse.py to compose raw parC parse graph with compile_cascade_domain_acceptor and optimize
- [x] #2 Implement persistent disk caching (.cache/cascade_domain.fst) to ensure instantaneous parse graph startup
- [x] #3 Update scratch/verify_roots_compatibility.py to assert strict prefix_class matching (cfg.prefix_class == exp_prefix) alongside root and aspect_class
- [x] #4 Run verify_roots_compatibility across all 912 rows in roots.csv and achieve 100.0% rows passed (912/912) and 100.0% forms passed (4,738/4,738)
- [x] #5 Verify zero regressions across existing pytest test suites
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. In parse_chr_dict/parse.py, update get_parse_graph() to:
   - Call parC's get_open_parse_graph('verb', infer_lexical_features=True, non_deterministic_cleanup=True).
   - Load or build cascade_domain_acceptor via parse_chr_dict.acceptors with disk caching.
   - Compose raw parse graph with domain acceptor and optimize.
2. In scratch/verify_roots_compatibility.py, update verify_row to assert:
   - root_matches = clean_cfg_root in valid_stems
   - aspect_matches = not exp_aspect or cfg.aspect_class == exp_aspect
   - prefix_matches = not exp_prefix or cfg.prefix_class == exp_prefix
3. Run python scratch/verify_roots_compatibility.py --jobs 8 and verify:
   - All 86 previously failed [DIST] rows pass cleanly.
   - 912 / 912 rows pass (100.0%).
   - 4,738 / 4,738 forms pass (100.0%).
4. Run full pytest suite to verify zero regressions.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Integration Architecture & Verification Gate

### Runtime Composition:
Rather than modifying parC core, parse_chr_dict wraps parC's open parse graph:
PARSE_GRAPH = pynini.compose(raw_parse_graph, cascade_domain_acceptor).optimize()
This filters all illicit morphotactic combinations and invalid stem shapes on output projection.

### Disk Caching:
The composed domain acceptor is cached to disk (.cache/cascade_domain.fst) keyed by config checksums, ensuring zero startup penalty.

### Verification Benchmark:
- Baseline Task 102.6: 826 / 912 rows passed (90.6%), 4,566 / 4,738 forms passed (96.4%). All 86 failures were [DIST] verbs missing imperative/infinitive realizations.
- Target with Task 107: 912 / 912 rows passed (100.0%), 4,738 / 4,738 forms passed (100.0%), with strict prefix_class assertions enabled.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Unified morphotactic and stem-shape acceptors into a composed cascade domain acceptor with persistent disk caching (.cache/cascade_domain.fst). Updated get_parse_graph() in parse_chr_dict/parse.py to compose parC's open parse graph with the cascade domain acceptor, eliminating illicit stem shapes and invalid morphotactic combinations. Updated scratch/verify_roots_compatibility.py with strict prefix class matching. Verified 100.0% parity across all 912 rows (912/912, 100%) and 4,738 reference forms (4,738/4,738, 100%) of roots.csv in 37.17s. All 377 unit tests in the pytest suite pass with zero regressions.
<!-- SECTION:FINAL_SUMMARY:END -->
