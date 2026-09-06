---
id: TASK-55
title: Investigate verb-aspect.csv generation bug
status: Done
assignee:
  - '@agent'
created_date: '2026-07-17 23:08'
updated_date: '2026-07-17 23:08'
labels: []
dependencies: []
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate why the content of verb-aspect.csv is getting shoved into pro_replace.yaml during generation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Find the root cause of the incorrect file generation
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Discovered that verb-aspect.csv specifies '# morpheme_name: [Aspect]' instead of '# morpheme_tag: [Aspect]'. The script generate_morpheme_replace_rules.py expects 'morpheme_tag' and falls back to '[Pro]' if it is not found, causing the content to be generated into pro_replace.yaml.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Identified that verb-aspect.csv uses morpheme_name instead of morpheme_tag. generate_morpheme_replace_rules.py only reads morpheme_tag, falling back to [Pro] (hence generating into pro_replace.yaml).
<!-- SECTION:FINAL_SUMMARY:END -->
