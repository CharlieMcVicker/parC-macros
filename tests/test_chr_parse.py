import csv
import os
from pathlib import Path
import pytest
from parC.grammar.paradigm_compilation import parse, _get_or_build

# Ensure environment variable YAML_DIR is set so parC knows where to look for compiled FST/YAML files.
if "YAML_DIR" not in os.environ:
    os.environ["YAML_DIR"] = str(Path(__file__).parent.parent / "chr-generated")

# Path to the CSV file with test cases
CSV_PATH = Path(__file__).parent / "test_chr_parse.csv"
WORDLIST_PATH = Path(__file__).parent.parent / "chr-config" / "wordlists" / "verb.csv"


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


def load_wordlist_features():
    lexicon = {}
    if WORDLIST_PATH.exists():
        with open(WORDLIST_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lexicon[row["root"]] = {
                    "prefix_class": row.get("prefix_class"),
                    "aspect_class": row.get("aspect_class"),
                }
    return lexicon


# Build parse graph once before running tests
@pytest.fixture(scope="module", autouse=True)
def setup_paradigm():
    _get_or_build(graph_type="parse", paradigm_name="verb", force_rebuild=True)


@pytest.mark.parametrize(
    "surface,root,pronominal,prefix_class,aspect,aspect_class",
    load_test_cases(),
)
def test_cherokee_parsing(
    surface, root, pronominal, prefix_class, aspect, aspect_class
):
    results = parse(surface, kind="Paradigm", name="verb")
    assert len(results) > 0, f"No parse results found for surface form: {surface}"

    # Find the result that matches the expected root
    match = None
    for r in results:
        if r["root"] == root:
            match = r
            break

    assert (
        match is not None
    ), f"Expected root '{root}' not found in parse results: {results}"

    # Verify features in parse result
    assert (
        match["features"].get("pronominal") == pronominal
    ), f"Pronominal feature mismatch: expected {pronominal}, got {match['features'].get('pronominal')}"
    assert (
        match["features"].get("aspect") == aspect
    ), f"Aspect feature mismatch: expected {aspect}, got {match['features'].get('aspect')}"

    # Verify lexical features of the root from the wordlist (these are columns after root that should match)
    lexicon = load_wordlist_features()
    assert (
        root in lexicon
    ), f"Root '{root}' not found in wordlist at {WORDLIST_PATH}"
    assert (
        lexicon[root]["prefix_class"] == prefix_class
    ), f"Prefix class mismatch for root '{root}': expected {prefix_class}, got {lexicon[root]['prefix_class']}"
    assert (
        lexicon[root]["aspect_class"] == aspect_class
    ), f"Aspect class mismatch for root '{root}': expected {aspect_class}, got {lexicon[root]['aspect_class']}"
