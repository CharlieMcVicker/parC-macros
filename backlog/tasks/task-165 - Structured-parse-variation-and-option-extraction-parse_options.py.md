---
id: TASK-165
title: Structured parse variation and option extraction (parse_options.py)
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-10 16:26'
updated_date: '2026-09-10 16:34'
labels: []
dependencies: []
ordinal: 175000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a new submodule parse_chr_dict/parse_options.py (analogous to segment.py) to extract and nicely represent structured morphotactic variations and feature option bundles directly from parse graph lattices before/during decoding.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create parse_chr_dict/parse_options.py module
- [x] #2 Implement FST lattice inspection/factorization to extract root equivalence classes and slot variation options (e.g. binary/n-ary tag choices) without flat string enumeration
- [x] #3 Provide clean data structures/dataclasses to represent structured parse options (e.g., shared root + slot option sets)
- [x] #4 Add unit tests verifying structured parse extraction and variation representations
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define structured dataclasses (PrefixBundle, SuffixBundle, RootParseOptions, WordParseOptions) in parse_chr_dict/parse_options.py.
2. Implement lattice extraction and factorization logic to identify root equivalence classes and factored prefix/suffix bundles from FST lattices.
3. Implement CLI interface and rich formatter for interactive and command-line parse option inspection.
4. Add comprehensive unit tests in tests/test_parse_options.py testing extraction, factorization, and equivalence with parse outputs.
5. Verify test suite and check off acceptance criteria.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented structured parse variation and option extraction in parse_chr_dict/parse_options.py.

Key highlights:
- Created frozen domain dataclasses: PrefixBundle, SuffixBundle, RootParseOptions, and WordParseOptions with rich summary formatting and JSON serialization.
- Implemented DAG lattice path extraction (extract_lattice_paths) and token sequence decomposition (parse_token_sequence), extracting root equivalence classes, factored prefix and suffix bundles, and individual slot choice sets.
- Built CLI interface supporting word arguments, -v/--verbose, --json, and interactive REPL mode.
- Added comprehensive unit tests in tests/test_parse_options.py verifying dataclasses, root equivalence groupings, NFS handling, specialized parse graph integration, CLI modes, and 100% agreement with flat parse outputs.
- Verified test suite passes completely (156 passing tests) with clean syntax compilation across all packages.
<!-- SECTION:FINAL_SUMMARY:END -->
