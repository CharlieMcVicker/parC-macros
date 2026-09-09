---
id: TASK-152
title: >-
  Add h-metathesis flag to VerbMetadata and integrate into dictionary derivation
  pipeline
status: Done
assignee:
  - '@agent'
created_date: '2026-09-09 13:07'
updated_date: '2026-09-09 13:20'
labels: []
dependencies: []
ordinal: 162000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate h-metathesis into the dictionary derivation and reconstruction pipeline. Correct chr-config/feature_acceptors/h_meta_morphotactics.csv to target H_metathesis via <HMetaPro>. Add is_h_metathesis flag to VerbMetadata and ParseData, compile <HMetaPro> FST to identify triggering forms in derivation and reconstruction, update build_tag_str and inflect_form to include H_metathesis, and ensure test suite passes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Fix quoting in chr-config/Phonology/Patterns/phoneme_groups.yaml and configure h_meta_morphotactics.csv
- [x] #2 Regenerate grammar markers and validate YAML schemas
- [x] #3 Add is_h_metathesis flag to VerbMetadata, ParseData, and serialization in parse_chr_dict
- [x] #4 Use compiled <HMetaPro> FST to conditionally apply and expect h_metathesis during derivation and reconstruction
- [x] #5 Update build_tag_str, inflect_form, and to_tag_string to format [H_metathesis=...] slot
- [x] #6 Add tests verifying h-metathesis in dictionary pipeline and ensure full test suite passes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Fix YAML quoting in chr-config/Phonology/Patterns/phoneme_groups.yaml and configure target_slot/licensed in chr-config/feature_acceptors/h_meta_morphotactics.csv.
2. Regenerate markers (generate_markers.py) and validate YAML assets (yaml_validation.py).
3. Implement is_h_metathesis_trigger helper using compiled <HMetaPro> FST.
4. Update VerbMetadata, ParseData, VerbTemplate, and LexicalVerb to support is_h_metathesis flag and serialization.
5. Update parse.py, derive.py, reconstruct.py, and types.py to parse, branch, and reconstruct [H_metathesis=active] vs [H_metathesis=none] across the open_root_template.
6. Verify with test cases and run full pytest suite.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Integrated h-metathesis into the dictionary derivation and reconstruction pipeline. Handcrafted feature acceptor chr-config/feature_acceptors/h_meta_morphotactics.csv compiled into morphotactics acceptor constraining H_metathesis to [H_metathesis=active] vs [H_metathesis=none]. Implemented is_h_metathesis_trigger() using compiled <HMetaPro> FST. Updated VerbMetadata and LexicalVerb to track is_h_metathesis boolean, inflect_form() and build_tag_str() to conditionally emit [H_metathesis=active] for trigger forms and [H_metathesis=none] otherwise. Updated candidate derivation and pruning in derive.py to branch and enforce multi-form metathesis consistency. All 136 tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
