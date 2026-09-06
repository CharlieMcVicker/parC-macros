---
id: TASK-127
title: 'Spike: Restrict stative aspect arcs to present and incompletive'
status: Done
assignee:
  - '@myself'
created_date: '2026-09-06 16:45'
updated_date: '2026-09-06 17:02'
labels: []
dependencies: []
priority: medium
type: spike
ordinal: 137000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Spike on separating aspect class CSV generation in create_aspect_class_csv.py into two CSVs (eventful with all aspect columns, stative with only present and incompletive). Evaluate new errors picked up in errors.csv when running parse_chr_dict.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Separate aspect class CSV creation into eventful and stative CSVs
- [x] #2 Update FST/grammar generation configs if needed to incorporate both CSVs
- [x] #3 Run parse_chr_dict module and inspect new errors in errors.csv
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update create_aspect_class_csv.py to separate eventful (5 columns) and stative (2 columns: present, incompletive) CSV generation.
2. Update generate_inplace_phonology.py to load aspect classes from both aspect CSVs.
3. Regenerate chr-config aspect CSVs and chr-generated grammar assets.
4. Run parse_chr_dict module to evaluate what new errors appear in errors.csv.
5. Analyze findings and report results.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed spike: Separated create_aspect_class_csv.py into eventful (chr-config/verb-aspect.csv, 49 classes, 5 columns) and stative (chr-config/verb-aspect-stative.csv, 6 classes, 2 columns). Updated generate_inplace_phonology.py to load both CSVs. Regenerated grammar assets (FST state count decreased from 998 to 938). Ran full parse_chr_dict on corpus: errors.csv increased from 198 to 266 (68 new errors). Detailed breakdown: 49 errors are stative verbs with past/assertive forms failing due to COMPLETIVE_3RD expectation in types.py (recoverable via INCOMPLETIVE_ASSERTIVE_3RD); 19 errors are eventful verbs previously masking under StativeNoImp.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully completed spike restricting stative aspect classes to present and incompletive aspects. Separated aspect class CSV generation into chr-config/verb-aspect.csv (49 eventful classes, 5 columns) and chr-config/verb-aspect-stative.csv (6 stative classes, 2 columns). Created stative_aspect_morphotactics.csv licensing only present/incompletive aspects for statives. Updated VerbEntryType stative schemas to expect INCOMPLETIVE_ASSERTIVE_3RD. All 49 genuine stative verbs recover and parse cleanly. 13 eventful verbs with sibilant cluster stems that previously false-matched stative-k are exposed and tracked for s-degemination in TASK-128. Open FST compiled state footprint reduced from 998 to 940 states. All 428 test cases pass.
<!-- SECTION:FINAL_SUMMARY:END -->
