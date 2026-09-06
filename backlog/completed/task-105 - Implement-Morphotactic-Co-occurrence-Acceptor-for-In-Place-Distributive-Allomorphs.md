---
id: TASK-105
title: >-
  Implement Morphotactic Co-occurrence Acceptor for In-Place Distributive
  Allomorphs
status: Done
assignee:
  - '@subagent'
created_date: '2026-09-03 13:32'
updated_date: '2026-09-03 14:46'
labels:
  - morphotactics
  - fst
dependencies: []
priority: high
ordinal: 110000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement declarative morphotactic co-occurrence licensing in chr-inplace-config and resolve Cherokee distributive allomorphy ([DIST=de] vs [DIST=di]). Merge insertion rules into a unified insert_di.csv (# rule: insert_DIST, # stage: insert_DIST) to resolve the remaining 86 failing [DIST] verb rows on imperative and infinitive forms.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define [DIST=de] and [DIST=di] in alphabet inventory and pattern groups (<PrepronominalPrefixes>)
- [x] #2 Merge insert_di1 and insert_di2 into unified insert_di.csv (# rule: insert_DIST, # stage: insert_DIST) and update verb-di-realize.csv
- [x] #3 Create declarative feature_acceptors/morphotactics.csv licensing [DIST=de] with indicative tenses, [DIST=di] with non-indicative tenses, and [Aspect=immediate]/[Aspect=infinitive] with their respective tenses
- [x] #4 Update InPlaceParseConfig and read_inplace_parse in parse_chr_dict/parse.py to extract [DIST=de]/[DIST=di] and map both to [DIST] for backwards compatibility
- [x] #5 Regenerate chr-inplace-generated and verify phonological realization across indicative (te-), imperative (th-), and infinitive (tsu-) forms
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define [DIST=de] and [DIST=di] in chr-inplace-config/Phonology/Inventory/alphabet.yaml (<PPP>) and chr-inplace-config/Phonology/Patterns/phoneme_groups.yaml (<PrepronominalPrefixes>: '[WI]?([DIST=de]|[DIST=di])?').
2. Merge insert_di1.csv and insert_di2.csv into chr-inplace-config/insertions/insert_di.csv (# rule: insert_DIST, # stage: insert_DIST), rewriting [DIST=de] and [DIST=di] within a single stage.
3. Update chr-inplace-config/verb-di1-realize.csv -> verb-di-realize.csv pointing to $insert_DIST.
4. Create declarative chr-inplace-config/feature_acceptors/morphotactics.csv specifying licensing constraints for [DIST=de], [DIST=di], [Aspect=immediate], and [Aspect=infinitive].
5. Update read_inplace_parse and InPlaceParseConfig in parse_chr_dict/parse.py to extract [DIST=de] and [DIST=di] and map both back to [DIST] in canonical_root and distributive flag for backwards compatibility.
6. Regenerate chr-inplace-generated via parc_macros/generate_markers.py and verify phonological realization across indicative, imperative (th-), and infinitive (tsu-) forms.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes & Decision Record

### Linguistic Rationale:
In Cherokee, the distributive prepronominal prefix alternates between 'de-' (indicative forms) and 'di-' (non-indicative: immediate imperative and infinitive).
Because 'de-hi-' yields 'tehi-' (indicative) while 'di-hi-' yields 'th-' (imperative 'thiyohi'), the alternation is conditioned by mood/tense across the stem, not phonological context.

### Merged Realization Architecture:
In in-place mode, parc_macros/generate_markers.py only assigns one rule to stage 'insert_dist'. We merge insert_di1 and insert_di2 into a single unified insert_di.csv:
- [DIST=de]i -> t
- [DIST=de] before <V> -> t
- default [DIST=de] -> te
- [DIST=di]a/i -> ti
- [DIST=di] before 'h' -> t (yields th-)
- [DIST=di] before <V> -> ts (yields tsu-)
- default [DIST=di] -> ti
Because tags [DIST=de] and [DIST=di] are disjoint, all realizations execute within a single stage 'insert_DIST' with zero collision.

### Morphotactic Licensing CSV:
chr-inplace-config/feature_acceptors/morphotactics.csv declaratively maps:
- [DIST=de] -> [Tense=present]|[Tense=habitual]|[Tense=future_prog]|[Tense=assertive]|[Tense=reported]
- [DIST=di] -> [Tense=immediate]|[Tense=infinitive]
- [Aspect=immediate] -> [Tense=immediate]
- [Aspect=infinitive] -> [Tense=infinitive]

### Backwards Compatibility:
read_inplace_parse maps both [DIST=de] and [DIST=di] to [DIST] in InPlaceParseConfig.canonical_root and sets distributive = '+'.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented declarative morphotactic co-occurrence configuration and in-place distributive allomorph resolution:
- Defined [DIST=de] and [DIST=di] in alphabet.yaml (<PPP>) and phoneme_groups.yaml (<PrepronominalPrefixes> and <Morpheme>).
- Merged distributive insertion rules into chr-inplace-config/insertions/insert_di.csv (# rule: insert_DIST) and unified verb-di-realize.csv, removing obsolete insert_di1/insert_di2 files.
- Ensured parc_macros/generate_markers.py maps insert_dist/insert_DIST stage to $insert_DIST.
- Created chr-inplace-config/feature_acceptors/morphotactics.csv licensing [DIST=de] with indicative tenses, [DIST=di] with non-indicative tenses, and [Aspect=immediate]/[Aspect=infinitive] with respective tenses.
- Updated InPlaceParseConfig and read_inplace_parse in parse_chr_dict/parse.py to parse [DIST=de] and [DIST=di], map them to distributive='+', and maintain canonical_root backwards compatibility.
- Regenerated chr-inplace-generated and verified full phonological realization across indicative (te-), imperative (th-), and infinitive (tsu-) forms.
- All 370 tests pass cleanly in pytest.
<!-- SECTION:FINAL_SUMMARY:END -->
