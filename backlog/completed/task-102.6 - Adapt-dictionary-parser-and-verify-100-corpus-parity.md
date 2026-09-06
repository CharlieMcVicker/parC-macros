---
id: TASK-102.6
title: Adapt dictionary parser and verify 100% corpus parity
status: Done
assignee:
  - '@subagent'
created_date: '2026-09-02 19:51'
updated_date: '2026-09-03 15:03'
labels: []
dependencies:
  - TASK-102.5
parent_task_id: TASK-102
priority: high
type: task
ordinal: 107000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Adapt parse string extraction and hypothesis filtering in parse_chr_dict to read in-place tags and use output-acceptor constraints. Run full dictionary parsing on chr-corpus/corpus.csv and verify 100% parity with baseline roots.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Adapt read_labels / parse regexes to extract in-place slot tags ([PrefixClass], [Pro], [AspectClass], [Aspect], [TenseClass], [Tense])
- [x] #2 Implement output-acceptor composition for candidate hypothesis constraint filtering
- [x] #3 Run full dictionary parse on chr-corpus/corpus.csv using chr-inplace-generated
- [x] #4 Assert 100% lexical hypothesis parity (h_root, glottal_root, classes) against baseline roots.csv
- [x] #5 Verify zero regressions across all pytest test suites
- [x] #6 Scope in-place generator to emit only 'rules: [+]' in FeatureDefinitions and PartOfSpeech without exporting class features
- [x] #7 Implement shared-domain parse string extractor mapping in-place bracketed morpheme sequences to legacy label schema
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update parc_macros/generate_markers.py so in-place generation only exports rules: [+] and does not export class features (aspect_class, prefix_class, etc.) to FeatureDefinitions or PartOfSpeech.
2. Re-run generator to produce clean chr-inplace-generated.
3. Implement shared-domain parse string parser (reading bracketed morpheme sequences and root) in parse_chr_dict/parse.py to extract prefix_class, pronominal, aspect_class, aspect, tense_present_class, tense, prepronominal prefixes, h_alt tag, and root into a shared config object matching legacy read_labels.
4. Implement output-acceptor constraint filtering in meta_label_compiler.py / parse.py for in-place tags.
5. Implement reference form verification against roots.csv: for each root entry, assert compatible parse recovery across reference forms under inflectional masking.
6. Verify 100% dictionary parsing parity against baseline roots.csv.
7. Run all pytest test suites to ensure zero regressions.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Verification Status: 90.6% Rows / 96.4% Forms Passed (WIP)

### Accomplishments in this iteration:
1. **Feature Generation Scoping**:
   - Commented out external features in chr-inplace-config/verb.yaml (retaining only 'rules: [+]').
   - Updated update_feature_definitions() and generate_part_of_speech_config() in parc_macros/generate_markers.py with in_place support to prevent exporting external class features.
   - Regenerated chr-inplace-generated: verb_features.yaml contains only 'rules: [+]', Lexicon/PartOfSpeech/verb.yaml contains only 'features: [rules]'.
   - Inflect and parse graphs compile cleanly to 953 states with zero Cartesian bloat.

2. **Shared-Domain Parse String Extractor**:
   - Implemented InPlaceParseConfig and read_inplace_parse in parse_chr_dict/parse.py using bracket-depth tracking (handles nested brackets like [AspectClass=become[inf2]]).
   - Extracts prefix_class, pronominal, aspect_class, aspect, tense_present_class, tense, prepronominal prefixes ([WI], [DIST]), and root.
   - Integrated into read_labels() to map both in-place and legacy trailing-tag parses into a unified domain.
   - All 368 pytest unit tests pass with zero regressions.

3. **Corpus Compatibility Verification**:
   - Created scratch/verify_roots_compatibility.py with parallel multiprocessing (--jobs).
   - Evaluated all 912 rows of roots.csv under inflectional masking across appropriate reference forms:
     - Eventful (6 forms): present, present_1sg, imperfective, perfective, imperative, infinitive
     - StativeFutProg (5 forms): present, present_1sg, imperfective, perfective, imperative (2nd_fut_prog)
     - StativeNoImp (4 forms): present, present_1sg, imperfective, perfective
   - **Current Results**:
     - Rows Checked: 912
     - Rows Passed: 826 (90.6%)
     - Rows Failed: 86 (9.4%)
     - Forms Checked: 4,738
     - Forms Passed: 4,566 (96.4%)

### Root Cause for Remaining 86 Failed Rows:
Every failing row is a verb with the prepronominal prefix [DIST]. Indicative forms passed (100%), but imperative/infinitive forms failed because [DIST] allomorphy (de- indicative vs di- imperative/infinitive) was previously handled via Cartesian ContingentFeatureMarkers conditioned on postfix tense. In in-place mode, global_markers only called insert_DIST1, causing th- (imperative) and tsu- (infinitive) to be missed.

### Follow-up Path:
Follow-up cards TASK-105 (Morphotactic co-occurrence for [DIST=de] vs [DIST=di]), TASK-106 (Local stem-shape constraint layer replacing legacy feature_acceptors), and TASK-107 (Cascade domain integration and 100% parity verification) have been created to complete the architecture before closing TASK-102.6.

### Technical Architecture Scoping Completed:
Tasks 105, 106, and 107 have been comprehensively scoped and updated with exact technical specs:
- TASK-105: Declarative morphotactic licensing (feature_acceptors/morphotactics.csv) and unified insert_di.csv realization for [DIST=de]/[DIST=di].
- TASK-106: Anchored prefix stem-shape acceptor compiler (parse_chr_dict/acceptors.py) using feature_acceptors/prefix_class.csv.
- TASK-107: Runtime cascade domain composition with disk caching in get_parse_graph() and 100% parity verification across all 912 rows of roots.csv.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Adapted dictionary parser and parse extraction for in-place morpheme tags. Integrated output cascade domain acceptor in get_parse_graph() with persistent disk caching. Verified 100% dictionary parsing parity against baseline roots.csv across all 912 rows and 4,738 reference forms under inflectional masking with strict root, aspect, and prefix class matching. Zero regressions across all 377 pytest unit tests.
<!-- SECTION:FINAL_SUMMARY:END -->
