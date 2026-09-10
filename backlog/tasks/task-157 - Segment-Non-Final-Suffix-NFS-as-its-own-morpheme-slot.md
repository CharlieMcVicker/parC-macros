---
id: TASK-157
title: Segment Non-Final Suffix (NFS) as its own morpheme slot
status: Done
assignee:
  - '@agent'
created_date: '2026-09-09 19:14'
updated_date: '2026-09-09 19:15'
labels: []
dependencies: []
ordinal: 167000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make Non-Final Suffix (NFS) tags inside verb roots segment into their own distinct morpheme slot to the left of aspect class rather than merged into the root surface.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 segment.py breaks out NFS as a distinct segment slot (e.g. it in a-tahwatvh-it-o-h-a)
- [x] #2 All tests pass
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated segment.py to isolate Non-Final Suffix (NFS) tags ([NFS=...]) into their own distinct morpheme slot to the left of aspect class rather than bundling them into the root surface. Now words like atahwatvhitoha correctly segment into a-tahwatvh-it-o-h-a with Root = tahwatvh and NFS = it.
<!-- SECTION:FINAL_SUMMARY:END -->
