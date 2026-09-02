---
id: TASK-102.1
title: Measure and record baseline FST metrics for chr-generated
status: In Progress
assignee:
  - '@subagent'
created_date: '2026-09-02 19:51'
updated_date: '2026-09-02 20:14'
labels: []
dependencies: []
modified_files:
  - scratch/benchmark_fst.py
  - scratch/baseline_metrics.json
  - scratch/baseline_metrics.md
parent_task_id: TASK-102
priority: high
type: task
ordinal: 102000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a benchmarking utility to measure and document the baseline FST metrics (state count, arc count, graph compilation time, FST file size on disk, and corpus parse time) for the existing chr-generated grammar.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create a benchmarking script in scratch/ to extract FST statistics from parC compiled graphs
- [x] #2 Measure open inflect graph states, arcs, file size, and compilation time for chr-generated
- [x] #3 Measure open parse graph states, arcs, file size, and compilation time for chr-generated
- [x] #4 Measure 100-row parse runtime on chr-corpus/corpus.csv
- [x] #5 Save baseline results as reference JSON/Markdown
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Develop benchmarking script in scratch/benchmark_fst.py to compile open inflect and parse graphs for chr-generated and extract FST stats (states, arcs, disk size, compilation time).\n2. Measure open inflect graph metrics for chr-generated (state count, arc count, file size, compile time).\n3. Measure open parse graph metrics for chr-generated (state count, arc count, file size, compile time).\n4. Measure 100-row dictionary parsing benchmark on the first 100 valid verb rows of chr-corpus/corpus.csv using parse_chr_dict.\n5. Output and format baseline metrics into scratch/baseline_metrics.json and scratch/baseline_metrics.md.\n6. Track modified files in backlog, verify all acceptance criteria, commit incrementally, and report completion to supervisor.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
### Summary of Changes

Implemented benchmarking script `scratch/benchmark_fst.py` and established comprehensive baseline FST metrics for the Cherokee verb grammar (`chr-generated`) prior to the in-place morpheme tag migration:

1. **Benchmarking Script (`scratch/benchmark_fst.py`)**:
   - Automated measurement of open inflect and open parse graphs (states, arcs, disk footprint, cold compilation time, and cached load time).
   - Automated dictionary parsing benchmark on the first 100 valid verb rows in `chr-corpus/corpus.csv` using `parse_chr_dict` (measuring derivation, validation, throughput, and latency).
   - Generates machine-readable JSON (`scratch/baseline_metrics.json`) and human-readable Markdown (`scratch/baseline_metrics.md`).

2. **Recorded Baseline FST Graph Metrics**:
   - **Open Inflect Graph (standard)**: 578,015 states, 1,963,760 arcs, 36.58 MB disk size, 3.13s cold compilation, 0.15s cached load.
   - **Open Inflect Graph (nd_cleanup)**: 578,015 states, 2,527,626 arcs, 45.18 MB disk size, 3.45s cold compilation, 0.18s cached load.
   - **Open Parse Graph (active parser)**: 578,015 states, 2,527,626 arcs, 45.18 MB disk size, 2.15s inversion, 5.53s total cold compilation, 0.19s cached load.

3. **Recorded Corpus Parsing Benchmark (100 Valid Verb Rows)**:
   - Evaluated first 100 valid verb rows across 131 rows of `chr-corpus/corpus.csv`.
   - Total parse time: 30.80s (throughput: 3.25 rows/sec).
   - Mean latency: 288.52 ms/row (median: 260.84 ms/row, min: 110.52 ms, max: 681.39 ms).
   - Compiler initialization time: 0.24s.
<!-- SECTION:FINAL_SUMMARY:END -->
