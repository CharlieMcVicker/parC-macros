---
id: TASK-169
title: >-
  Build interactive morpheme dropdown selector interface powered by
  parse_options
status: To Do
assignee: []
created_date: '2026-09-10 16:39'
labels: []
dependencies: []
ordinal: 179000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build an interactive parsing and morpheme selection interface (API and interactive CLI/TUI) where each morphological slot is presented as a dropdown/selector and choices dynamically constrain remaining slots in real time.

Background & Motivation:
The end goal is a morpheme parsing workflow where users inspect an ambiguous Cherokee verb form and select the intended morphemes slot-by-slot (Prepronominal, Pronominal, Voice, Root, NFS, Aspect, Tense) from dropdowns populated directly from WordParseOptions.

Technical Details:
- Interactive Selector Engine:
  - Implement MorphemeSelectorState in parse_chr_dict/parse_options.py (or a dedicated UI/API submodule).
  - Given a WordParseOptions instance for a surface word, provide methods to:
    - Query currently available choices for any unselected slot.
    - Set a selection for a slot (e.g. select root 'tek' or pronominal '3sg.A').
    - Filter and narrow the valid paths across all remaining slots in real time (reactive constraint propagation).
    - Reset or undo a slot selection.
    - Check if current selections specify a unique parse or return remaining candidate parses.
- Full Roundtrip Reconstitution:
  - When all slots (or sufficient disambiguating slots) are selected, assemble the morpheme sequence and verify surface generation matches the input word via reconstruct.py.
- Interactive Terminal / TUI Interface:
  - Provide an interactive terminal dropdown/selector (e.g., using curses, prompt_toolkit, or rich select menus) invoked via 'python -m parse_chr_dict.parse_options --interactive-select <word>'.
- Export & Serialization:
  - Ensure the selector state and options schema can be easily consumed by external web frontends (e.g. React/Vue dropdown components) via JSON endpoints or CLI --json outputs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement MorphemeSelectorState engine providing reactive slot filtering and constraint propagation across WordParseOptions
- [ ] #2 Support step-by-step slot selection, clearing, and candidate narrowing based on valid FST lattice paths
- [ ] #3 Provide roundtrip verification to reconstruct the surface word from selected slot morphemes
- [ ] #4 Implement interactive terminal morpheme selector CLI tool
- [ ] #5 Add unit tests verifying slot constraint propagation, multi-step narrowing, and roundtrip reconstruction
<!-- AC:END -->
