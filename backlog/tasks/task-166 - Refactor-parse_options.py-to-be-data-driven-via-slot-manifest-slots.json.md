---
id: TASK-166
title: Refactor parse_options.py to be data-driven via slot manifest (slots.json)
status: Done
assignee:
  - '@myself'
created_date: '2026-09-10 16:38'
updated_date: '2026-09-10 16:44'
labels: []
dependencies: []
ordinal: 176000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor parse_chr_dict/parse_options.py to dynamically read slot structures, template order, and root boundaries directly from slots.json (via get_slot_manifest()) rather than hardcoding slot and tag names.

Background & Motivation:
Currently, parse_options.py extracts prefix bundles, roots, and suffix bundles using a hardcoded token parser (tracking prefix_class, pro, h_alt, aspect_class, variant, aspect, tense). When new slots (such as slot:voice or slot:nfs) are added to chr-config/verb.yaml, parse_options.py should automatically adapt without requiring manual Python code changes.

Technical Details:
- slots.json (loaded via parse_chr_dict.slots.get_slot_manifest()) contains:
  - 'template': linear token list e.g. ['<PrepronominalPrefixes>', '<PrefixClass>', '<Pro>', '<H_metathesis>', '<H_alt>', '<Root>', '<AspectClass>', '<Variant>', '<Aspect>', '<Tense>']
  - 'root_boundaries': {'left': '<H_alt>', 'right': '<AspectClass>'}
  - 'slots': list of slot objects with 'name', 'role' ('prefix' or 'suffix'), 'tags'
  - 'tag_to_slot': mapping from tag names to slot names
- parse_options.py should use these mappings to:
  1. Dynamically partition tags into prefix slots (occurring before <Root>) and suffix slots (occurring after <Root>).
  2. Dynamically identify root boundary transitions from the manifest.
  3. Populate RootParseOptions.slot_options dictionary dynamically for all slots/tags present in the manifest.
- Preserve backward-compatible property accessors on RootParseOptions while exposing the generic slot_options map.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Load slot configuration dynamically using get_slot_manifest() in parse_chr_dict/parse_options.py
- [x] #2 Dynamically partition prefix tags, root boundaries, and suffix tags based on template and root_boundaries from manifest
- [x] #3 Populate RootParseOptions.slot_options dynamically for all slots and tags present in slots.json
- [x] #4 Add unit tests in tests/test_parse_options.py verifying dynamic adaptation when tested against custom/extended slot manifests
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect get_slot_manifest() data structures and analyze token stream partitioning against template & root_boundaries.
2. Refactor parse_chr_dict/parse_options.py:
   - Dynamic tag/slot partitioning based on template order (<Root> boundary) and slots list.
   - Dynamic parsing in parse_token_sequence(tokens, manifest=None) extracting prefix slots, root chars/internal tags, and suffix slots.
   - Dynamic slot_options dictionary generation in RootParseOptions while maintaining backward-compatible property accessors (prefix_class_options, pronominal_options, etc.).
   - Support custom manifests in parse_token_sequence, extract_parse_options_from_lattice, and extract_parse_options.
3. Add comprehensive unit tests in tests/test_parse_options.py testing custom manifests with novel slots and template configurations.
4. Run full test suite and verify all ACs and DoDs.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored parse_chr_dict/parse_options.py to be data-driven via slot manifest (slots.json):
- Integrated get_slot_manifest(), get_slot_tag_map(), get_root_boundary_tag_prefixes(), and get_slot_name_to_tag_map() from parse_chr_dict/slots.py.
- Dynamically partitions prefix and suffix slots based on template order (<Root> slot position) and roles defined in slots.json.
- Dynamic parse token sequence decomposition in parse_token_sequence() supporting custom manifest topologies.
- Dynamically populated RootParseOptions.slot_options dictionary preserving backward-compatible property accessors.
- Added comprehensive unit tests in tests/test_parse_options.py covering custom/extended manifests and dynamic slot option structures.
<!-- SECTION:FINAL_SUMMARY:END -->
