---
id: TASK-126
title: Create interactive CLI tool for automatic segmentation and parsing
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-06 16:32'
updated_date: '2026-09-06 16:35'
labels: []
dependencies: []
modified_files:
  - parse_chr_dict/segment.py
  - tests/test_segment.py
ordinal: 136000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a command line tool (runnable as a module, e.g. python -m parse_chr_dict.segment) modeled after parse_chr_dict/parse.py that provides automatic segmentation using shortest-path arc alignment in addition to parsing. Uses get_arc_alignment to map surface input symbols to output tags and phonological segments, displaying both alignment, morpheme segmentation, and parse groupings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement get_arc_alignment(fst, surface_str) supporting parC symbol tables and word FSAs
- [x] #2 Implement morpheme segmentation extraction from arc alignments
- [x] #3 Implement interactive CLI / module runner in parse_chr_dict/segment.py
- [x] #4 Display arc alignment, segmented surface form, and root-grouped parses
- [x] #5 Add automated tests for get_arc_alignment and segmentation CLI
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement get_arc_alignment(fst, surface_str) in parse_chr_dict/segment.py:
   - Handle symbol tables (OpenFst symbol table or parC get_symbol_table).
   - Use parC word_fsa(surface_str) or pynini.accep(surface_str) appropriately so composition with parC FST succeeds.
   - Extract the shortest path and return list of (in_sym, out_sym) tuples.
2. Implement segmentation derivation helper:
   - Derive grouped morpheme segments from the alignment (e.g. k-atat-e-k-a and morpheme labels).
3. Implement CLI module runner parse_chr_dict/segment.py:
   - Module executable: python -m parse_chr_dict.segment [optional words...]
   - Interactive REPL when run with no arguments, matching parse.py interactive loop with prompt, readline support, and graceful exit.
   - For each input word, print:
     * Segmented surface word and morpheme decomposition
     * Arc alignment table (in_sym --> out_sym)
     * Full parses grouped by root (as in parse.py) with total count summary
4. Add unit test suite in tests/test_segment.py covering get_arc_alignment, segmentation formatting, and CLI execution.
5. Verify tests with pytest and manual CLI test run.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented interactive command line tool and module runner `parse_chr_dict/segment.py` for automatic morphological segmentation and parsing. Integrated `get_arc_alignment(fst, surface_str)` to traverse shortest-path arc alignments using parC symbol tables and word FSAs. Added `segment_alignment` to extract hyphenated surface morpheme boundaries and morphological slot breakdowns. Added interactive REPL and CLI argument modes matching the module runner conventions of `parse_chr_dict/parse.py`. Added test suite in `tests/test_segment.py` with 100% pass rate.
<!-- SECTION:FINAL_SUMMARY:END -->
