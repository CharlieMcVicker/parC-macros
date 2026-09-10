---
id: TASK-167
title: >-
  Promote Voice Infix to a first-class template slot in verb.yaml and grammar
  pipeline
status: To Do
assignee: []
created_date: '2026-09-10 16:38'
updated_date: '2026-09-10 16:40'
labels: []
dependencies: []
ordinal: 177000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Promote Voice Infix from an internal root prefix tag to a first-class morphotactic template slot (slot:voice) positioned immediately before <Root> in chr-config/verb.yaml, and update the full dictionary derivation pipeline and roots.csv output.

Background & Motivation:
Currently, Voice Infix tags ([VoiceInfix=ada] for middle voice, [VoiceInfix=ad] for reflexive, [VoiceInfix=adad] for reciprocal) are embedded directly at the start of the <Root> string during FST expansion and parsing (e.g. producing root '[VoiceInfix=ada]tek'). This complicates lexical root extraction, requires special root filtering, and prevents pure stem extraction in the UI.

Technical Details:
- Grammar & Generator:
  - Add slot:voice under 'slots' in chr-config/verb.yaml with role 'prefix' and tags ['VoiceInfix'].
  - Place 'slot:voice' in 'paradigm.template' right before '<Root>' (between <H_alt> and <Root>).
  - Update expand_voice phonology rule in Phonology/Rules/voice.yaml to operate as a slot replacement rule or phonology stage.
  - Run 'python parc_macros/generate_markers.py chr-config chr-generated' to update YAML assets and slots.json.
- Domain Models & Derivation Pipeline:
  - Update LexicalVerb in parse_chr_dict/types.py to store voice_infix as a first-class attribute and serialize it in to_row_dict().
  - Update parse_chr_dict/__main__.py: add 'voice_infix' to ROOTS_FIELDNAMES and sort keys.
  - Update parse.py, derive.py, reconstruct.py, and segment.py to isolate pure stems (e.g. 'tek') from the voice slot.
  - Run the full dictionary batch pipeline (./parse_dict.sh / python -u -m parse_chr_dict) to verify zero regressions against errors.csv and verify that middle-voice entries (e.g., entry 554) output pure roots with voice_infix populated in roots.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define slot:voice in chr-config/verb.yaml and place it in paradigm.template before <Root>
- [ ] #2 Compile voice slot markers and updated slots.json via parc_macros/generate_markers.py
- [ ] #3 Update expand_voice phonology rule and parse graph compilation to handle slot:voice
- [ ] #4 Ensure lexical roots extracted in parse.py, derive.py, and reconstruct.py are pure stems without embedded [VoiceInfix=...] tags
- [ ] #5 Update LexicalVerb in types.py and parse_chr_dict/__main__.py ROOTS_FIELDNAMES to export voice_infix to roots.csv
- [ ] #6 Run full dictionary pipeline (./parse_dict.sh) verifying zero regressions in errors.csv and correct roots.csv output
- [ ] #7 Add unit tests verifying voice slot compilation, clean root parsing, and middle voice multi-form derivation
<!-- AC:END -->
