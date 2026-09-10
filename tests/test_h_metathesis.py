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


def _inflect_stem(
    stem: str,
    prefix_class: str,
    pro: str,
    metathesis_type: str,
    prepro: str = "[WI]",
    aspect_class: str = "rev-gi",
) -> list[str]:
    tag_str = (
        f"{prepro}[PrefixClass={prefix_class}][Pro={pro}]"
        f"[H_metathesis={metathesis_type}][H_alt=none]"
        f"{stem}[AspectClass={aspect_class}][Aspect=present][Tense=present_a]"
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


def test_voice_infix_h_metathesis_talhinoheha():
    """
    Verifies that voice infix [VoiceInfix=ali] before root nho correctly applies
    H-metathesis to produce talhinoheha (alinh -> alhin).
    """
    forms = _inflect_stem(
        stem="[VoiceInfix=ali]nho",
        prefix_class="a_stem",
        pro="3sg.A",
        metathesis_type="active",
        prepro="[DIST=de]",
        aspect_class="apl-active-h",
    )
    assert "talhinoheha" in forms, f"Expected 'talhinoheha' in forms, but got: {forms}"


def test_voice_infix_licenses_h_metathesis_on_non_trigger_pronominal():
    """
    Verifies that voice infix [VoiceInfix=ali] allows H-metathesis even with
    pronominals like 3sg.B which would otherwise clamp to [H_metathesis=none].
    """
    from parse_chr_dict.acceptors import accepts_parse, compile_morphotactic_acceptor

    acceptor = compile_morphotactic_acceptor()

    # 3sg.B without voice infix with [H_metathesis=active] must be REJECTED (clamped to none)
    bad_parse = "[PrefixClass=a_stem][Pro=3sg.B][H_metathesis=active][H_alt=none]nho[AspectClass=rev-gi][Aspect=present][Tense=present_a]"
    assert not accepts_parse(acceptor, bad_parse), "Expected 3sg.B without voice infix to reject [H_metathesis=active]"

    # 3sg.B without voice infix with [H_metathesis=none] must be ACCEPTED
    good_parse_none = "[PrefixClass=a_stem][Pro=3sg.B][H_metathesis=none][H_alt=none]nho[AspectClass=rev-gi][Aspect=present][Tense=present_a]"
    assert accepts_parse(acceptor, good_parse_none), "Expected 3sg.B without voice infix to accept [H_metathesis=none]"

    # 3sg.B WITH voice infix [VoiceInfix=ali] with [H_metathesis=active] must be ACCEPTED
    good_voice_active = "[PrefixClass=a_stem][Pro=3sg.B][H_metathesis=active][H_alt=none][VoiceInfix=ali]nho[AspectClass=rev-gi][Aspect=present][Tense=present_a]"
    assert accepts_parse(acceptor, good_voice_active), "Expected 3sg.B with [VoiceInfix=ali] to license [H_metathesis=active]"

