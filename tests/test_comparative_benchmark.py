"""
tests/test_comparative_benchmark.py

Validation test suite for TASK-102.5:
- Verifies that comparative benchmark reports exist and contain valid schema.
- Asserts state, arc, disk size, and compilation time reductions meet or exceed optimization targets.
- Verifies 100-row parse comparison metrics.
- Validates read_labels backwards compatibility on both legacy and in-place parse strings.
"""

import json
from pathlib import Path
import pytest
from parse_chr_dict.parse import read_labels

REPO_ROOT = Path(__file__).parent.parent.resolve()
BENCHMARK_JSON = REPO_ROOT / "scratch" / "comparative_benchmark.json"
BENCHMARK_MD = REPO_ROOT / "scratch" / "comparative_benchmark.md"


def test_comparative_benchmark_files_exist():
    """Verify that both comparative JSON and Markdown artifacts exist and are non-empty."""
    assert BENCHMARK_JSON.exists(), f"Missing {BENCHMARK_JSON}"
    assert BENCHMARK_MD.exists(), f"Missing {BENCHMARK_MD}"
    assert BENCHMARK_JSON.stat().st_size > 0
    assert BENCHMARK_MD.stat().st_size > 0


def test_comparative_benchmark_metrics():
    """Verify key reduction targets in comparative_benchmark.json."""
    with open(BENCHMARK_JSON, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data["summary_gains"]
    # States reduction > 99%
    assert summary["states_reduction_percentage"] > 99.0, (
        f"Expected states reduction > 99%, got {summary['states_reduction_percentage']}%"
    )

    # Arcs reduction > 99%
    assert summary["arcs_reduction_percentage"] > 99.0, (
        f"Expected arcs reduction > 99%, got {summary['arcs_reduction_percentage']}%"
    )

    # Disk size reduction > 99%
    assert summary["disk_size_reduction_percentage"] > 99.0, (
        f"Expected disk size reduction > 99%, got {summary['disk_size_reduction_percentage']}%"
    )

    # Cold compilation speedup > 30x
    assert summary["cold_compilation_speedup_factor"] > 30.0, (
        f"Expected compilation speedup > 30x, got {summary['cold_compilation_speedup_factor']}x"
    )

    # Graph comparisons
    graphs = data["graph_comparisons"]
    active_parser = graphs["open_parse_nd_cleanup"]
    assert active_parser["states"]["inplace"] == 956
    assert active_parser["states"]["baseline"] == 578015
    assert active_parser["file_size_mb"]["inplace"] <= 0.5
    assert active_parser["file_size_mb"]["baseline"] >= 40.0

    # 100-row parse comparison
    runtime = data["parse_runtime_comparison"]
    assert runtime["valid_rows_count"] == 100
    assert runtime["all_581_forms_across_100_rows"]["total_forms"] == 581
    assert runtime["all_581_forms_across_100_rows"]["inplace_total_seconds"] < runtime["all_581_forms_across_100_rows"]["baseline_total_seconds"]


def test_read_labels_inplace_and_legacy_compatibility():
    """Verify read_labels behaves identically for legacy and in-place slot tags."""
    # 1. Legacy
    legacy_str = "[BOW]gawoniha[EOW][tense=present][aspect=present][pronominal=3sg.A]"
    form, labels = read_labels(legacy_str)
    assert form == "gawoniha"
    assert labels["tense"] == "present"
    assert labels["aspect"] == "present"
    assert labels["pronominal"] == "3sg.A"

    # 2. In-place
    inplace_str = (
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]tateka[AspectClass=a][Aspect=present]"
        "[Tense=present_a][EOW][aspect_class=a][prefix_class=a_stem]"
    )
    form_ip, labels_ip = read_labels(inplace_str)
    assert form_ip == "tateka"
    assert labels_ip["prefix_class"] == "a_stem"
    assert labels_ip["pronominal"] == "3sg.A"
    assert labels_ip["aspect_class"] == "a"
    assert labels_ip["aspect"] == "present"
    assert labels_ip["tense"] == "present_a"
