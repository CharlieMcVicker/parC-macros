---
id: TASK-168
title: Promote Non-Final Suffix (NFS) to a first-class template slot in verb.yaml
status: Done
assignee:
  - '@subagent'
created_date: '2026-09-10 16:38'
updated_date: '2026-10-02 15:33'
labels: []
dependencies: []
modified_files:
  - chr-config/verb.yaml
  - chr-generated/Morphotactics/Paradigm/verb.yaml
  - chr-generated/Morphotactics/Paradigm/verb_segmented.yaml
  - chr-generated/slots.json
  - parse_chr_dict/__main__.py
  - parse_chr_dict/derive.py
  - parse_chr_dict/parse.py
  - parse_chr_dict/reconstruct.py
  - parse_chr_dict/slots.py
  - parse_chr_dict/types.py
  - roots.csv
  - tests/test_lexical_verb_types.py
  - tests/test_markers_generation.py
  - tests/test_nfs.py
  - tests/test_parse_options.py
  - tests/test_slots_manifest.py
  - tests/test_yaml_validation.py
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
- [x] #1 Define slot:nfs in chr-config/verb.yaml and place it in paradigm.template immediately after <Root>
- [x] #2 Compile NFS slot markers and updated slots.json via parc_macros/generate_markers.py
- [x] #3 Update expand_nfs phonology rule and parse graph compilation to handle slot:nfs
- [x] #4 Ensure lexical roots in derivation pipeline and ParseData are pure stems without embedded [NFS=...] tags
- [x] #5 Update LexicalVerb in types.py and parse_chr_dict/__main__.py ROOTS_FIELDNAMES to export nfs to roots.csv
- [x] #6 Run full dictionary pipeline (./parse_dict.sh) verifying zero regressions in errors.csv and correct roots.csv output
- [x] #7 Add unit tests verifying NFS slot compilation, clean root extraction, and multi-form derivation on NFS corpus entries
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update chr-config/verb.yaml: define slot:nfs under slots with role: suffix and TagGroup: NFS (optional: true), and place slot:nfs in paradigm.template immediately after <Root>.\n2. Regenerate YAML assets and slots.json using parc_macros/generate_markers.py.\n3. Update parse_chr_dict domain models and derivation pipeline:\n   - slots.py: Update FALLBACK_MANIFEST, DEFAULT_SLOT_TAG_MAP, SPECIAL_TAG_MAP for NFS -> nfs.\n   - types.py: Add nfs field to ParseData, VerbTemplate, LexicalVerb, and update to_row_dict(), to_tag_string(), inflect_form().\n   - parse.py: Update read_parse to parse [NFS=...] into nfs, and update build_root_filter_fsa to support optional post-root NFS/AspectClass boundary.\n   - derive.py: Check p_data.nfs == hyp.nfs and preserve nfs in VerbTemplate.\n   - reconstruct.py: Update build_tag_str to emit [NFS=...] after root and reconstruct_row to read nfs.\n   - parse_chr_dict/__main__.py: Add nfs to ROOTS_FIELDNAMES and sort keys.\n   - parse_options.py & segment.py: Support nfs in SuffixBundle, option extraction, and segmentation.\n4. Update unit tests across test_nfs.py, test_markers_generation.py, test_slots_manifest.py, test_yaml_validation.py, test_parse_options.py.\n5. Run test suite and full dictionary batch pipeline (YAML_DIR=chr-generated/ python -u -m parse_chr_dict) to verify 0 regressions and correct roots.csv output.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Promoted Non-Final Suffixes (NFS) to a first-class morphotactic template slot in verb.yaml and the dictionary derivation engine.

Key Changes:
- **Grammar & Morphotactics**: Configured 'slot:nfs' in chr-config/verb.yaml with role 'suffix' and TagGroup 'NFS' (optional: true), positioned immediately following '<Root>' and before 'slot:aspect'. Regenerated YAML assets, verb paradigms, and slots.json.
- **Domain Models & Pipeline**: Added 'nfs' field to ParseData, VerbTemplate, and LexicalVerb in parse_chr_dict/types.py; updated parse.py, derive.py, reconstruct.py, segment.py, and parse_options.py to parse, inflect, and isolate pure lexical roots from the NFS slot.
- **Batch Pipeline & Output**: Exported 'nfs' column to ROOTS_FIELDNAMES in parse_chr_dict/__main__.py and roots.csv with deterministic multi-key sorting.
- **Verification**: All 171 pytest unit and integration tests passed; full dictionary pipeline (708 entries) ran with zero regressions in errors.csv and verified clean roots (e.g. 'whahthvh' with nfs='AMB') across roots.csv.
<!-- SECTION:FINAL_SUMMARY:END -->
