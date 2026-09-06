---
id: TASK-12
title: Slim down spanish-base configuration files
status: Done
assignee:
  - '@myself'
created_date: '2026-07-04 20:52'
updated_date: '2026-07-04 20:53'
labels: []
dependencies: []
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove shell files and remove README.md from empty folders within spanish-base, then list the remaining files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify shell files/folders in spanish-base and how to remove them
- [x] #2 Remove README.md files from folders in spanish-base that are otherwise empty
- [x] #3 Report what files are remaining in spanish-base
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Identify directories in spanish-base that only contain README.md or are empty.\n2. Delete README.md files from those otherwise empty folders.\n3. Identify and remove shell folders/files with no actual configuration data.\n4. Document what remains in spanish-base.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed README.md files from empty directories (Morphotactics/Paradigm, Exponence/FeatureMarkers, Exponence/ContingentFeatureMarkers, and Lexicon/PartOfSpeech) in spanish-base to slim down the folder. Verified that all tests still pass and the build pipeline dynamically generates required directories.
<!-- SECTION:FINAL_SUMMARY:END -->
