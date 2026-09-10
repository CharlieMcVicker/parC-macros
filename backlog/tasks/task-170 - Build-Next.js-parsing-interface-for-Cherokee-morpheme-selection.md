---
id: TASK-170
title: Build Next.js parsing interface for Cherokee morpheme selection
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 17:03'
updated_date: '2026-09-10 17:11'
labels: []
dependencies: []
ordinal: 180000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a lightweight Next.js + TypeScript web application in 'parsing_interface/' that allows users to paste Cherokee text, parses words via python -m parse_chr_dict.parse_options --json child_process, and provides a reactive slot-by-slot morpheme selector interface.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create Next.js TypeScript app in parsing_interface/ with Tailwind CSS
- [x] #2 Implement /api/parse route using child_process to invoke parse_options CLI with stripped punctuation
- [x] #3 Build Cherokee text input textarea with parse execution button and word list display
- [x] #4 Render selectable word list showing parse counts and highlighting parseable words
- [x] #5 Implement reactive client-side slot constraint propagation and selection table for sum-of-products JSON
- [x] #6 Ensure full type safety in TypeScript with proper naming conventions
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Initialize Next.js project with TypeScript and Tailwind CSS in 'parsing_interface/'.
2. Define TypeScript types matching the parse_options JSON schema (WordParseOptions, RootParseOptions, PrefixBundle, SuffixBundle, SlotOptions).
3. Implement '/api/parse' route to receive text, strip punctuation, tokenize words, and spawn 'python -m parse_chr_dict.parse_options --json' asynchronously via child_process.
4. Build UI:
   - Textarea for pasting Cherokee phonetic text with 'Parse' action.
   - Word selector list displaying tokenized words, parse counts, and parseable badges.
   - Reactive Morpheme Slot Builder at the bottom for the active word: displays slots vertically, dynamically computes available choices across remaining candidates (sum-of-products constraint propagation), and allows narrowing/resetting selections.
5. Verify end-to-end functionality and build output.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created Next.js + TypeScript parsing interface application in 'parsing_interface/'. Implemented /api/parse API route executing python -m parse_chr_dict.parse_options --json via child_process, automatic punctuation stripping, multi-word token list with parse count badges, and reactive morpheme slot builder performing client-side sum-of-products constraint propagation.
<!-- SECTION:FINAL_SUMMARY:END -->
