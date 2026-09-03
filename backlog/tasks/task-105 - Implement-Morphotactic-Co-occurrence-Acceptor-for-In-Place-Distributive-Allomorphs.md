---
id: TASK-105
title: >-
  Implement Morphotactic Co-occurrence Acceptor for In-Place Distributive
  Allomorphs
status: To Do
assignee: []
created_date: '2026-09-03 13:32'
updated_date: '2026-09-03 13:36'
labels:
  - morphotactics
  - fst
dependencies: []
priority: high
ordinal: 110000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a morphotactic co-occurrence constraint system on the in-place template domain FST before phonological rule stages apply. Specifically, resolve the allomorphy between Cherokee distributive prefix variants ([DIST=de] vs [DIST=di]) by constraining [DIST=di] to co-occur only with non-indicative tenses ([Tense=immediate], [Tense=infinitive]) and [DIST=de] with indicative tenses, keeping phonological insertion rules 100% local.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define [DIST=de] and [DIST=di] in alphabet inventory and pattern groups
- [ ] #2 Implement early template-level morphotactic co-occurrence acceptor FST to constrain [DIST=de] with indicative tenses and [DIST=di] with immediate/infinitive tenses before phonological rules
- [ ] #3 Update insert_di1 to locally rewrite [DIST=de] and insert_di2 to locally rewrite [DIST=di] without nonlocal right_context lookahead
- [ ] #4 Update InPlaceParseConfig and read_inplace_parse to map both tags to [DIST] for backwards compatibility with roots.csv
- [ ] #5 Verify 100% compatibility across all 912 rows in roots.csv and zero regressions across pytest suite
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Context & Linguistic Design

### Linguistic Rationale:
In Cherokee, the prepronominal distributive prefix alternates between two allomorphs:
1. 'de-' (indicative forms: present, habitual, future progressive, assertive, reported)
2. 'di-' (non-indicative forms: immediate imperative, infinitive)

Critically, in 2nd person indicative forms (e.g. 'you are doing it'), the sequence is 'te-hi-' (from 'de-' + 'hi-'), whereas in the imperative ('do it!') the sequence is 'th-' ('thiyohi', from 'di-' + 'hi-'). Because both face the identical phonological following context ('hi-'), the choice of allomorph is strictly conditioned by mood/tense, NOT phonology.

### Architecture: Early Non-local Morphotactic Acceptor
Instead of a complex, unbounded context-dependent phonological rewrite (cdrewrite) across the stem and suffixes:
1. Define distinct in-place tags: [DIST=de] and [DIST=di] in <PrepronominalPrefixes>.
2. Intersect a minimal 3-state morphotactic co-occurrence acceptor directly onto the template domain FST before phonological stages run:
   - [DIST=de] requires [Tense=present | habitual | future_prog | assertive | reported]
   - [DIST=di] requires [Tense=immediate | infinitive]
   - Absence of [DIST] allows any [Tense]
3. Because the template string is at its shortest and has no phonological alternations, this acceptor adds only ~4-6 states to the template domain without Cartesian explosion.

### Local Insertion Phonology:
- insert_di1 locally rewrites [DIST=de]: [DIST=de]i -> t, [DIST=de] before <V> -> t, default [DIST=de] -> te
- insert_di2 locally rewrites [DIST=di]: [DIST=di]a/i -> ti, [DIST=di] before 'h' -> t (yields th-), [DIST=di] before <V> -> ts (yields tsu-), default [DIST=di] -> ti
- Zero right_context lookahead is needed in phonology.

### Backwards Compatibility:
In parse_chr_dict/parse.py, read_inplace_parse maps both [DIST=de] and [DIST=di] to [DIST] in InPlaceParseConfig.canonical_root, ensuring 100% compatibility with roots.csv.
<!-- SECTION:NOTES:END -->
