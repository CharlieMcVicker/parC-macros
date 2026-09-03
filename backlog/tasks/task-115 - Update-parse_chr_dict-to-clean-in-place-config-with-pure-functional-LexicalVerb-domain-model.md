---
id: TASK-115
title: >-
  Update parse_chr_dict to clean in-place config with pure functional
  LexicalVerb domain model
status: Done
assignee:
  - '@agent'
created_date: '2026-09-03 18:44'
updated_date: '2026-09-03 19:55'
labels: []
dependencies: []
priority: high
type: feature
ordinal: 125000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor parse_chr_dict to compile and parse from chr-clean-inplace-config using a pure functional domain model with IO at boundaries. Structure LexicalVerb as a composition of InPlaceParseConfig and VerbMetadata, collect and validate aspect variants across all forms (enforcing present-tense variant consistency), serialize to roots.csv, and verify errors.csv parity against baseline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define immutable dataclasses: InPlaceParseConfig, VerbMetadata, and LexicalVerb
- [x] #2 Implement pure form parsing and aspect variant collection across all 5 Cherokee verb forms
- [x] #3 Enforce present tense variant consistency between 3rd present and 1st present forms
- [x] #4 Preserve VerbMetadata flags (set_a, plural, animate_objects, entry_type) in hypothesis generation and validation
- [x] #5 Connect parse_chr_dict to FSTs built from chr-clean-inplace-config
- [x] #6 Implement pure serialization of LexicalVerb to roots.csv rows
- [x] #7 Maintain errors.csv format parity with zero new error cases relative to baseline
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Domain Types: Define immutable ParseData (single FST parse), VerbTemplate (coarse lexical core), VerbMetadata (pooled AspectVariants & paradigm flags), and LexicalVerb = VerbTemplate x VerbMetadata.\n2. FST Integration: Connect parse_chr_dict to compile/load graphs from chr-clean-inplace-config and parse to ParseData.\n3. Form Parsing & Consistency: Project ParseData to VerbTemplate, enforce variant equality between 1st/3rd present, and accumulate form variants into VerbMetadata.\n4. Validation & Forward Inflection: Validate LexicalVerb against all row forms via exact ParseData reconstruction.\n5. Serialization & Parity: Serialize LexicalVerb to roots.csv (with variant columns) and verify zero new errors in errors.csv.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
User confirmed design decisions:
1. Serialization: Emit distinct variant columns in roots.csv: variant_present, variant_incompletive, variant_completive, variant_immediate, variant_infinitive.
2. Grammar generation: Compile chr-clean-inplace-config to a dedicated directory and configure YAML_DIR.
3. Pure functional architecture: Immutable frozen dataclasses (AspectVariants, InPlaceParseConfig, VerbMetadata, LexicalVerb) with IO strictly on boundaries.
4. Consistency: Enforce variant_present(3rd_present) == variant_present(1st_present).
5. Parity: Exact 9-column signature in errors.csv and zero new regressions against baseline.

\nRefinement: Dropped obsolete 'rules' field (fixed value '+'). Added 'h_alt_tag' to VerbTemplate and LexicalVerb product type so alternating trigger forms know precisely which mutation tag to apply.

\nRefinement: VerbTemplate comes from coarse-graining a single parse, so it holds only one root (the root of that specific parse). The pairing of h_root and glottal_root is resolved across forms and held on the LexicalVerb product type along with h_alt_tag.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored parse_chr_dict to a pure functional domain architecture with immutable frozen dataclasses (ParseData, VerbTemplate, AspectVariants, VerbMetadata, LexicalVerb) with IO strictly at pipeline boundaries. Connected parsing and validation to chr-clean-inplace-config compiled into chr-inplace-generated. Updated in-place lattice parsing with slot mask intersection, enforced present-tense variant consistency (template_3sg.variant == template_1sg.variant), and collected aspect variants across all forms into VerbMetadata. Updated forward inflection in reconstruct.py to support in-place tag strings, prepronominal prefixes (DIST=de/di, WI), and exact variant dispatch. Serialized LexicalVerb into roots.csv with exact 23 columns (including individual aspect variant columns) and preserved exact 9-column signature on errors.csv. Verified zero new error cases relative to baseline (0 new errors, 39 baseline errors fixed, roots increased from 913 to 1033) and all 412 test cases in the test suite pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->
