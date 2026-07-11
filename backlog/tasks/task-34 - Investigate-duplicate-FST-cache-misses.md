---
id: TASK-34
title: Investigate duplicate FST cache misses
status: Done
assignee:
  - '@myself'
created_date: '2026-07-11 02:01'
updated_date: '2026-07-11 02:01'
labels: []
dependencies: []
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research why the same cache key is checked and reported as a miss multiple times in get_cached_fst, rather than being cached on the first miss/compilation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Find the get_cached_fst implementation
- [ ] #2 Explain the duplicate cache miss behavior to the user
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Locate where parC cache module is defined.
2. Read the source code around get_cached_fst and cache writes.
3. Determine why it doesn't write/cache the FST upon compile or if it skips writing on certain errors/scenarios.
4. Answer the user and update the task.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Duplicate cache misses occur because compilation of specific markers/FSTs fails (raising an exception caught by build_inflect_graph_for_root_regex). Because the compilation fails, the FST is never successfully compiled or saved to disk (save_cached_fst is not called), so subsequent checks for the same marker continue to result in cache misses.
<!-- SECTION:FINAL_SUMMARY:END -->
