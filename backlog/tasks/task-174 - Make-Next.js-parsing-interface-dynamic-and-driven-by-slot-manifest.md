---
id: TASK-174
title: Make Next.js parsing interface dynamic and driven by slot manifest
status: Done
assignee:
  - '@agent'
created_date: '2026-09-10 17:29'
updated_date: '2026-09-10 17:39'
labels: []
dependencies: []
ordinal: 184000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Expose slot manifest via /api/manifest API route and dynamically generate slot column headers, selectors, and dropdowns in parsing_interface/app/page.tsx from the manifest rather than static hardcoded SLOT_COLUMNS.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create /api/manifest route in Next.js app serving compiled slots.json manifest
- [x] #2 Update types/parser.ts and page.tsx to fetch manifest and render linear template columns dynamically
- [x] #3 Ensure column hiding and constraint propagation continue to work seamlessly across dynamically loaded slots
- [x] #4 Frontend builds cleanly with npm run build / next build
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented /api/manifest endpoint serving compiled slots.json, defined SlotManifest and ColumnDef types in types/parser.ts, refactored page.tsx to dynamically load manifest and build column definitions matching exact linear template order, and dynamicized cross-slot constraint propagation and single-line assembly preview.
<!-- SECTION:FINAL_SUMMARY:END -->
