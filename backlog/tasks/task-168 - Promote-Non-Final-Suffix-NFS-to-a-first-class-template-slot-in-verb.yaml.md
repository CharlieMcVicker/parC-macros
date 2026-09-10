---
id: TASK-168
title: Promote Non-Final Suffix (NFS) to a first-class template slot in verb.yaml
status: To Do
assignee: []
created_date: '2026-09-10 16:38'
updated_date: '2026-09-10 16:40'
labels: []
dependencies: []
ordinal: 178000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Promote Non-Final Suffixes (NFS) from root-internal tags to a first-class morphotactic template slot (slot:nfs) positioned immediately following <Root> (before slot:aspect) in chr-config/verb.yaml, and update the full dictionary derivation pipeline and roots.csv output.

Background & Motivation:
Currently, Non-Final Suffix tags (e.g. [NFS=AMB] for ambulative '-it-', [NFS=MOT] for motion) are appended to the root string during parsing (e.g. producing root 'whahthvh[NFS=AMB]'). Promoting NFS to an explicit template slot isolates the pure lexical root (e.g. 'whahthvh') and allows clean dropdown selection for derivational/aspectual suffixes in user interfaces.

Technical Details:
- Grammar & Generator:
  - Add slot:nfs under 'slots' in chr-config/verb.yaml with role 'suffix', tags ['NFS'], and sources from verb-nfs.csv.
  - Place 'slot:nfs' in 'paradigm.template' immediately following '<Root>' and before 'slot:aspect'.
  - Support optionality ([NFS=none] / epsilon).
  - Run 'python parc_macros/generate_markers.py chr-config chr-generated' to regenerate YAML assets and compile updated slots.json.
- Domain Models & Derivation Pipeline:
  - Update ParseData, VerbTemplate, and LexicalVerb in parse_chr_dict/types.py to store nfs as an explicit field and serialize it in to_row_dict().
  - Update parse_chr_dict/__main__.py: add 'nfs' to ROOTS_FIELDNAMES and sort keys.
  - Update parse.py, derive.py, reconstruct.py, segment.py, and parse_options.py to isolate pure stems (e.g. 'whahthvh') from the NFS slot.
  - Run the full dictionary batch pipeline (./parse_dict.sh / python -u -m parse_chr_dict) to verify zero regressions across all 708 corpus entries and verify that ambulative/motion entries correctly export nfs to roots.csv.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define slot:nfs in chr-config/verb.yaml and place it in paradigm.template immediately after <Root>
- [ ] #2 Compile NFS slot markers and updated slots.json via parc_macros/generate_markers.py
- [ ] #3 Update expand_nfs phonology rule and parse graph compilation to handle slot:nfs
- [ ] #4 Ensure lexical roots in derivation pipeline and ParseData are pure stems without embedded [NFS=...] tags
- [ ] #5 Update LexicalVerb in types.py and parse_chr_dict/__main__.py ROOTS_FIELDNAMES to export nfs to roots.csv
- [ ] #6 Run full dictionary pipeline (./parse_dict.sh) verifying zero regressions in errors.csv and correct roots.csv output
- [ ] #7 Add unit tests verifying NFS slot compilation, clean root extraction, and multi-form derivation on NFS corpus entries
<!-- AC:END -->
