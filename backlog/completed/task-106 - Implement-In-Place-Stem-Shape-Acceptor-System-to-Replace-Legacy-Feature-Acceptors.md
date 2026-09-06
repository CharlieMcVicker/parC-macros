---
id: TASK-106
title: >-
  Implement In-Place Stem-Shape Acceptor System to Replace Legacy Feature
  Acceptors
status: Done
assignee:
  - '@subagent'
created_date: '2026-09-03 13:35'
updated_date: '2026-09-03 14:55'
labels:
  - morphotactics
  - phonology
  - fst
dependencies: []
priority: high
ordinal: 111000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement deterministic acceptor compilers for morphotactic licensing and anchored stem-shape constraints in parse_chr_dict/acceptors.py. Compile feature_acceptors/prefix_class.csv into an anchored linear template acceptor ([PrefixClass=c]<Pro><H_ALT>?<AllowedInitialPhone>) and feature_acceptors/morphotactics.csv into a licensing acceptor, eliminating illicit parses (such as [PrefixClass=a_stem] with consonant-initial stems) without Cartesian state explosion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Audit and maintain chr-inplace-config/feature_acceptors/prefix_class.csv for all 7 prefix classes (a_stem, cons_stem, v_stem, e_stem, k_a_stem, vowel_stem, r_stem)
- [x] #2 Implement compile_morphotactic_acceptor in parse_chr_dict/acceptors.py reading feature_acceptors/morphotactics.csv to enforce trigger => licensed constraints over the template alphabet
- [x] #3 Implement compile_prefix_stem_shape_acceptor in parse_chr_dict/acceptors.py anchoring [PrefixClass=c] across <Pro><H_ALT>? to root-initial phonemes
- [x] #4 Implement compile_cascade_domain_acceptor combining morphotactic and stem-shape acceptors with [BOW] and [EOW] wrapping
- [x] #5 Verify that invalid combinations (e.g. [PrefixClass=a_stem] before consonant root 'that', or [DIST=di] with [Tense=present]) are pruned with minimal state footprint
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit chr-inplace-config/feature_acceptors/prefix_class.csv to ensure exact phone patterns: a_stem (a), cons_stem (<C>), v_stem (v), e_stem (e), k_a_stem (a), vowel_stem (<V>), r_stem (<Son>|<N>).
2. Create parse_chr_dict/acceptors.py containing deterministic FST compiler functions:
   - compile_morphotactic_acceptor(syms, alphabet, rules_csv): constructs DFA enforcing trigger => licensed tokens over template strings.
   - compile_prefix_stem_shape_acceptor(syms, alphabet, rules_csv): constructs anchored DFA matching [PrefixClass=c]<Pro><H_ALT>?<PhoneConstraint>.
   - compile_cascade_domain_acceptor(syms, alphabet): intersects morphotactic and stem-shape acceptors and wraps with [BOW]...[EOW][rules=+]?.
3. Add unit tests in tests/test_acceptors.py verifying that illicit template strings fail acceptance and valid strings pass.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes & Architecture

### Anchored Stem Shape:
In the linear in-place template:
<PrepronominalPrefixes><PrefixClass><Pro><H_ALT>?<Root><AspectClass><Aspect><TenseClass><Tense>
The PrefixClass slot is separated from Root only by Pro and optional H_ALT.
The stem-shape acceptor enforces that each [PrefixClass=c] is immediately followed by a valid pronominal tag, optional H-tag, and the appropriate root-initial phoneme:
Union_c ( [PrefixClass=c] . <Pro> . (<H_ALT>)? . PhonemeConstraint_c )
This requires only ~12-16 states and operates purely as a template-level regular language filter.

### Solves TASK-108:
This cleanly resolves the issue flagged in TASK-108:
'[PrefixClass=a_stem][Pro=3sg.A][H_DROP]that'
Under this acceptor, 'a_stem' requires initial 'a', immediately pruning the hypothesis with consonant-initial root 'that'.

### Pure Functional Design:
Compilers take symbol table and alphabet blueprints as parameters and return optimized deterministic pynini.Fst objects with zero external mutations.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented deterministic FST compiler functions in parse_chr_dict/acceptors.py for in-place morphotactic licensing, anchored prefix stem-shape constraints, and cascade domain acceptors. Audited and cleaned chr-inplace-config/feature_acceptors/prefix_class.csv to declare exact phoneme sets across all 7 prefix classes (a_stem -> 'a', v_stem -> 'v', e_stem -> 'e', k_a_stem -> 'a', vowel_stem -> <V>, cons_stem -> <C>, r_stem -> <Son>|<N>). Created compile_morphotactic_acceptor (17 states) and compile_prefix_stem_shape_acceptor (19 states) which operate with tiny state footprints (~15-35 states) and eliminate illicit parses (such as [PrefixClass=a_stem] before consonant root 'that' or [DIST=di] with [Tense=present]). Added comprehensive unit tests in tests/test_acceptors.py; all 375 tests in the test suite pass.
<!-- SECTION:FINAL_SUMMARY:END -->
