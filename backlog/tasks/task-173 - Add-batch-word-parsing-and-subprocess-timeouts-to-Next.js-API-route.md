---
id: TASK-173
title: Add batch word parsing and subprocess timeouts to Next.js API route
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 17:29'
updated_date: '2026-09-10 17:37'
labels: []
dependencies: []
ordinal: 183000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor parse_options CLI to support batch parsing of multiple words in one execution, and update Next.js /api/parse route to call Python once per request with timeout protection and robust path resolution.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Support multiple words batch parsing in parse_options CLI when --json flag is used
- [x] #2 Update /api/parse in parsing_interface to execute a single batch CLI subprocess per API request instead of per-word spawning
- [x] #3 Add execution timeout handling to prevent hanging promises on subprocess failure
- [x] #4 Add REPO_ROOT environment variable resolution with fallback to safe path resolution
- [x] #5 Ensure positional arguments are safely passed to Python CLI (e.g. using -- delimiter)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented batch word parsing in parse_options CLI and Next.js /api/parse route. parse_options now supports one or more words, returning a structured results array when multiple words are passed with --json. /api/parse now invokes a single Python subprocess per request with a 30s execution timeout and process cleanup, robust REPO_ROOT resolution with fallback, and uses the -- positional argument delimiter to safely handle hyphen-prefixed tokens. Verified via pytest and TypeScript check.
<!-- SECTION:FINAL_SUMMARY:END -->
