---
id: TASK-102
title: 'FST Optimization: Migrate Cherokee Verb Grammar to In-Place Morpheme Tags'
status: To Do
assignee: []
created_date: '2026-09-02 19:51'
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
- [ ] #1 Record baseline FST metrics for chr-generated
- [ ] #2 Configure chr-inplace-config with in-place tags and patterns
- [ ] #3 Update generate_markers.py to generate in-place string_map rules and global_markers paradigm
- [ ] #4 Generate chr-inplace-generated and compile open inflect/parse FSTs
- [ ] #5 Benchmark in-place FST size and compilation gains against baseline
- [ ] #6 Verify 100% dictionary parsing parity on chr-corpus/corpus.csv
<!-- AC:END -->
