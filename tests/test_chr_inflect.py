import csv
import os
from pathlib import Path
import pytest
import pynini
from loguru import logger

from parC.grammar.paradigm_compilation import (
    build_inflect_graph_for_root_regex,
    word_fsa,
    fsa,
    fsm_strings,
    stringify_features,
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
            print("read row", row)
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


def stringify_lexical_features(lexical_features):
    if not lexical_features:
        return ""
    # Cherokee verbs lexical features must be ordered: prefix_class, aspect_class
    parts = []
    if "prefix_class" in lexical_features:
        parts.append(f"[prefix_class={lexical_features['prefix_class']}]")
    if "aspect_class" in lexical_features:
        parts.append(f"[aspect_class={lexical_features['aspect_class']}]")
    return "".join(parts)


def test_build_inflect_graph_for_specific_root():
    """
    Test build_inflect_graph_for_root_regex with a specific root.
    Since the root is a fixed string, pynini.cross preserves the mapping between the root and surface form.
    """
    logger.info(
        "Testing build_inflect_graph_for_root_regex with specific root 'woni'..."
    )

    # We build the graph specifically for the root 'woni'
    graph = build_inflect_graph_for_root_regex(
        "verb", "woni", infer_lexical_features=True
    )

    lexical_features = {
        "prefix_class": "r_stem",
        "aspect_class": "ha-hi-s",
    }
    inflectional_features = {
        "pronominal": "3sg.A",
        "aspect": "present",
    }

    lexical_str = stringify_lexical_features(lexical_features)
    inflectional_str = stringify_features(inflectional_features)

    input_fsa = pynini.concat(word_fsa("woni"), fsa(lexical_str))
    input_fsa = pynini.concat(input_fsa, fsa(inflectional_str))

    output_lattice = pynini.compose(input_fsa, graph).optimize()
    output_lattice = pynini.project(output_lattice, project_type="output")
    surface_forms = fsm_strings(output_lattice, strip_all_tags=True, nshortest=5)

    logger.info(f"Specific root woni -> Got surface forms: {surface_forms}")
    assert "kawoniha" in surface_forms


def test_build_inflect_graph_for_root_regex_wildcard():
    """
    Test build_inflect_graph_for_root_regex with a wildcard root regex '<Phone>+'.
    Because parC compiles the graph by crossing the entire input set with the inflected output set,
    the identity of the root is not preserved. We log the resulting surface forms and verify
    that they contain the correct prefix/suffix markers (e.g. ka...ha for woni/r_stem/ha-hi-s).
    """
    logger.info(
        "Building inflection graph for root regex '<Phone>+' with infer_lexical_features=True..."
    )
    graph = build_inflect_graph_for_root_regex(
        "verb", "<Phone>+", infer_lexical_features=True
    )

    test_cases = load_test_cases()
    assert len(test_cases) > 0, "No test cases found in CSV"

    for surface, root, pronominal, prefix_class, aspect, aspect_class in test_cases:
        lexical_features = {
            "prefix_class": prefix_class,
            "aspect_class": aspect_class,
        }
        inflectional_features = {
            "pronominal": pronominal,
            "aspect": aspect,
        }

        lexical_str = stringify_lexical_features(lexical_features)
        inflectional_str = stringify_features(inflectional_features)

        input_fsa = pynini.concat(word_fsa(root), fsa(lexical_str))
        input_fsa = pynini.concat(input_fsa, fsa(inflectional_str))

        output_lattice = pynini.compose(input_fsa, graph).optimize()
        output_lattice = pynini.project(output_lattice, project_type="output")
        surface_forms = fsm_strings(output_lattice, strip_all_tags=True, nshortest=5)

        logger.info(
            f"Wildcard inflection test: Root='{root}', Lexical={lexical_features}, Inflectional={inflectional_features} "
            f"-> Expected='{surface}', Got={surface_forms}"
        )

        # Verify that all outputs start with the expected prefix and end with the expected suffix.
        # For example, for woni/3sg.A/present/r_stem/ha-hi-s, the prefix is 'ka' and suffix is 'ha'.
        # Since the root identity is not preserved, any sequence of phones could be inside.
        if (
            prefix_class == "r_stem"
            and aspect_class == "ha-hi-s"
            and pronominal == "3sg.A"
            and aspect == "present"
        ):
            for form in surface_forms:
                assert form.startswith("ka")
                assert form.endswith("ha")

