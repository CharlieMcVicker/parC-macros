---
id: TASK-106
title: >-
  Implement In-Place Stem-Shape Acceptor System to Replace Legacy Feature
  Acceptors
status: To Do
assignee: []
created_date: '2026-09-03 13:35'
updated_date: '2026-09-03 13:36'
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
Re-implement the feature acceptor system in the in-place architecture. In place of legacy Cartesian loops over external features in _apply_feature_acceptor_constraints, compile local stem-shape constraint acceptors on the in-place template domain that filter the initial/final phonemes of <Root> based on <PrefixClass> (e.g. a_stem requires initial 'a', cons_stem requires initial consonant, etc.) and <AspectClass>. Migrate feature_acceptors/prefix_class.csv into this in-place constraint layer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Design in-place stem constraint schema/representation for prefix_class and aspect_class
- [ ] #2 Migrate feature_acceptors/prefix_class.csv into the in-place constraint format
- [ ] #3 Compile stem-initial constraint acceptor that restricts <Root> based on [PrefixClass=...] locally without Cartesian feature explosion
- [ ] #4 Verify that invalid prefix-class/root combinations are pruned early in the template domain
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Context & Stem-Shape System Design

### Problem with Legacy Feature Acceptors:
In the baseline system, feature acceptors were defined in 'feature_acceptors/prefix_class.csv':
- a_stem: <Morpheme>*a<Phone>*<Morpheme>*
- cons_stem: <Morpheme>*<C><Phone>*<Morpheme>*
- v_stem: <Morpheme>*v<Phone>*<Morpheme>*
- e_stem: <Morpheme>*e<Phone>*<Morpheme>*
- k_a_stem: <Morpheme>*a<Phone>*<Morpheme>*
- r_stem: <Morpheme>*(<Son>|<N>)<Phone>*<Morpheme>*
- vowel_stem: <Morpheme>*<V><Phone>*<Morpheme>*

In parC, _apply_feature_acceptor_constraints() enforced these by running a Cartesian loop over every lexical combo and intersecting each root FSA with the feature acceptor, which contributed directly to the 578k-state explosion. During the in-place rewrite, we pruned external feature definitions, temporarily losing this stem-shape filtering.

### In-Place Reimplementation:
In the in-place template:
<PrepronominalPrefixes><PrefixClass><Pro><H_ALT>?<Root><AspectClass><Aspect><TenseClass><Tense>
1. [PrefixClass=...] sits directly adjacent to <Pro><H_ALT>?<Root>.
   - A local template constraint acceptor can immediately check that the initial phoneme of <Root> matches the prefix class requirements (e.g. a_stem requires initial 'a', cons_stem requires initial consonant).
2. [AspectClass=...] sits directly adjacent to the end of <Root>.
   - Any stem-final requirements imposed by aspect classes can likewise be checked locally.
3. Because these constraints run directly on the template domain FST, they eliminate invalid stem/class combinations upfront before any phonological rewrite stages run, keeping FST compilation fast and lean.
<!-- SECTION:NOTES:END -->
