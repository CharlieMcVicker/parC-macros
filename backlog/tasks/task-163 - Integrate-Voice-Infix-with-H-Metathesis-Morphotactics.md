---
id: TASK-163
title: Integrate Voice Infix with H-Metathesis Morphotactics
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 15:41'
updated_date: '2026-09-10 15:45'
labels: []
dependencies: []
ordinal: 173000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Support VoiceInfix in the verb template and enable H-metathesis phonological rules across voice infixes without morphotactic overgeneration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Reorder expand_voice before tag_h_metathesis in chr-config/verb.yaml
- [x] #2 Update tag_h_metathesis.yaml context to match voice infix material (alinh -> alhin)
- [x] #3 Update phoneme patterns and h_meta_morphotactics to license H-metathesis with voice infixes and avoid 3sg.B overgeneration
- [x] #4 Update Python acceptors, derivation, and reconstruction pipeline in parse_chr_dict
- [x] #5 Pass all tests in tests/test_h_metathesis.py including talhinoheha test cases and full test suite
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reorder expand_voice before tag_h_metathesis in chr-config/verb.yaml
2. Update tag_h_metathesis.yaml context patterns to support multi-syllable/voice-infix contexts
3. Check and update phoneme groups and h_meta_morphotactics for voice infix licensing
4. Regenerate YAMLs with generate_markers.py
5. Update acceptors.py and parse_chr_dict types/derivation if needed
6. Add unit test for talhinoheha and voice infix metathesis in tests/test_h_metathesis.py
7. Verify all tests pass
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Integrated Voice Infix with H-Metathesis phonology and morphotactic licensing. Reordered expand_voice before tag_h_metathesis in chr-config/verb.yaml and updated context matching in chr-config/Phonology/Rules/tag_h_metathesis.yaml to match non-laryngeal voice infix material. Added <HMetaVoice> pattern group and '# unless: <HMetaVoice>' to chr-config/feature_acceptors/h_meta_morphotactics.csv. Updated compile_morphotactic_acceptor and is_h_metathesis_trigger in parse_chr_dict to support disjunctive voice infix licensing without overgenerating active/none pairs on 3sg.B forms. Added unit tests for talhinoheha and voice infix licensing in tests/test_h_metathesis.py; all 146 tests in the test suite pass.
<!-- SECTION:FINAL_SUMMARY:END -->
