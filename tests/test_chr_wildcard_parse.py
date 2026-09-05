import csv
import os
from pathlib import Path
import pytest
import pynini

from parse_chr_dict.parse import parse, feature_tag, read_labels

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
    assert len(parses) > 0, f"No parses returned for '{surface}'"

    # Match via read_labels for in-place grammar parses
    found = False
    for p in parses:
        p_root, p_labels = read_labels(p)
        if p_root != root:
            continue
        lex_match = True
        for k, v in lexical.items():
            base_v = v.split("[")[0] if "[" in v else v
            if p_labels.get(k) not in (v, base_v):
                lex_match = False
                break
        if not lex_match:
            continue
        infl_match = True
        for k, v in infl.items():
            if p_labels.get(k) != v:
                infl_match = False
                break
        if infl_match:
            found = True
            break

    if not found:
        # Fallback to literal target_pattern check for baseline grammars
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
        ), f"Expected parse matching root '{root}' and features was not found for '{surface}' - num parses {len(parses)} \n {(parses[:10])}"

