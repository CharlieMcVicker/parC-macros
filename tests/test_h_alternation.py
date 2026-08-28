from __future__ import annotations
import csv
from pathlib import Path
import pytest
import pynini

from parse_chr_dict.h_alternation import (
    is_h_alternation_trigger,
    strip_h_alt_tags,
    validate_h_alternation_trigger,
    H_ALT_TAGS,
)
from parse_chr_dict.h_alternation_fst import (
    build_drop_first_h_fst,
    build_first_h_to_glottal_fst,
    build_drop_h_in_deaffricated_lateral_fst,
    build_prevent_c_glottal_cluster_fst,
    build_recreate_c_glottal_clusters_fst,
    build_possible_alternates_fst,
    build_vowel_restoration_fst,
    build_grades_compatible_fst,
    fst_possible_alternates,
    fst_prevent_c_glottal_cluster,
    fst_recreate_c_glottal_clusters,
    fst_grades_are_compatible,
)


DATA_DIR = Path(__file__).parent / "data"


def load_csv_rows(filename: str) -> list[dict[str, str]]:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _run_fst_output(fst: pynini.Fst, text: str) -> list[str]:
    res = pynini.compose(pynini.accep(text), fst)
    if res.num_states() == 0:
        return []
    out = pynini.project(res, "output").optimize()
    return [item[1] for item in out.paths().items()]


# Load CSV datasets
TRIGGERS_DATA = load_csv_rows("h_alternation_triggers.csv")
PHONOLOGY_RULES_DATA = load_csv_rows("h_alternation_phonology_rules.csv")
VOWEL_RESTORATION_DATA = load_csv_rows("h_alternation_vowel_restoration.csv")
POSSIBLE_ALTERNATES_DATA = load_csv_rows("h_alternation_possible_alternates.csv")
GRADES_COMPATIBLE_DATA = load_csv_rows("h_alternation_grades_compatible.csv")


@pytest.mark.parametrize(
    "row",
    TRIGGERS_DATA,
    ids=[r["pronominal"] for r in TRIGGERS_DATA],
)
def test_h_alternation_triggers_from_csv(row: dict[str, str]):
    pronominal = row["pronominal"]
    expected = row["is_trigger"].lower() == "true"
    assert is_h_alternation_trigger(pronominal) is expected


@pytest.mark.parametrize(
    "row",
    [r for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "drop_first_h"],
    ids=[f"drop_first_h_{r['input_str']}" for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "drop_first_h"],
)
def test_drop_first_h_from_csv(row: dict[str, str]):
    input_str = row["input_str"]
    expected = row["expected_output"]

    # FST
    fst = build_drop_first_h_fst()
    fst_outputs = _run_fst_output(fst, input_str)
    assert expected in fst_outputs


@pytest.mark.parametrize(
    "row",
    [r for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "first_h_to_glottal"],
    ids=[f"first_h_to_glottal_{r['input_str']}" for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "first_h_to_glottal"],
)
def test_first_h_to_glottal_from_csv(row: dict[str, str]):
    input_str = row["input_str"]
    expected = row["expected_output"]

    # FST
    fst = build_first_h_to_glottal_fst()
    fst_outputs = _run_fst_output(fst, input_str)
    assert expected in fst_outputs


@pytest.mark.parametrize(
    "row",
    [r for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "drop_h_in_deaffricated_lateral"],
    ids=[f"drop_lateral_{r['input_str']}" for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "drop_h_in_deaffricated_lateral"],
)
def test_drop_h_in_deaffricated_lateral_from_csv(row: dict[str, str]):
    input_str = row["input_str"]
    expected = row["expected_output"]

    # FST
    fst = build_drop_h_in_deaffricated_lateral_fst()
    fst_outputs = _run_fst_output(fst, input_str)
    assert expected in fst_outputs


@pytest.mark.parametrize(
    "row",
    [r for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "prevent_c_glottal_cluster"],
    ids=[f"prevent_{r['input_str']}" for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "prevent_c_glottal_cluster"],
)
def test_prevent_c_glottal_cluster_from_csv(row: dict[str, str]):
    form = row["input_str"]
    prevented = row["expected_output"]

    # FST
    fst_res = fst_prevent_c_glottal_cluster(form)
    assert fst_res == prevented


@pytest.mark.parametrize(
    "row",
    [r for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "recreate_c_glottal_clusters"],
    ids=[f"recreate_{r['input_str']}" for r in PHONOLOGY_RULES_DATA if r["rule_name"] == "recreate_c_glottal_clusters"],
)
def test_recreate_c_glottal_clusters_from_csv(row: dict[str, str]):
    surface = row["input_str"]
    recreated = row["expected_output"]

    # FST
    fst_res = fst_recreate_c_glottal_clusters(surface)
    assert fst_res == recreated


@pytest.mark.parametrize(
    "row",
    VOWEL_RESTORATION_DATA,
    ids=[f"restoration_{r['restored']}_vs_{r['syncopated']}" for r in VOWEL_RESTORATION_DATA],
)
def test_is_compatible_with_vowel_restoration_from_csv(row: dict[str, str]):
    restored = row["restored"]
    syncopated = row["syncopated"]
    expected = row["is_compatible"].lower() == "true"

    fst = build_vowel_restoration_fst()
    outputs = _run_fst_output(fst, syncopated)
    assert (restored in outputs) is expected


@pytest.mark.parametrize(
    "row",
    POSSIBLE_ALTERNATES_DATA,
    ids=[f"alt_{r['h_form']}_fix_{r['fix_clusters']}" for r in POSSIBLE_ALTERNATES_DATA],
)
def test_possible_alternates_from_csv(row: dict[str, str]):
    h_form = row["h_form"]
    fix_clusters = row["fix_clusters"].lower() == "true"
    expected_set = set(row["expected_alternates"].split("|")) if row["expected_alternates"] else set()

    fst_set = fst_possible_alternates(h_form, fix_clusters=fix_clusters)
    assert fst_set == expected_set


@pytest.mark.parametrize(
    "row",
    GRADES_COMPATIBLE_DATA,
    ids=[f"grades_{r['h_form']}_{r['glottal_form']}" for r in GRADES_COMPATIBLE_DATA],
)
def test_grades_are_compatible_from_csv(row: dict[str, str]):
    h_form = row["h_form"]
    glottal_form = row["glottal_form"]
    expected = row["is_compatible"].lower() == "true"

    fst_res = fst_grades_are_compatible(h=h_form, glottal=glottal_form)
    assert fst_res is expected



def test_fst_grades_compatible_transducer_structure():
    fst = build_grades_compatible_fst()
    assert fst.num_states() > 0

    input_fsa = pynini.accep("ahne")
    composed = pynini.compose(input_fsa, fst)
    assert composed.num_states() > 0
    projected = pynini.project(composed, "output").optimize()
    outputs = {item[1] for item in projected.paths().items()}

    assert "ane" in outputs
    assert "a'ne" in outputs
    assert "ahne" in outputs
