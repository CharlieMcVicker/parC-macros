# Cherokee Verb Grammar: In-Place Morpheme Tag Optimization - Comparative Benchmark Report

## 1. Executive Summary

This report provides an empirical before-and-after benchmark comparing the Cherokee verb grammar in `parC-macros`:
- **Baseline Grammar** (`chr-generated`): Relies on trailing morpheme feature tags (`[aspect_class=...]`, `[prefix_class=...]`, `[tense_present_class=...]`, `[aspect=...]`, `[pronominal=...]`, `[tense=...]`) appended after `[EOW]`. In open parsing and open inflection (`infer_lexical_features=True`), intermediate states must maintain hypotheses across the entire verb root and suffixes, resulting in Cartesian state space explosion.
- **Optimized In-Place Grammar** (`chr-inplace-generated`): Migrated under [TASK-102](file:///Users/julietmcvicker/code/parC-macros/backlog/docs/specifications/doc-1%20-%20In-Place-Morpheme-Tags-and-FST-State-Space-Optimization.md) to local 2-tag replacement rules (`[PrefixClass][Pro]`, `[AspectClass][Aspect]`, `[TenseClass][Tense]`) positioned directly within the stem template (`[BOW][PrefixClass][Pro]<Stem>[AspectClass][Aspect][TenseClass][Tense][EOW]`).

### Key Highlights & Results:
- **States**: Reduced from **578,015** to **956** (**99.83% reduction**)
- **Arcs**: Reduced from **2,527,626** to **19,130** (**99.24% reduction**)
- **FST Disk Footprint**: Reduced from **45.18 MB** to **0.3 MB** (**99.33% reduction**)
- **Cold Compilation Time**: Dropped from **5.5347s** to **0.074s** (**74.79x speedup** / **98.66% reduction**)
- **Graph Inversion Time**: Dropped from **2.1498s** to **0.0101s** (**212.85x speedup**)
- **Cached Load Time**: Dropped from **0.1866s** to **0.0008s** (**233.25x speedup**)
- **100-Row Parse Runtime**: **1.05x faster** (4.91% runtime reduction), processing 581 forms across 100 rows in **0.3853s** vs **0.4052s** on baseline.

- **Git Branch**: `inplace-gloss-template` (`f741bb85`)
- **Python**: `/opt/homebrew/Caskroom/miniconda/base/envs/parC/bin/python`
- **Execution Timestamp**: `2026-09-02T15:50:41-0500`

---

## 2. Graph Metrics Comparison Table

| Graph Configuration | Metric | Baseline (`chr-generated`) | In-Place (`chr-inplace-generated`) | Reduction % | Speedup Factor |
|---|---|---|---|---|---|
| **Active Parser** (`open_parse_nd_cleanup`) | **States** | 578,015 | 956 | **-99.83%** | 604.6x |
| | **Arcs** | 2,527,626 | 19,130 | **-99.24%** | 132.1x |
| | **Disk Size** | 45.18 MB | 0.3 MB | **-99.33%** | 149.2x |
| | **Cold Compile** | 5.5347 s | 0.074 s | **-98.66%** | **74.79x** |
| | **Inversion Time** | 2.1498 s | 0.0101 s | **-99.53%** | **212.85x** |
| | **Cached Load** | 0.1866 s | 0.0008 s | **-99.57%** | **233.25x** |
| **Open Inflect** (`open_inflect_standard`) | **States** | 578,015 | 956 | **-99.83%** | 604.6x |
| | **Arcs** | 1,963,760 | 19,029 | **-99.03%** | 103.2x |
| | **Disk Size** | 36.58 MB | 0.3 MB | **-99.18%** | 121.4x |
| | **Cold Compile** | 3.1286 s | 0.0598 s | **-98.09%** | **52.32x** |
| | **Cached Load** | 0.1541 s | 0.0009 s | **-99.42%** | **171.22x** |
| **Open Inflect Pre-Parse** (`open_inflect_nd_cleanup`) | **States** | 578,015 | 956 | **-99.83%** | 604.6x |
| | **Arcs** | 2,527,626 | 19,130 | **-99.24%** | 132.1x |
| | **Disk Size** | 45.18 MB | 0.3 MB | **-99.33%** | 149.2x |
| | **Cold Compile** | 3.4451 s | 0.0603 s | **-98.25%** | **57.13x** |
| **Open Parse Raw** (`open_parse_standard`) | **States** | 578,015 | 956 | **-99.83%** | 604.6x |
| | **Arcs** | 1,963,760 | 19,029 | **-99.03%** | 103.2x |
| | **Disk Size** | 36.58 MB | 0.3 MB | **-99.18%** | 121.4x |
| | **Cold Compile** | 4.6497 s | 0.0696 s | **-98.5%** | **66.81x** |

---

## 3. 100-Row Corpus Parse Runtime Comparison

Benchmarked against the first **100 valid verb rows** in `chr-corpus/corpus.csv` (identical to TASK-102.1 baseline rows #8 through #230).

### 3.1 All Conjugated Forms Across 100 Rows (581 Forms Total)

| Metric | Baseline (`chr-generated`) | In-Place (`chr-inplace-generated`) | Gain / Difference |
|---|---|---|---|
| **Valid Rows Benchmarked** | 100 | 100 | Identical |
| **Total Forms Evaluated** | 581 | 581 | Identical (avg 5.8 forms/row) |
| **Parser Initialization Time** | 0.5395 s | 0.0877 s | **6.15x faster init** |
| **Total Parse Runtime** | 0.4052 s | 0.3853 s | **-4.91% (1.05x speedup)** |
| **Mean Time Per Row** | 4.05 ms | 3.85 ms | **0.2 ms saved per row** |
| **Median Time Per Row** | 3.87 ms | 3.78 ms | **0.09 ms saved per row** |
| **Throughput (Rows/sec)** | 246.82 rows/s | 259.56 rows/s | **+12.74 rows/s** |
| **Throughput (Forms/sec)** | 1434.01 forms/s | 1508.06 forms/s | **+74.05 forms/s** |

### 3.2 Primary Present Forms (100 Forms)

| Metric | Baseline (`chr-generated`) | In-Place (`chr-inplace-generated`) | Gain / Difference |
|---|---|---|---|
| **Total Forms Evaluated** | 100 | 100 | Identical |
| **Total Parse Runtime** | 0.0678 s | 0.0419 s | **-38.25% (1.62x speedup)** |
| **Mean Time Per Form** | 0.68 ms | 0.42 ms | **0.26 ms saved** |
| **Median Time Per Form** | 0.43 ms | 0.38 ms | **0.05 ms saved** |
| **Throughput (Forms/sec)** | 1475.32 forms/s | 2389.25 forms/s | **+913.93 forms/s** |

---

## 4. Backwards-Compatible `read_labels` Adaptation

To support parses produced by `chr-inplace-generated`, `read_labels()` in `parse_chr_dict/parse.py` was extended to extract in-place slot tags while preserving backwards-compatibility:
- **Slot Tag Mappings**:
  - `[PrefixClass=...]` $\to$ `prefix_class`
  - `[Pro=...]` $\to$ `pronominal`
  - `[AspectClass=...]` $\to$ `aspect_class`
  - `[Aspect=...]` $\to$ `aspect`
  - `[TenseClass=...]` $\to$ `tense_present_class`
  - `[Tense=...]` $\to$ `tense`
- **Root Extraction**: In-place tags are extracted and cleanly stripped from the root form without altering non-feature mutation markers (such as `[H_NONE]`, `[H_GLOT]`, `[H_DROP]`, `[H_LAT]`, `[H_VOWEL]`).
- **Backwards Compatibility**: Classical trailing-tag strings (`[BOW]root[EOW][feat=val]...`) continue to parse with 100% fidelity.

---

## 5. Architectural Analysis: Why In-Place Tags Succeeded

### 5.1 The Root Cause of the Baseline Explosion
In `chr-generated`, all morpheme features (`[aspect_class=...]`, `[prefix_class=...]`, `[tense_present_class=...]`, `[aspect=...]`, `[pronominal=...]`, `[tense=...]`) were emitted at the very end of the string after `[EOW]`. In open inflection and parsing:
1. Intermediate states were required to remember every combination of `(aspect_class, prefix_class, tense_class, pronominal, aspect, tense)` across the entire root `<Phone>*` and all phonological rewrite rules.
2. This created a massive Cartesian product of hypotheses: $7 \text{ prefix classes} \times 92 \text{ aspect classes} \times 2 \text{ tense classes} \times 22 \text{ pronouns} \times 5 \text{ aspects} \times 7 \text{ tenses} = \mathcal{O}(10^7)$ theoretical states, resulting in **578,015 actual states** and **2.5 million arcs**.

### 5.2 The In-Place Morpheme Solution
By structuring the underlying representation as:
```
[BOW][PrefixClass=...][Pro=...]<Root>[AspectClass=...][Aspect=...][TenseClass=...][Tense=...][EOW]
```
each morphological rule acts strictly locally:
- `pro_replace`: Replaces adjacent `[PrefixClass=...][Pro=...]` with prefix phonemes immediately at the start of the word.
- `aspect_replace`: Replaces adjacent `[AspectClass=...][Aspect=...]` with aspect suffixes immediately after the root.
- `tense_replace`: Replaces adjacent `[TenseClass=...][Tense=...]` with tense suffixes at the end of the word.
Because state hypotheses are resolved locally at their exact positions, the transducer does **not** need to carry cross-word dependencies, collapsing the state space from **578,015 states down to 956 states** (a **99.83% reduction**).

---

## 6. Reproducing This Benchmark

To re-run this comparative benchmark at any time using the parC conda environment:
```bash
/opt/homebrew/Caskroom/miniconda/base/envs/parC/bin/python scratch/comparative_benchmark.py
```
