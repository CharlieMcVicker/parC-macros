"""
tests/test_h_metathesis.py

Parameterized test suite for H-metathesis phonology rules.
Metathesis occurs across the Pro.Root boundary where the root begins with <C>*<V><C>h.
Add or edit test cases in the CASES list below.
"""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from parC.constants import set_yaml_dir
from parC.grammar.acceptor_compilation import fsm_strings, word_fsa
from parC.grammar.paradigm_compilation import clear_all_caches, get_open_inflect_graph

REPO_ROOT = Path(__file__).parent.parent.resolve()
YAML_DIR = REPO_ROOT / "chr-generated"


# =============================================================================
# EDITABLE TEST CASES
# Format: (stem, prefix_class, pro, metathesis_type, expected_surface_form)
# - stem: lexical root (e.g. "anho", "inho", "kanho")
# - prefix_class: e.g. "cons_stem" or "a_stem"
# - pro: pronominal tag (e.g. "1sg.A")
# - metathesis_type: "active" or "none"
# - expected_surface_form: expected full surface word after inflection
# =============================================================================
CASES = [
    # -------------------------------------------------------------------------
    # Pro.Root boundary with vowel-initial roots (<C>* = ""): Pro + VChV
    # -------------------------------------------------------------------------
    # [Pro=1sg.A] on a_stem is "k": k + anho -> khano
    ("nho", "r_stem", "3sg.A", "active", "wikhanoki'a"),
    ("nho", "r_stem", "3sg.A", "none", "wikanhoki'a"),
    ("elho", "vowel_stem", "3sg.A", "active", "wikheloki'a"),
    # aki
    ("nhalv", "r_stem", "1sg.B", "active", "wakhinalvki'a"),
    ("nhalv", "r_stem", "1sg.B", "none", "wakinhalvki'a"),

    # tsa -> tsha
    ("nhalv", "r_stem", "2sg.B", "active", "witshanalvki'a"),
    ("nhalv", "r_stem", "2sg.B", "none", "witsanhalvki'a"),
]


@pytest.fixture(scope="module", autouse=True)
def setup_env():
    orig_yaml_dir = os.environ.get("YAML_DIR")
    os.environ["YAML_DIR"] = str(YAML_DIR)
    set_yaml_dir(str(YAML_DIR))
    clear_all_caches()
    yield
    if orig_yaml_dir:
        os.environ["YAML_DIR"] = orig_yaml_dir
        set_yaml_dir(orig_yaml_dir)
    clear_all_caches()


def _inflect_stem(stem: str, prefix_class: str, pro: str, metathesis_type: str) -> list[str]:
    tag_str = (
        f"[WI][PrefixClass={prefix_class}][Pro={pro}]"
        f"[H_metathesis={metathesis_type}][H_alt=none]"
        f"{stem}[AspectClass=rev-gi][Aspect=present][Tense=present_a]"
    )
    inflect_fst = get_open_inflect_graph("verb", infer_lexical_features=False)
    out = (word_fsa(tag_str) @ inflect_fst).project("output").optimize()
    return [f.replace("[BOW]", "").replace("[EOW]", "") for f in fsm_strings(out)]


@pytest.mark.parametrize("stem, prefix_class, pro, metathesis_type, expected_surface_form", CASES)
def test_h_metathesis_case(
    stem: str,
    prefix_class: str,
    pro: str,
    metathesis_type: str,
    expected_surface_form: str,
):
    forms = _inflect_stem(stem, prefix_class, pro, metathesis_type)
    assert expected_surface_form in forms, (
        f"For stem '{stem}' ({prefix_class}, {pro}) with H_metathesis={metathesis_type}, "
        f"expected '{expected_surface_form}', but got: {forms}"
    )
