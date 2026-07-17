import os
from pathlib import Path
import pytest

# Ensure environment variable YAML_DIR is set
if "YAML_DIR" not in os.environ:
    os.environ["YAML_DIR"] = str(Path(__file__).parent.parent / "min-min-generated")

from parse_chr_dict.parse import parse


def test_optional_feature_combinations():
    tests = [("watata", "[WI]"), ("tatata", "[DIST]"), ("witata", "[WI][DIST]")]

    for surface, tag_seq in tests:
        parses = parse(surface)
        assert any(
            tag_seq in p for p in parses
        ), f"Expected some parse of '{surface}' to include {tag_seq}\n{parses}"
