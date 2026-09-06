---
id: TASK-33
title: Debug logging in pytest for test_chr_inflect
status: Done
assignee:
  - '@myself'
created_date: '2026-07-11 01:54'
updated_date: '2026-07-11 01:56'
labels: []
dependencies: []
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate why no terminal output/logs are shown when running pytest on test_chr_inflect.py, add logging, and run to verify output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Configure logging/prints in test_chr_inflect.py
- [x] #2 Successfully run pytest and display logging output
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify tests/test_chr_inflect.py to use both standard prints and loguru/standard logging.
2. Run pytest with different flags (e.g. -vv, -s, --tb=short) to see if we get output.
3. Diagnose and fix the log output capture.
4. Mark AC as completed once logs are displayed.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Configured loguru to run without capture by invoking python directly under conda run --no-capture-output. Reverted debug lines from test file.
<!-- SECTION:FINAL_SUMMARY:END -->
