---
id: TASK-17
title: Remove defaults key from part of speech configuration
status: Done
assignee:
  - '@antigravity'
created_date: '2026-07-08 17:14'
updated_date: '2026-07-08 17:46'
labels: []
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove the 'defaults' key from verb.yaml (and other part-of-speech configurations) to enforce atomicity and rely solely on metadata within each CSV file.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove 'defaults' sections from spanish-config/verb.yaml and chr-config/verb.yaml
- [x] #2 Update parse_csv_with_metadata and generate_markers.py to remove defaults dictionary and fallback logic
- [x] #3 Ensure all tests pass and configurations are atomic
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored generate_markers.py to remove 'defaults' parsing and fallback logic. Updated parse_csv_with_metadata to take only the csv_path argument. Verified that all configurations are atomic and tests pass successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
