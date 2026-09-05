import os
from pathlib import Path
import pytest

from parC.constants import set_yaml_dir
from parC.grammar.paradigm_compilation import clear_all_caches
import parse_chr_dict.parse as parse_mod
from parse_chr_dict.parse import parse

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "min-min-insertion-generated"


@pytest.fixture(autouse=True)
def setup_yaml_dir():
    orig_yaml_dir = os.environ.get("YAML_DIR")
    os.environ["YAML_DIR"] = str(FIXTURE_DIR)
    set_yaml_dir(str(FIXTURE_DIR))
    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    yield
    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    if orig_yaml_dir:
        os.environ["YAML_DIR"] = orig_yaml_dir
        set_yaml_dir(orig_yaml_dir)


def test_optional_feature_combinations_insertion():
    """Same surface/tag assertions as test_prefix_template but for
    min-min-insertion-generated/, which is produced by the CSV-based
    insertion macro system instead of hand-coded YAML rules."""
    tests = [
        ("watata", "[WI]"),
        ("tatata", "[DIST]"),
        ("witata", "[WI][DIST]"),
    ]


    for surface, tag_seq in tests:
        parses = parse(surface)
        assert any(
            tag_seq in p for p in parses
        ), f"Expected some parse of '{surface}' to include {tag_seq}\n{parses}"
