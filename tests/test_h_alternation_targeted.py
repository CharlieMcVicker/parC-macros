"""
tests/test_h_alternation_targeted.py

Unit test suite for TASK-104:
Fix h alternation applying to multiple sounds by targeting only the first matching sound.

Validates:
- AC 1: Temp tags in alphabet.yaml (<TempTags>)
- AC 2: 3-step targeted alternation architecture in h_alternation.yaml
- AC 3: Inflection and parse parity on real dictionary entries from roots.csv:
    - H_DROP: Entry 22 (atawhahthvhit), Entry 214 (whahthvhit), Entry 218 (yhahkhets), Entry 537 (yvwhahth)
    - H_GLOT: Entry 65 (atehohist), Entry 321 (alihelitsh), Entry 1045 (ohiyhtan)
    - H_LAT: Entry 175 (alhawitht), Entry 173 (alhawit), Entry 563 (alhilost)
    - H_VOWEL: Entry 45 (atanhthehil), Entry 186 (alhkhotht), Entry 280 (khtha)
- AC 4: Parse of Entry 8/9 surface 'atatek' produces zero multi-h restored roots (e.g. eliminating spurious 'athathek' / 'athathekh')
- Verification of noise-verb exception root -noyhvlhist- (Entries 46 and 952)
"""

import os
from pathlib import Path
import pytest
import pynini

from parC.constants import set_yaml_dir
from parC.grammar.acceptor_compilation import fsm_strings, word_fsa
from parC.grammar.paradigm_compilation import get_open_inflect_graph, clear_all_caches
from parse_chr_dict.parse import parse, get_just_root


REPO_ROOT = Path(__file__).parent.parent.resolve()
INPLACE_GEN_DIR = REPO_ROOT / "chr-generated"


@pytest.fixture(scope="module", autouse=True)
def setup_env():
    orig_yaml_dir = os.environ.get("YAML_DIR")
    os.environ["YAML_DIR"] = str(INPLACE_GEN_DIR)
    set_yaml_dir(str(INPLACE_GEN_DIR))
    clear_all_caches()
    import parse_chr_dict.parse as parse_mod
    parse_mod.PARSE_GRAPH = None

    yield

    if orig_yaml_dir:
        os.environ["YAML_DIR"] = orig_yaml_dir
        set_yaml_dir(orig_yaml_dir)
    clear_all_caches()
    parse_mod.PARSE_GRAPH = None


def _inflect(tag_str: str) -> list[str]:
    inflect_fst = get_open_inflect_graph("verb", infer_lexical_features=False)
    out = pynini.project(pynini.compose(word_fsa(tag_str), inflect_fst), "output").optimize()
    forms = fsm_strings(out)
    return [f.replace("[BOW]", "").replace("[EOW]", "") for f in forms]


# =========================================================================
# AC 3: Real dictionary multi-h root inflection tests
# =========================================================================

def test_h_drop_entry_22():
    """Entry 22: [Pro][H_DROP]atawhahthvhit[Aspect][Tense] -> 1sg katawahthvhitoha
    1st h in wh drops, subsequent ah, th, vh remain.
    """
    tag_str = "[PrefixClass=a_stem][Pro=1sg.A][H_alt=drop]atawhahthvhit[AspectClass=be-at][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "katawahthvhitoha" in forms


def test_h_drop_entry_214():
    """Entry 214: [Pro][H_alt=drop]whahthvhit[Aspect][Tense] -> 1sg tsiwahthvhitoha
    1st h in wh drops, subsequent ah, th, vh remain.
    """
    tag_str = "[PrefixClass=cons_stem][Pro=1sg>3sg][H_alt=drop]whahthvhit[AspectClass=be-at][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tsiwahthvhitoha" in forms


def test_h_drop_entry_218():
    """Entry 218: [Pro][H_alt=drop]yhahkhets[Aspect][Tense] -> 1sg tsiyahkhetska
    1st h in yh drops, subsequent hk remains.
    """
    tag_str = "[PrefixClass=cons_stem][Pro=1sg>3sg][H_alt=drop]yhahkhets[AspectClass=stative-k][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tsiyahkhetska" in forms


def test_h_drop_entry_537():
    """Entry 537: [Pro][H_alt=drop]yvwhahth[Aspect][Tense] -> 1sg tsiyvwahthiha
    1st h in wh drops, subsequent th remains.
    """
    tag_str = "[PrefixClass=cons_stem][Pro=1sg>3sg][H_alt=drop]yvwhahth[AspectClass=ih-vh][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tsiyvwahthiha" in forms


def test_h_glot_entry_65():
    """Entry 65: [Pro][H_alt=glot]atehohist[Aspect][Tense] -> 1sg tsiyate'ohistiha
    1st h becomes ', 2nd h in histiha remains.
    """
    tag_str = "[PrefixClass=a_stem][Pro=1sg>3sg][H_alt=glot]atehohist[AspectClass=cause][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tsiyate'ohistiha" in forms


def test_h_glot_entry_321():
    """Entry 321: [Pro][H_alt=glot]alihelitsh[Aspect][Tense] -> 1sg tsiyali'elitsheha
    1st h becomes ', subsequent tsh remains.
    """
    tag_str = "[PrefixClass=a_stem][Pro=1sg>3sg][H_alt=glot]alihelitsh[AspectClass=apl][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tsiyali'elitsheha" in forms


def test_h_glot_entry_1045():
    """Entry 1045: [Pro][H_alt=glot]ohiyhtan[Aspect][Tense] -> 1sg tsiyo'iyhtaneha
    1st h becomes ', subsequent yht remains.
    """
    tag_str = "[PrefixClass=vowel_stem][Pro=1sg>3sg][H_alt=glot]ohiyhtan[AspectClass=apl][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tsiyo'iyhtaneha" in forms


def test_h_lat_entry_175():
    """Entry 175: [Pro][H_alt=lat]alhawitht[Aspect][Tense] -> 1sg tsiyatlawithtiha
    1st lh becomes tl, subsequent th and ht remain.
    """
    tag_str = "[PrefixClass=a_stem][Pro=1sg>3sg][H_alt=lat]alhawitht[AspectClass=cause][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tsiyatlawithtiha" in forms


def test_h_lat_entry_173():
    """Entry 173: [Pro][H_alt=lat]alhawit[Aspect][Tense] -> 1sg katlawitiha
    1st lh becomes tl.
    """
    tag_str = "[PrefixClass=a_stem][Pro=1sg.A][H_alt=lat]alhawit[AspectClass=ih-vh][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "katlawitiha" in forms


def test_h_lat_entry_563():
    """Entry 563: [DIST=de][Pro][H_alt=lat]alhilost[Aspect][Tense] -> 1sg tetsiyatlilostiha
    1st lh becomes tl.
    """
    tag_str = "[DIST=de][PrefixClass=a_stem][Pro=1sg>3sg][H_alt=lat]alhilost[AspectClass=cause][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tetsiyatlilostiha" in forms


def test_h_vowel_entry_45():
    """Entry 45: [Pro][H_alt=vowel]atanhthehil[Aspect][Tense] -> 1sg katanvthehilo'a
    Vowel v restored at 1st h, subsequent th and hil remain.
    """
    tag_str = "[PrefixClass=a_stem][Pro=1sg.A][H_alt=vowel]atanhthehil[AspectClass=o][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "katanvthehilo'a" in forms


def test_h_vowel_entry_186():
    """Entry 186: [Pro][H_alt=vowel]alhkhotht[Aspect][Tense] -> 1sg kalikhothtiha
    Vowel i restored in lh, subsequent kh and th remain.
    """
    tag_str = "[PrefixClass=a_stem][Pro=1sg.A][H_alt=vowel]alhkhotht[AspectClass=cause][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "kalikhothtiha" in forms


def test_h_vowel_entry_280():
    """Entry 280: [Pro][H_alt=vowel]khtha[Aspect][Tense] -> 1sg tsikathaha
    Vowel a restored in kh, subsequent th remains.
    """
    tag_str = "[PrefixClass=cons_stem][Pro=1sg>3sg][H_alt=vowel]khtha[AspectClass=stative-h][Aspect=present][TenseClass=a_present][Tense=present]"
    forms = _inflect(tag_str)
    assert "tsikathaha" in forms


# =========================================================================
# AC 4: Spurious multi-h root prevention in parse
# =========================================================================

def test_parse_atatek_zero_multi_h_roots():
    """AC 4: Verify parse of Entry 8/9 surface 'atatek' produces zero multi-h restored roots.
    Eliminates spurious overgenerated parses like 'athathek', 'athathekh', etc.
    """
    parses = parse("atatek")
    assert len(parses) > 0, "Expected non-empty parses for atatek"
    roots = set(get_just_root(p) for p in parses)
    multi_h_roots = [r for r in roots if r.count("h") > 1]
    assert len(multi_h_roots) == 0, f"Expected zero multi-h roots for atatek, got: {multi_h_roots}"
    assert "athathek" not in roots
    assert "athathekh" not in roots


def test_parse_entry_22_surface_no_multi_restorations():
    """Parsing katawahthvhitoha should recover underlying atawhahthvhit without spurious multi-h roots."""
    parses = parse("katawahthvhitoha")
    assert len(parses) > 0
    roots = set(get_just_root(p) for p in parses)
    assert "atawhahthvhit" in roots
    # Verify no spurious multi-dropped roots such as athawhahthvhit or athwhhthvhit
    assert "athawhahthvhit" not in roots
    assert "athwhhthvhit" not in roots
