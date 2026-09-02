#!/usr/bin/env python3
"""
Benchmarking utility to measure and document baseline FST metrics for Cherokee verb grammar.

Measures:
1. Open Inflect Graph: states, arcs, disk size (.fst), cold compilation time, and cached load time.
2. Open Parse Graph: states, arcs, disk size (.fst), invert & optimize time, total compilation time, and cached load time.
3. Corpus Parse Runtime: 100-row parse runtime on the first 100 valid verb rows in chr-corpus/corpus.csv.
4. Outputs structured results to JSON and Markdown.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
DEFAULT_GRAMMAR_DIR = REPO_ROOT / "chr-generated"
DEFAULT_CORPUS_PATH = REPO_ROOT / "chr-corpus" / "corpus.csv"
DEFAULT_JSON_OUTPUT = REPO_ROOT / "scratch" / "baseline_metrics.json"
DEFAULT_MD_OUTPUT = REPO_ROOT / "scratch" / "baseline_metrics.md"

if "YAML_DIR" not in os.environ:
    os.environ["YAML_DIR"] = str(DEFAULT_GRAMMAR_DIR)


def count_fst_arcs(fst: Any) -> int:
    """Calculates the total number of arcs across all states in an Fst."""
    return sum(fst.num_arcs(s) for s in fst.states())


def get_git_info(repo_dir: Path) -> Dict[str, str]:
    """Retrieves current git commit hash and branch name."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_dir, text=True
        ).strip()
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=repo_dir, text=True
        ).strip()
        return {"commit": commit, "branch": branch}
    except Exception:
        return {"commit": "unknown", "branch": "unknown"}


def benchmark_open_inflect_graph(
    paradigm_name: str = "verb",
    infer_lexical_features: bool = True,
    non_deterministic_cleanup: bool = False,
    cache_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Measures open inflect graph metrics:
    - State count
    - Arc count
    - File size on disk
    - Cold compilation time
    - Cache load time
    """
    import parC.grammar.paradigm_compilation as pc
    from parC.grammar.blueprints.paradigms import StageCascadeBlueprint

    blueprint = StageCascadeBlueprint.from_paradigm(paradigm_name)
    base_cache_key = pc.get_paradigm_cache_key(paradigm_name)

    suffix_parts = []
    if infer_lexical_features:
        suffix_parts.append("infer")
    if non_deterministic_cleanup:
        suffix_parts.append("nd_cleanup")
    suffix = f"_{'_'.join(suffix_parts)}" if suffix_parts else ""
    standard_cache_key = f"{base_cache_key}_open_inflect{suffix}"

    temp_cache_key = f"_bench_cold_inflect_{int(time.time() * 1000)}"
    t0 = time.perf_counter()
    cold_fst = blueprint.build_open_inflect_graph(
        root_regex="<Phone>*",
        infer_lexical_features=infer_lexical_features,
        non_deterministic_cleanup=non_deterministic_cleanup,
        cache_key=temp_cache_key,
    )
    cold_compile_time = time.perf_counter() - t0

    num_states = cold_fst.num_states()
    num_arcs = count_fst_arcs(cold_fst)

    if cache_dir and cache_dir.exists():
        for pattern in [f"{temp_cache_key}*"]:
            for f in glob.glob(str(cache_dir / pattern)):
                try:
                    os.remove(f)
                except OSError:
                    pass

    fst_file_path = (
        cache_dir / f"{standard_cache_key}.fst" if cache_dir else None
    )
    if fst_file_path and not fst_file_path.exists():
        pc.save_cached_fst(standard_cache_key, cold_fst)

    file_size_bytes = fst_file_path.stat().st_size if (fst_file_path and fst_file_path.exists()) else None

    cache_load_time = None
    if fst_file_path and fst_file_path.exists():
        import pynini
        t_load_0 = time.perf_counter()
        _ = pynini.Fst.read(str(fst_file_path))
        cache_load_time = time.perf_counter() - t_load_0

    return {
        "paradigm": paradigm_name,
        "infer_lexical_features": infer_lexical_features,
        "non_deterministic_cleanup": non_deterministic_cleanup,
        "states": num_states,
        "arcs": num_arcs,
        "cold_compilation_seconds": round(cold_compile_time, 4),
        "cached_load_seconds": round(cache_load_time, 4) if cache_load_time else None,
        "file_path": str(fst_file_path) if fst_file_path else None,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": round(file_size_bytes / (1024 * 1024), 2) if file_size_bytes else None,
        "cache_key": standard_cache_key,
    }


def benchmark_open_parse_graph(
    paradigm_name: str = "verb",
    infer_lexical_features: bool = True,
    non_deterministic_cleanup: bool = True,
    cache_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Measures open parse graph metrics:
    - State count
    - Arc count
    - File size on disk
    - Inversion + optimization time
    - Total compilation time (inflect compile + inversion)
    - Cache load time
    """
    import parC.grammar.paradigm_compilation as pc
    from parC.grammar.blueprints.paradigms import StageCascadeBlueprint
    import pynini

    blueprint = StageCascadeBlueprint.from_paradigm(paradigm_name)
    base_cache_key = pc.get_paradigm_cache_key(paradigm_name)

    suffix_parts = []
    if infer_lexical_features:
        suffix_parts.append("infer")
    if non_deterministic_cleanup:
        suffix_parts.append("nd_cleanup")
    suffix = f"_{'_'.join(suffix_parts)}" if suffix_parts else ""
    standard_parse_key = f"{base_cache_key}_open_parse{suffix}"

    temp_cache_key = f"_bench_cold_parse_{int(time.time() * 1000)}"
    t0 = time.perf_counter()
    inflect_fst = blueprint.build_open_inflect_graph(
        root_regex="<Phone>*",
        infer_lexical_features=infer_lexical_features,
        non_deterministic_cleanup=non_deterministic_cleanup,
        cache_key=temp_cache_key,
    )
    t_inflect_done = time.perf_counter()
    inflect_compile_time = t_inflect_done - t0

    t_invert_0 = time.perf_counter()
    parse_fst = pynini.invert(inflect_fst).optimize()
    invert_time = time.perf_counter() - t_invert_0
    total_compile_time = inflect_compile_time + invert_time

    num_states = parse_fst.num_states()
    num_arcs = count_fst_arcs(parse_fst)

    if cache_dir and cache_dir.exists():
        for pattern in [f"{temp_cache_key}*"]:
            for f in glob.glob(str(cache_dir / pattern)):
                try:
                    os.remove(f)
                except OSError:
                    pass

    fst_file_path = (
        cache_dir / f"{standard_parse_key}.fst" if cache_dir else None
    )
    if fst_file_path and not fst_file_path.exists():
        pc.save_cached_fst(standard_parse_key, parse_fst)

    file_size_bytes = fst_file_path.stat().st_size if (fst_file_path and fst_file_path.exists()) else None

    cache_load_time = None
    if fst_file_path and fst_file_path.exists():
        t_load_0 = time.perf_counter()
        _ = pynini.Fst.read(str(fst_file_path))
        cache_load_time = time.perf_counter() - t_load_0

    return {
        "paradigm": paradigm_name,
        "infer_lexical_features": infer_lexical_features,
        "non_deterministic_cleanup": non_deterministic_cleanup,
        "states": num_states,
        "arcs": num_arcs,
        "inversion_seconds": round(invert_time, 4),
        "cold_compilation_seconds": round(total_compile_time, 4),
        "cached_load_seconds": round(cache_load_time, 4) if cache_load_time else None,
        "file_path": str(fst_file_path) if fst_file_path else None,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": round(file_size_bytes / (1024 * 1024), 2) if file_size_bytes else None,
        "cache_key": standard_parse_key,
    }


def benchmark_corpus_parsing(
    corpus_path: Path,
    target_valid_rows: int = 100,
) -> Dict[str, Any]:
    """
    Measures dictionary parsing runtime across the first target_valid_rows valid verb rows
    in chr-corpus/corpus.csv using the parse_chr_dict derivation and validation pipeline.
    """
    from parse_chr_dict.create_aspect_class_csv import respell_consonants
    from parse_chr_dict.meta_label_compiler import (
        MetaConstraintCompiler,
        PRIMARY_ENTRY_TYPES,
        derive_hypotheses_for_forms,
    )
    from parse_chr_dict.reconstruct import validate_hypothesis
    from parse_chr_dict.__main__ import ENTRY_TYPE_FORMS

    fieldnames = [
        "corpus_id",
        "entry_no",
        "definition",
        "present",
        "present_1sg",
        "imperfective",
        "perfective",
        "imperative",
        "infinitive",
    ]

    t_init_0 = time.perf_counter()
    compiler = MetaConstraintCompiler()
    init_time = time.perf_counter() - t_init_0

    with open(corpus_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        next(reader)  # skip header
        all_rows = list(reader)

    valid_results: List[Dict[str, Any]] = []
    total_examined = 0
    row_times: List[float] = []

    t_parse_start = time.perf_counter()

    for idx, row in enumerate(all_rows):
        total_examined += 1
        r_start = time.perf_counter()
        row_written = False
        valid_hypotheses_count = 0
        matched_entry_type = None

        for entry_type in PRIMARY_ENTRY_TYPES:
            entry_forms = [
                (respell_consonants(row[parsing.corpus_key]), parsing)
                for parsing in ENTRY_TYPE_FORMS[entry_type.name]
                if row.get(parsing.corpus_key) and " " not in row[parsing.corpus_key]
            ]
            if not entry_forms:
                continue

            derived_hypotheses = derive_hypotheses_for_forms(entry_forms, compiler)
            if not derived_hypotheses:
                continue

            if entry_type.name.startswith("Stative"):
                derived_hypotheses = {
                    h for h in derived_hypotheses if h.aspect_class.startswith("stative")
                }

            valid_hypotheses = [
                h
                for h in derived_hypotheses
                if validate_hypothesis(h, row, entry_type, compiler=compiler)
            ]

            if valid_hypotheses:
                row_written = True
                valid_hypotheses_count = len(valid_hypotheses)
                matched_entry_type = entry_type.name
                break

        r_elapsed = time.perf_counter() - r_start

        if row_written:
            row_times.append(r_elapsed)
            valid_results.append(
                {
                    "row_index": idx,
                    "entry_no": row["entry_no"],
                    "definition": row["definition"],
                    "entry_type": matched_entry_type,
                    "valid_hypotheses": valid_hypotheses_count,
                    "parse_time_ms": round(r_elapsed * 1000, 2),
                }
            )

        if len(valid_results) >= target_valid_rows:
            break

    total_parse_time = time.perf_counter() - t_parse_start

    import statistics

    mean_time_ms = statistics.mean(row_times) * 1000 if row_times else 0
    median_time_ms = statistics.median(row_times) * 1000 if row_times else 0
    min_time_ms = min(row_times) * 1000 if row_times else 0
    max_time_ms = max(row_times) * 1000 if row_times else 0
    throughput = len(valid_results) / total_parse_time if total_parse_time > 0 else 0

    return {
        "target_valid_rows": target_valid_rows,
        "valid_rows_parsed": len(valid_results),
        "total_corpus_rows_examined": total_examined,
        "compiler_initialization_seconds": round(init_time, 4),
        "total_parse_seconds": round(total_parse_time, 4),
        "total_elapsed_with_init_seconds": round(init_time + total_parse_time, 4),
        "mean_ms_per_valid_row": round(mean_time_ms, 2),
        "median_ms_per_valid_row": round(median_time_ms, 2),
        "min_ms_per_valid_row": round(min_time_ms, 2),
        "max_ms_per_valid_row": round(max_time_ms, 2),
        "throughput_rows_per_second": round(throughput, 2),
        "first_5_entries": [f"#{r['entry_no']} ({r['definition']})" for r in valid_results[:5]],
        "last_5_entries": [f"#{r['entry_no']} ({r['definition']})" for r in valid_results[-5:]],
        "parsed_entries": valid_results,
    }


def generate_markdown_report(metrics: Dict[str, Any]) -> str:
    """Generates a clean, comprehensive markdown report summarizing the baseline metrics."""
    inflect_std = metrics["graphs"]["open_inflect_standard"]
    inflect_nd = metrics["graphs"]["open_inflect_nd_cleanup"]
    parse_active = metrics["graphs"]["open_parse_nd_cleanup"]
    parse_std = metrics["graphs"]["open_parse_standard"]
    corpus = metrics["corpus_benchmark"]
    env = metrics["environment"]

    lines = [
        "# Cherokee Verb Grammar - Baseline FST Metrics",
        "",
        "## 1. Executive Summary & Overview",
        "",
        f"This report records the baseline finite-state transducer (FST) metrics for the Cherokee verb grammar in `parC-macros` (`chr-generated`) prior to the in-place morpheme tag migration ([doc-1](file:///Users/julietmcvicker/code/parC-macros/backlog/docs/specifications/doc-1%20-%20In-Place-Morpheme-Tags-and-FST-State-Space-Optimization.md)).",
        "",
        "- **Repository**: `parC-macros`",
        f"- **Git Branch**: `{env.get('git_branch')}` (`{env.get('git_commit')[:8]}`)",
        f"- **Python Interpreter**: `{env.get('python_path')}`",
        f"- **Execution Timestamp**: `{env.get('timestamp')}`",
        "",
        "---",
        "",
        "## 2. Finite-State Transducer (FST) Graph Metrics",
        "",
        "The Cherokee verb grammar currently relies on trailing feature labels (`[aspect_class=...]`, `[prefix_class=...]`, `[tense_present_class=...]`, etc.) positioned after `[EOW]`. In open parsing and open inflection (`infer_lexical_features=True`), intermediate states must maintain hypotheses across the entire verb root and suffixes, resulting in Cartesian state space explosion.",
        "",
        "### 2.1 Summary Metrics Table",
        "",
        "| Graph | States | Arcs | File Size (MB) | File Size (Bytes) | Cold Compile Time (s) | Cached Load Time (s) | Notes |",
        "|---|---|---|---|---|---|---|---|",
        f"| **Open Inflect** (`nd_cleanup=False`) | {inflect_std['states']:,} | {inflect_std['arcs']:,} | {inflect_std['file_size_mb']} MB | {inflect_std['file_size_bytes']:,} | {inflect_std['cold_compilation_seconds']}s | {inflect_std['cached_load_seconds']}s | Standard inflection graph (`get_inflect_graph`) |",
        f"| **Open Inflect** (`nd_cleanup=True`) | {inflect_nd['states']:,} | {inflect_nd['arcs']:,} | {inflect_nd['file_size_mb']} MB | {inflect_nd['file_size_bytes']:,} | {inflect_nd['cold_compilation_seconds']}s | {inflect_nd['cached_load_seconds']}s | Pre-inversion graph for parser |",
        f"| **Open Parse** (`nd_cleanup=True`) | {parse_active['states']:,} | {parse_active['arcs']:,} | {parse_active['file_size_mb']} MB | {parse_active['file_size_bytes']:,} | {parse_active['cold_compilation_seconds']}s | {parse_active['cached_load_seconds']}s | **Active parser graph** (`get_parse_graph`) |",
        f"| **Open Parse** (`nd_cleanup=False`) | {parse_std['states']:,} | {parse_std['arcs']:,} | {parse_std['file_size_mb']} MB | {parse_std['file_size_bytes']:,} | {parse_std['cold_compilation_seconds']}s | {parse_std['cached_load_seconds']}s | Parse graph inverted without cleanup |",
        "",
        "### 2.2 Key FST Observations",
        "",
        f"1. **State Space Explosion**: Both open inflect and open parse graphs contain **{inflect_std['states']:,} states** and up to **{parse_active['arcs']:,} arcs**.",
        f"2. **On-Disk Footprint**: The compiled parser graph (`open_parse_infer_nd_cleanup.fst`) consumes **{parse_active['file_size_mb']} MB** ({parse_active['file_size_bytes']:,} bytes) of disk space.",
        f"3. **Inversion Overhead**: Inverting and optimizing the {parse_active['states']:,}-state inflection graph requires **{parse_active['inversion_seconds']}s**.",
        f"4. **Cache Load Time**: Reading the binary OpenFst file from disk takes **{parse_active['cached_load_seconds']}s**.",
        "",
        "---",
        "",
        "## 3. Dictionary Corpus Parsing Benchmark (100 Valid Verb Rows)",
        "",
        f"Benchmarked using `parse_chr_dict` on the first **{corpus['target_valid_rows']} valid verb rows** from `{DEFAULT_CORPUS_PATH.name}`.",
        "",
        "### 3.1 Performance Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **Target Valid Rows** | {corpus['target_valid_rows']} |",
        f"| **Total Corpus Rows Examined** | {corpus['total_corpus_rows_examined']} |",
        f"| **Valid Rows Successfully Parsed** | {corpus['valid_rows_parsed']} |",
        f"| **Compiler Initialization Time** | {corpus['compiler_initialization_seconds']} s |",
        f"| **Total 100-Row Parse Time** | {corpus['total_parse_seconds']} s |",
        f"| **Total Elapsed (Init + Parse)** | {corpus['total_elapsed_with_init_seconds']} s |",
        f"| **Mean Time Per Row** | {corpus['mean_ms_per_valid_row']} ms |",
        f"| **Median Time Per Row** | {corpus['median_ms_per_valid_row']} ms |",
        f"| **Min Time Per Row** | {corpus['min_ms_per_valid_row']} ms |",
        f"| **Max Time Per Row** | {corpus['max_ms_per_valid_row']} ms |",
        f"| **Throughput** | {corpus['throughput_rows_per_second']} rows/second |",
        "",
        "### 3.2 Sample Verified Entries",
        "",
        "- **First 5 Valid Entries**:",
    ]
    for item in corpus["first_5_entries"]:
        lines.append(f"  - {item}")

    lines.append("- **Last 5 Valid Entries**:")
    for item in corpus["last_5_entries"]:
        lines.append(f"  - {item}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## 4. Optimization Target Comparison",
            "",
            "The in-place morpheme tag migration (`chr-inplace-config` / `chr-inplace-generated`) aims to replace trailing post-`[EOW]` features with strictly local 2-tag replacement rules (`[PrefixClass][Pro]`, `[AspectClass][Aspect]`, `[TenseClass][Tense]`).",
            "",
            "| Target Metric | Baseline (`chr-generated`) | Expected In-Place (`chr-inplace-generated`) | Projected Gain |",
            "|---|---|---|---|",
            f"| **Open Inflect States** | {inflect_std['states']:,} | < 15,000 | > 95% reduction |",
            f"| **Open Parse Arcs** | {parse_active['arcs']:,} | < 100,000 | > 95% reduction |",
            f"| **FST Disk Size** | {parse_active['file_size_mb']} MB | < 3 MB | > 90% reduction |",
            f"| **Compile Time** | {inflect_std['cold_compilation_seconds']} s | < 1.0 s | > 3x speedup |",
            f"| **100-Row Parse Runtime** | {corpus['total_parse_seconds']} s | Faster | Maintained or improved |",
            "",
            "---",
            "",
            "## 5. Reproducing This Benchmark",
            "",
            "To re-run this benchmark at any time using the parC conda environment:",
            "```bash",
            "/opt/homebrew/Caskroom/miniconda/base/envs/parC/bin/python scratch/benchmark_fst.py",
            "```",
            "",
            "To benchmark only graphs or customize row counts:",
            "```bash",
            "/opt/homebrew/Caskroom/miniconda/base/envs/parC/bin/python scratch/benchmark_fst.py --num-corpus-rows 50",
            "```",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark baseline FST metrics for Cherokee verb grammar."
    )
    parser.add_argument(
        "--grammar-dir",
        type=Path,
        default=DEFAULT_GRAMMAR_DIR,
        help="Path to compiled grammar directory (default: chr-generated)",
    )
    parser.add_argument(
        "--corpus-path",
        type=Path,
        default=DEFAULT_CORPUS_PATH,
        help="Path to corpus CSV file (default: chr-corpus/corpus.csv)",
    )
    parser.add_argument(
        "--num-corpus-rows",
        type=int,
        default=100,
        help="Number of valid verb rows to parse (default: 100)",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=DEFAULT_JSON_OUTPUT,
        help="Path to output JSON metrics file",
    )
    parser.add_argument(
        "--md-output",
        type=Path,
        default=DEFAULT_MD_OUTPUT,
        help="Path to output Markdown metrics file",
    )
    parser.add_argument(
        "--skip-corpus",
        action="store_true",
        help="Skip the 100-row corpus parsing benchmark",
    )
    parser.add_argument(
        "--skip-graphs",
        action="store_true",
        help="Skip the graph compilation benchmark",
    )

    args = parser.parse_args()

    abs_grammar_dir = args.grammar_dir.resolve()
    os.environ["YAML_DIR"] = str(abs_grammar_dir)

    import parC.constants as const
    const.set_yaml_dir(str(abs_grammar_dir))
    const._YAML_DIR = str(abs_grammar_dir)

    cache_dir = abs_grammar_dir / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("CHEROKEE VERB GRAMMAR - BASELINE FST BENCHMARK")
    print("=" * 70)
    print(f"Grammar Directory : {abs_grammar_dir}")
    print(f"Corpus Path       : {args.corpus_path.resolve()}")
    print(f"Target Valid Rows : {args.num_corpus_rows}")
    print(f"JSON Output       : {args.json_output.resolve()}")
    print(f"Markdown Output   : {args.md_output.resolve()}")
    print("=" * 70)

    git_info = get_git_info(REPO_ROOT)
    env_info = {
        "python_path": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "git_commit": git_info["commit"],
        "git_branch": git_info["branch"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "grammar_dir": str(abs_grammar_dir),
    }

    graph_metrics = {}

    if not args.skip_graphs:
        print("\n>>> Benchmarking Open Inflect Graph (nd_cleanup=False)...")
        inflect_std = benchmark_open_inflect_graph(
            paradigm_name="verb",
            infer_lexical_features=True,
            non_deterministic_cleanup=False,
            cache_dir=cache_dir,
        )
        print(f"    States: {inflect_std['states']:,}, Arcs: {inflect_std['arcs']:,}")
        print(f"    Disk Size: {inflect_std['file_size_mb']} MB ({inflect_std['file_size_bytes']:,} bytes)")
        print(f"    Cold Compile: {inflect_std['cold_compilation_seconds']}s, Cache Load: {inflect_std['cached_load_seconds']}s")

        print("\n>>> Benchmarking Open Inflect Graph (nd_cleanup=True)...")
        inflect_nd = benchmark_open_inflect_graph(
            paradigm_name="verb",
            infer_lexical_features=True,
            non_deterministic_cleanup=True,
            cache_dir=cache_dir,
        )
        print(f"    States: {inflect_nd['states']:,}, Arcs: {inflect_nd['arcs']:,}")
        print(f"    Disk Size: {inflect_nd['file_size_mb']} MB ({inflect_nd['file_size_bytes']:,} bytes)")
        print(f"    Cold Compile: {inflect_nd['cold_compilation_seconds']}s, Cache Load: {inflect_nd['cached_load_seconds']}s")

        print("\n>>> Benchmarking Open Parse Graph (nd_cleanup=True - Active Parser)...")
        parse_active = benchmark_open_parse_graph(
            paradigm_name="verb",
            infer_lexical_features=True,
            non_deterministic_cleanup=True,
            cache_dir=cache_dir,
        )
        print(f"    States: {parse_active['states']:,}, Arcs: {parse_active['arcs']:,}")
        print(f"    Disk Size: {parse_active['file_size_mb']} MB ({parse_active['file_size_bytes']:,} bytes)")
        print(f"    Inversion: {parse_active['inversion_seconds']}s, Total Compile: {parse_active['cold_compilation_seconds']}s")
        print(f"    Cache Load: {parse_active['cached_load_seconds']}s")

        print("\n>>> Benchmarking Open Parse Graph (nd_cleanup=False)...")
        parse_std = benchmark_open_parse_graph(
            paradigm_name="verb",
            infer_lexical_features=True,
            non_deterministic_cleanup=False,
            cache_dir=cache_dir,
        )
        print(f"    States: {parse_std['states']:,}, Arcs: {parse_std['arcs']:,}")
        print(f"    Inversion: {parse_std['inversion_seconds']}s, Total Compile: {parse_std['cold_compilation_seconds']}s")

        graph_metrics = {
            "open_inflect_standard": inflect_std,
            "open_inflect_nd_cleanup": inflect_nd,
            "open_parse_nd_cleanup": parse_active,
            "open_parse_standard": parse_std,
        }

    corpus_metrics = {}
    if not args.skip_corpus:
        print(f"\n>>> Benchmarking 100-Row Corpus Parsing ({args.num_corpus_rows} valid verb rows)...")
        corpus_metrics = benchmark_corpus_parsing(
            corpus_path=args.corpus_path,
            target_valid_rows=args.num_corpus_rows,
        )
        print(f"    Target Valid Rows : {corpus_metrics['target_valid_rows']}")
        print(f"    Corpus Rows Read  : {corpus_metrics['total_corpus_rows_examined']}")
        print(f"    Valid Rows Parsed : {corpus_metrics['valid_rows_parsed']}")
        print(f"    Total Parse Time  : {corpus_metrics['total_parse_seconds']}s")
        print(f"    Throughput        : {corpus_metrics['throughput_rows_per_second']} rows/sec")
        print(f"    Mean Time / Row   : {corpus_metrics['mean_ms_per_valid_row']} ms")
        print(f"    Median Time / Row : {corpus_metrics['median_ms_per_valid_row']} ms")

    all_metrics = {
        "environment": env_info,
        "graphs": graph_metrics,
        "corpus_benchmark": corpus_metrics,
    }

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_output, mode="w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nSaved JSON metrics to: {args.json_output}")

    md_content = generate_markdown_report(all_metrics)
    args.md_output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.md_output, mode="w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved Markdown report to: {args.md_output}")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
