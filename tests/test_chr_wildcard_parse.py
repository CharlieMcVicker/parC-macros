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
INFL_FEATURES = ["aspect", "pronominal", "rules", "tense", "translocutive", "distributive"]


def load_test_cases():
    cases = []
    for path in [CSV_PATH, WILDCARD_CSV_PATH]:
        if not path.exists():
            continue
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty rows or partitive rows (partitive currently disabled in verb.yaml)
                if not row.get("surface") or row.get("partitive"):
                    continue
                infl_dict = {f: row[f] for f in INFL_FEATURES if f in row and row[f]}
                if "rules" not in infl_dict:
                    infl_dict["rules"] = "+"
                cases.append(
                    (
                        row["surface"],
                        row["root"],
                        {f: row[f] for f in LEXICAL_FEATURES if f in row},
                        infl_dict,
                    )
                )
    return cases


@pytest.mark.parametrize(
    "surface,root,lexical,infl",
    load_test_cases(),
)
def test_cherokee_wildcard_parsing(surface, root, lexical, infl):
    parses = parse(surface)
    # Construct the expected tag sequence with prefix tags [WI]/[DIST]
    prefix_tags = ""
    if infl.get("translocutive") == "+":
        prefix_tags += "[WI]"
    if infl.get("distributive") == "+":
        prefix_tags += "[DIST]"

    wrapped_root = root if root.startswith("[Pro]") else f"{prefix_tags}[Pro]{root}[Aspect][Tense]"
    word_parts = ["[BOW]", wrapped_root, "[EOW]"]
    word_parts.extend(
        [
            feature_tag(f, v)
            for f, v in sorted(lexical.items(), key=lambda kv: kv[0])
            if v
        ]
    )

    word_parts.extend(
        [
            feature_tag(f, v)
            for f, v in sorted(infl.items(), key=lambda kv: kv[0])
            if v and f not in ("translocutive", "distributive")
        ]
    )
    target_pattern = "".join(word_parts)
    assert (
        target_pattern in parses
    ), f"Expected parse string '{target_pattern}' was not accepted by the parse lattice for surface form '{surface}' - num parses {len(parses)} \n {(parses[:10])}"

