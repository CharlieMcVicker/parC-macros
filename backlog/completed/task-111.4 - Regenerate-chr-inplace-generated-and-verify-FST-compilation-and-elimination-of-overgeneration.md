---
id: TASK-111.4
title: >-
  Regenerate chr-inplace-generated and verify FST compilation and elimination of
  overgeneration
status: Done
assignee:
  - '@agent'
created_date: '2026-09-03 16:30'
updated_date: '2026-09-03 18:10'
labels: []
dependencies:
  - TASK-111.1
  - TASK-111.2
  - TASK-111.3
parent_task_id: TASK-111
priority: high
type: task
ordinal: 120000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run generator to build chr-inplace-generated from updated chr-inplace-config. Validate YAML schemas, compile open inflect/parse FSTs, and assert that non-varying aspect forms (e.g. present) no longer overgenerate multiple paths per base class.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Execute generate_markers to create chr-inplace-generated
- [x] #2 Validate all generated YAML files against parc_macros schema suite
- [x] #3 Compile open inflect and parse FSTs with zero errors
- [x] #4 Assert non-varying forms (e.g. present) produce exactly 1 parse/inflection per base class
- [x] #5 Verify variant-bearing forms (e.g. become infinitive) parse/inflect with [Variant=N]
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Execute generate_markers on chr-inplace-config to rebuild chr-inplace-generated\n2. Validate all generated YAML files against schemas\n3. Compile open inflect and parse FSTs using parC with YAML_DIR=chr-inplace-generated\n4. Write integration test verifying that present tense on class become has exactly 1 path (no variant overgeneration)\n5. Verify variant-bearing infinitive forms parse/inflect with [Variant=N]\n6. Run test_inplace_compilation.py test suite
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Rebuilt chr-inplace-generated with unified aspect classes and Variant tags. Open inflect and parse graphs compile cleanly with zero errors (983 states). Verified that present tense forms produce exactly 1 path per base class with no variant overgeneration, and verified that variant-bearing infinitive forms (become st, 'ist, yhst, ist) inflect cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
