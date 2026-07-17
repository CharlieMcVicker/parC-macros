import os
from pathlib import Path
import pytest

# Ensure environment variable YAML_DIR is set to the insertion-generated output
if "YAML_DIR" not in os.environ:
    os.environ["YAML_DIR"] = str(
        Path(__file__).parent.parent / "min-min-insertion-generated"
    )

from parse_chr_dict.parse import parse


def test_optional_feature_combinations_insertion():
    """Same surface/tag assertions as test_prefix_template but for
    min-min-insertion-generated/, which is produced by the CSV-based
    insertion macro system instead of hand-coded YAML rules."""
    tests = [("watata", "[WI]"), ("tatata", "[DIST]"), ("witata", "[WI][DIST]")]

    for surface, tag_seq in tests:
        parses = parse(surface)
        assert any(
            tag_seq in p for p in parses
        ), f"Expected some parse of '{surface}' to include {tag_seq}\n{parses}"
