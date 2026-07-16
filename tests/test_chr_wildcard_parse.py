import csv
import os
from pathlib import Path
import pytest
import pynini

from parse_chr_dict.parse import parse, feature_tag

# Ensure environment variable YAML_DIR is set
if "YAML_DIR" not in os.environ:
    os.environ["YAML_DIR"] = str(Path(__file__).parent.parent / "chr-generated")

# Path to the CSV files with test cases
CSV_PATH = Path(__file__).parent / "test_chr_parse.csv"
WILDCARD_CSV_PATH = Path(__file__).parent / "test_chr_wildcard_parse.csv"

LEXICAL_FEATURES = ["aspect_class", "prefix_class", "tense_present_class"]
INFL_FEATURES = ["aspect", "pronominal", "tense", "translocutive"]


def load_test_cases():
    cases = []
    for path in [CSV_PATH, WILDCARD_CSV_PATH]:
        if not path.exists():
            continue
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty rows
                if not row.get("surface"):
                    continue
                cases.append(
                    (
                        row["surface"],
                        row["root"],
                        {f: row[f] for f in LEXICAL_FEATURES},
                        {f: row[f] for f in INFL_FEATURES if f in row},
                    )
                )
    return cases


@pytest.mark.parametrize(
    "surface,root,lexical,infl",
    load_test_cases(),
)
def test_cherokee_wildcard_parsing(surface, root, lexical, infl):
    parses = parse(surface)
    # Construct the expected tag sequence
    word_parts = ["[BOW]", root, "[EOW]"]
    word_parts.extend(
        [
            feature_tag(f, v)
            for f, v in sorted(lexical.items(), key=lambda kv: kv[0])
            if v
        ]
    )
    word_parts.extend(
        [feature_tag(f, v) for f, v in sorted(infl.items(), key=lambda kv: kv[0]) if v]
    )
    target_pattern = "".join(word_parts)
    for p in parses:
        if "be-at" in p and "present" in p and "completive" not in p:
            print(p)
    assert (
        target_pattern in parses
    ), f"Expected parse string '{target_pattern}' was not accepted by the parse lattice for surface form '{surface}' - num parses {len(parses)} \n {(parses[:10])}"
