# Cherokee Verb Grammar - Baseline FST Metrics

## 1. Executive Summary & Overview

This report records the baseline finite-state transducer (FST) metrics for the Cherokee verb grammar in `parC-macros` (`chr-generated`) prior to the in-place morpheme tag migration ([doc-1](file:///Users/julietmcvicker/code/parC-macros/backlog/docs/specifications/doc-1%20-%20In-Place-Morpheme-Tags-and-FST-State-Space-Optimization.md)).

- **Repository**: `parC-macros`
- **Git Branch**: `subagent-Baseline-Metrics-Benchmark-Subagent-self-bf14b2ff` (`b1c721f8`)
- **Python Interpreter**: `/opt/homebrew/Caskroom/miniconda/base/envs/parC/bin/python`
- **Execution Timestamp**: `2026-09-02T15:12:59-0500`

---

## 2. Finite-State Transducer (FST) Graph Metrics

The Cherokee verb grammar currently relies on trailing feature labels (`[aspect_class=...]`, `[prefix_class=...]`, `[tense_present_class=...]`, etc.) positioned after `[EOW]`. In open parsing and open inflection (`infer_lexical_features=True`), intermediate states must maintain hypotheses across the entire verb root and suffixes, resulting in Cartesian state space explosion.

### 2.1 Summary Metrics Table

| Graph | States | Arcs | File Size (MB) | File Size (Bytes) | Cold Compile Time (s) | Cached Load Time (s) | Notes |
|---|---|---|---|---|---|---|---|
| **Open Inflect** (`nd_cleanup=False`) | 578,015 | 1,963,760 | 36.58 MB | 38,356,406 | 3.1286s | 0.1541s | Standard inflection graph (`get_inflect_graph`) |
| **Open Inflect** (`nd_cleanup=True`) | 578,015 | 2,527,626 | 45.18 MB | 47,378,262 | 3.4451s | 0.1833s | Pre-inversion graph for parser |
| **Open Parse** (`nd_cleanup=True`) | 578,015 | 2,527,626 | 45.18 MB | 47,378,262 | 5.5347s | 0.1866s | **Active parser graph** (`get_parse_graph`) |
| **Open Parse** (`nd_cleanup=False`) | 578,015 | 1,963,760 | 36.58 MB | 38,356,406 | 4.6497s | 0.1575s | Parse graph inverted without cleanup |

### 2.2 Key FST Observations

1. **State Space Explosion**: Both open inflect and open parse graphs contain **578,015 states** and up to **2,527,626 arcs**.
2. **On-Disk Footprint**: The compiled parser graph (`open_parse_infer_nd_cleanup.fst`) consumes **45.18 MB** (47,378,262 bytes) of disk space.
3. **Inversion Overhead**: Inverting and optimizing the 578,015-state inflection graph requires **2.1498s**.
4. **Cache Load Time**: Reading the binary OpenFst file from disk takes **0.1866s**.

---

## 3. Dictionary Corpus Parsing Benchmark (100 Valid Verb Rows)

Benchmarked using `parse_chr_dict` on the first **100 valid verb rows** from `corpus.csv`.

### 3.1 Performance Metrics

| Metric | Value |
|---|---|
| **Target Valid Rows** | 100 |
| **Total Corpus Rows Examined** | 131 |
| **Valid Rows Successfully Parsed** | 100 |
| **Compiler Initialization Time** | 0.237 s |
| **Total 100-Row Parse Time** | 30.8009 s |
| **Total Elapsed (Init + Parse)** | 31.0379 s |
| **Mean Time Per Row** | 288.52 ms |
| **Median Time Per Row** | 260.84 ms |
| **Min Time Per Row** | 110.52 ms |
| **Max Time Per Row** | 681.39 ms |
| **Throughput** | 3.25 rows/second |

### 3.2 Sample Verified Entries

- **First 5 Valid Entries**:
  - #8 (it’s bouncing)
  - #9 (he/she is limping)
  - #10 (he/she is bouncing it)
  - #11 (he/she is putting on a belt)
  - #14 (he/she is praying)
- **Last 5 Valid Entries**:
  - #222 (he/she is taking it somewhere by hand)
  - #224 (he/she is quilting it)
  - #226 (he/she is imitating him/her)
  - #229 (he/she is swimming (refers to propelling oneself through the water))
  - #230 (it’s thundering)

---

## 4. Optimization Target Comparison

The in-place morpheme tag migration (`chr-inplace-config` / `chr-inplace-generated`) aims to replace trailing post-`[EOW]` features with strictly local 2-tag replacement rules (`[PrefixClass][Pro]`, `[AspectClass][Aspect]`, `[TenseClass][Tense]`).

| Target Metric | Baseline (`chr-generated`) | Expected In-Place (`chr-inplace-generated`) | Projected Gain |
|---|---|---|---|
| **Open Inflect States** | 578,015 | < 15,000 | > 95% reduction |
| **Open Parse Arcs** | 2,527,626 | < 100,000 | > 95% reduction |
| **FST Disk Size** | 45.18 MB | < 3 MB | > 90% reduction |
| **Compile Time** | 3.1286 s | < 1.0 s | > 3x speedup |
| **100-Row Parse Runtime** | 30.8009 s | Faster | Maintained or improved |

---

## 5. Reproducing This Benchmark

To re-run this benchmark at any time using the parC conda environment:
```bash
/opt/homebrew/Caskroom/miniconda/base/envs/parC/bin/python scratch/benchmark_fst.py
```

To benchmark only graphs or customize row counts:
```bash
/opt/homebrew/Caskroom/miniconda/base/envs/parC/bin/python scratch/benchmark_fst.py --num-corpus-rows 50
```
