import csv
import os
from pathlib import Path
import pytest
import pynini

from parC.grammar.paradigm_compilation import (
    build_inflect_graph_for_root_regex,
    build_parse_graph,
    word_fsa,
    fsa,
)

# Ensure environment variable YAML_DIR is set
if "YAML_DIR" not in os.environ:
    os.environ["YAML_DIR"] = str(Path(__file__).parent.parent / "chr-generated")

# Path to the CSV file with test cases
CSV_PATH = Path(__file__).parent / "test_chr_parse.csv"


def load_test_cases():
    cases = []
    if not CSV_PATH.exists():
        return cases
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(
                (
                    row["surface"],
                    row["root"],
                    row["pronominal"],
                    row["prefix_class"],
                    row["aspect"],
                    row["aspect_class"],
                )
            )
    return cases


@pytest.fixture(scope="module")
def wildcard_parse_graph():
    # Build the inflection graph with open ended "<Phone>*" root and infer_lexical_features=True
    inflect_graph = build_inflect_graph_for_root_regex(
        "verb", "<Phone>*", infer_lexical_features=True
    )
    # Invert to build the parse graph
    parse_graph = build_parse_graph(inflect_graph)
    return parse_graph


@pytest.mark.parametrize(
    "surface,root,pronominal,prefix_class,aspect,aspect_class",
    load_test_cases(),
)
def test_cherokee_wildcard_parsing(
    wildcard_parse_graph, surface, root, pronominal, prefix_class, aspect, aspect_class
):
    form_fsa = word_fsa(surface)
    parse_lattice = (form_fsa @ wildcard_parse_graph).optimize()
    output_projected = pynini.project(parse_lattice, "output").optimize()

    # Construct the expected tag sequence
    target_pattern = (
        f"[BOW]{root}[EOW]"
        f"[prefix_class={prefix_class}]"
        f"[aspect_class={aspect_class}]"
        f"[aspect={aspect}]"
        f"[pronominal={pronominal}]"
    )
    target_fsa = fsa(target_pattern)

    intersected = pynini.intersect(output_projected, target_fsa).optimize()
    assert intersected.num_states() > 0, (
        f"Expected parse string '{target_pattern}' was not accepted by the parse lattice for surface form '{surface}'"
    )
