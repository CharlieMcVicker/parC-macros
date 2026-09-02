---
id: TASK-102.5
title: Benchmark in-place FST size and compilation gains against baseline
status: Done
assignee:
  - '@subagent'
created_date: '2026-09-02 19:51'
updated_date: '2026-09-02 20:51'
labels: []
dependencies:
  - TASK-102.4
modified_files:
  - parse_chr_dict/parse.py
  - tests/test_parse_chr_dict_baseline.py
  - tests/test_comparative_benchmark.py
  - scratch/comparative_benchmark.py
  - scratch/comparative_benchmark.json
  - scratch/comparative_benchmark.md
parent_task_id: TASK-102
priority: high
type: task
ordinal: 106000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the benchmarking utility against chr-inplace-generated to extract states, arcs, compile times, and disk sizes. Compare directly against baseline metrics recorded in TASK-102.1 and produce a detailed comparative gain report.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Measure states, arcs, file size, and compilation time for chr-inplace-generated open inflect graph
- [x] #2 Measure states, arcs, file size, and compilation time for chr-inplace-generated open parse graph
- [x] #3 Measure 100-row parse runtime comparison
- [x] #4 Generate comparative markdown report with percentage reductions in states, arcs, and time
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Adapt read_labels in parse_chr_dict/parse.py to extract and strip in-place slot tags ([PrefixClass=...], [Pro=...], [AspectClass=...], [Aspect=...], [TenseClass=...], [Tense=...]) and map them to standard feature names in a backwards-compatible manner.
2. Add unit tests for read_labels verifying both legacy trailing-tag format and new in-place format with mutation tags, ensuring all 364+ tests pass.
3. Extend / implement benchmark runner to measure in-place FST graph metrics (Open Inflect and Open Parse states, arcs, compile times, file sizes) for AC 1 and AC 2.
4. Execute 100-row parse runtime benchmark on chr-corpus/corpus.csv matching the 100 valid verb rows from baseline for AC 3.
5. Compute comparative gain metrics (percentage reductions for states, arcs, disk sizes, compile times, and parse times) and generate scratch/comparative_benchmark.json and scratch/comparative_benchmark.md for AC 4.
6. Verify all pytest unit tests pass cleanly.
7. Track modified files in backlog, commit incrementally with git, check off ACs, add PR summary, and report results to supervisor via send_message.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## PR Summary: TASK-102.5 - Benchmark in-place FST size and compilation gains against baseline

### Executive Overview
Completed comprehensive empirical benchmarking comparing the baseline trailing-tag Cherokee verb grammar (`chr-generated`) against the optimized in-place morpheme tag grammar (`chr-inplace-generated`). The in-place morpheme tag migration resolves the Cartesian state space explosion by constraining morpheme replacements locally within the stem template.

### Key Comparative Metrics
| Metric | Baseline (`chr-generated`) | In-Place (`chr-inplace-generated`) | Reduction / Speedup |
|---|---|---|---|
| **Active Parser States** | 578,015 | 956 | **-99.83%** (604.6x reduction) |
| **Active Parser Arcs** | 2,527,626 | 19,130 | **-99.24%** (132.1x reduction) |
| **FST File Size** | 45.18 MB | 0.30 MB (317,618 bytes) | **-99.33%** (149.2x reduction) |
| **Cold Compilation Time** | 5.5347 s | 0.0740 s | **74.79x speedup** (-98.66%) |
| **Graph Inversion Time** | 2.1498 s | 0.0101 s | **212.85x speedup** (-99.53%) |
| **Cached Load Time** | 0.1866 s | 0.0008 s | **233.25x speedup** (-99.57%) |
| **100-Row Parse (581 forms)** | 0.4052 s | 0.3853 s | **1.05x speedup** (-4.91%) |
| **Primary 100 Forms Parse** | 0.0678 s | 0.0419 s | **1.62x speedup** (-38.25%) |

### Acceptance Criteria Fulfillment
- **AC 1 (Open Inflect Graph)**: Measured states (956), arcs (19,029), file size (0.30 MB), and cold compilation (0.0598s) on `chr-inplace-generated`.
- **AC 2 (Open Parse Graph)**: Measured states (956), arcs (19,130), file size (0.30 MB), inversion (0.0101s), and cold compilation (0.0740s) on `chr-inplace-generated`.
- **AC 3 (100-Row Parse Comparison & read_labels Adaptation)**:
  - Adapted `read_labels` in `parse_chr_dict/parse.py` to extract and strip in-place slot tags (`PrefixClass`, `Pro`, `AspectClass`, `Aspect`, `TenseClass`, `Tense`) into standard feature names (`prefix_class`, `pronominal`, `aspect_class`, `aspect`, `tense_present_class`, `tense`) with 100% backwards-compatibility for legacy trailing tags.
  - Benchmarked the first 100 valid verb rows from `chr-corpus/corpus.csv` across 581 total forms.
- **AC 4 (Comparative Reporting)**:
  - Generated `scratch/comparative_benchmark.json` with structured before-and-after comparison schema.
  - Generated `scratch/comparative_benchmark.md` with executive summary, graph comparison tables, runtime analysis, and architectural explanation.

### Validation
- Added automated validation in `tests/test_comparative_benchmark.py` and extended `tests/test_parse_chr_dict_baseline.py`.
- 100% test pass rate across all 367 unit tests in `parC-macros` using the designated parC environment (`/opt/homebrew/Caskroom/miniconda/base/envs/parC/bin/pytest`).
<!-- SECTION:FINAL_SUMMARY:END -->
