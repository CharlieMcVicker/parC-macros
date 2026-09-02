---
id: TASK-102
title: 'FST Optimization: Migrate Cherokee Verb Grammar to In-Place Morpheme Tags'
status: In Progress
assignee:
  - '@antigravity'
created_date: '2026-09-02 19:51'
updated_date: '2026-09-02 20:14'
labels: []
dependencies: []
documentation:
  - >-
    backlog/docs/specifications/doc-1 -
    In-Place-Morpheme-Tags-and-FST-State-Space-Optimization.md
priority: high
type: feature
ordinal: 101000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comprehensive architectural initiative to migrate Cherokee verb grammar from trailing post-[EOW] feature labels to in-place adjacent morpheme tags ([PrefixClass][Pro], [AspectClass][Aspect], [TenseClass][Tense]), eliminating long-distance FST dependencies, shrinking Cartesian tag domains by >450x, and verifying full parity with baseline corpus parsing. See doc-1 for detailed specification.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Record baseline FST metrics for chr-generated
- [ ] #2 Configure chr-inplace-config with in-place tags and patterns
- [ ] #3 Update generate_markers.py to generate in-place string_map rules and global_markers paradigm
- [ ] #4 Generate chr-inplace-generated and compile open inflect/parse FSTs
- [ ] #5 Benchmark in-place FST size and compilation gains against baseline
- [ ] #6 Verify 100% dictionary parsing parity on chr-corpus/corpus.csv
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Execute TASK-102.1 via subagent: benchmark chr-generated baseline metrics and record in scratch/baseline_metrics.json.
2. Execute TASK-102.2 via subagent: set up chr-inplace-config with in-place tags, phoneme groups, open_root_template, and local drop rules.
3. Execute TASK-102.3 via subagent: enhance generate_markers.py to produce in-place 2-tag string_map rules and global_markers paradigm.
4. Execute TASK-102.4 via subagent: generate chr-inplace-generated and verify parC compilation of open inflect/parse graphs.
5. Execute TASK-102.5 via subagent: benchmark chr-inplace-generated gains and generate comparative report.
6. Execute TASK-102.6 via subagent: adapt parse_chr_dict for in-place tags and verify 100% dictionary parity against roots.csv.
7. Merge subagent branches, verify all tests pass, and close TASK-102.
<!-- SECTION:PLAN:END -->
