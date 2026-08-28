from __future__ import annotations
import csv
from pathlib import Path
import pytest

from parse_chr_dict.h_alternation_fst import fst_grades_are_compatible

CORPUS_CSV_PATH = Path(__file__).parent / "data" / "h_alternation_test_corpus.csv"


def load_test_corpus() -> list[dict[str, str]]:
    with open(CORPUS_CSV_PATH, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


CORPUS_ENTRIES = load_test_corpus()


def test_corpus_loaded_and_non_empty():
    assert len(CORPUS_ENTRIES) >= 150
    for row in CORPUS_ENTRIES:
        assert row["h_stem"]
        assert row["glottal_stem"]
        assert row["h_stem"] != row["glottal_stem"]


@pytest.mark.parametrize(
    "row",
    CORPUS_ENTRIES,
    ids=[f"entry_{r['entry_no']}_{r['alternation_type']}_{r['h_stem']}" for r in CORPUS_ENTRIES],
)
def test_corpus_entry_h_alternation_compatibility(row: dict[str, str]):
    h_stem = row["h_stem"]
    g_stem = row["glottal_stem"]

    # FST transducer checker
    fst_result = fst_grades_are_compatible(h=h_stem, glottal=g_stem)
    assert fst_result is True, f"FST checker failed for entry {row['entry_no']} ({h_stem} vs {g_stem})"



def test_alternation_type_subsets():
    categories = {"drop_h", "h_to_glottal", "lateral_deaffrication", "syncopation_restoration"}
    counts = {cat: 0 for cat in categories}

    for row in CORPUS_ENTRIES:
        cat = row["alternation_type"]
        assert cat in categories
        counts[cat] += 1

    # Verify every category has real empirical representation in Cherokee
    assert counts["drop_h"] >= 40
    assert counts["h_to_glottal"] >= 20
    assert counts["lateral_deaffrication"] >= 5
    assert counts["syncopation_restoration"] >= 50


def test_corpus_negative_controls():
    # Test distinctly unrelated stem pairs across the corpus
    num_entries = len(CORPUS_ENTRIES)
    for i in range(num_entries):
        h_stem = CORPUS_ENTRIES[i]["h_stem"]
        # Offset by half the corpus to guarantee unrelated roots
        g_stem_other = CORPUS_ENTRIES[(i + num_entries // 2) % num_entries]["glottal_stem"]

        fst_compat = fst_grades_are_compatible(h=h_stem, glottal=g_stem_other)
        assert fst_compat is False

