"""
tests/test_segmented_paradigm.py

Integration test suite for TASK-175.4:
- AC 1: Unit test verifies `inflect("verb_segmented", ...)` outputs expected structured format:
        `[Pro=...]...-[Root]...[drop]...-[Aspect=...]...-[Tense=...]...` across verb forms
        (a-stem vowel drops, root-final drops, prefix/aspect/tense morpheme anchors with hyphens).
- AC 2: Test canonical dictionary root extraction by removing `[drop]` tags from segmented output.
- AC 3: Test surface slice extraction by stripping elided characters and tags to reconstruct the exact surface word.
- AC 4: Test direct transduction from surface form to segmented string via composed parse/inflect graphs:
        $T_{\\text{segment}} = \\text{PARSE}(\\text{verb}) \\circ \\text{INFLECT}(\\text{verb\\_segmented})$.
"""

import os
from pathlib import Path
import re
import pytest
import pynini

from parc_macros.generate_markers import generate_markers
from parC.constants import set_yaml_dir
from parC.grammar.acceptor_compilation import fsm_strings, word_fsa
from parC.grammar.paradigm_compilation import clear_all_caches, get_open_inflect_graph, get_open_parse_graph
import parse_chr_dict.parse as parse_mod


REPO_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_DIR = REPO_ROOT / "chr-config"
GEN_DIR = REPO_ROOT / "chr-generated"


@pytest.fixture(scope="module", autouse=True)
def setup_segmented_env():
    """Ensure chr-generated exists, configure parC YAML_DIR, and restore after."""
    orig_yaml_dir = os.environ.get("YAML_DIR")

    generate_markers(str(CONFIG_DIR), str(GEN_DIR))

    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    set_yaml_dir(str(GEN_DIR))
    os.environ["YAML_DIR"] = str(GEN_DIR)

    yield

    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    if orig_yaml_dir:
        set_yaml_dir(orig_yaml_dir)
        os.environ["YAML_DIR"] = orig_yaml_dir


def extract_canonical_root(segmented_str: str) -> str:
    """
    Extract canonical dictionary root from segmented output by:
    1. Finding the root segment between prefix and aspect markers.
    2. Stripping feature tags and removing any [drop] elision tags.
    """
    clean = segmented_str.replace("[BOW]", "").replace("[EOW]", "")
    parts = clean.split("-")
    # Identify the root part: morpheme slice not starting with prefix tags or aspect/tense tags
    root_part = None
    for p in parts:
        if not (
            p.startswith("[Pro=")
            or p.startswith("[PrefixClass=")
            or p.startswith("[Aspect=")
            or p.startswith("[Tense=")
            or p.startswith("[NFS=")
        ):
            root_part = p
            break
    if root_part is None:
        return ""
    # Strip any feature tags inside root part and remove [drop] markers
    no_tags = re.sub(r"\[(?!drop\])[^\]]+\]", "", root_part)
    return no_tags.replace("[drop]", "")


def extract_surface_slices(segmented_str: str) -> list[str]:
    """
    Extract surface-aligned morpheme slices by:
    1. Splitting on hyphen boundaries.
    2. Stripping feature tags (e.g., [Pro=...], [Aspect=...], [Tense=...]).
    3. Stripping elided phones along with their [drop] tag (e.g., 'a[drop]' -> '').
    """
    clean = segmented_str.replace("[BOW]", "").replace("[EOW]", "")
    parts = clean.split("-")
    slices = []
    for p in parts:
        # Strip all feature tags except [drop]
        no_tags = re.sub(r"\[(?!drop\])[^\]]+\]", "", p)
        # Strip any phone followed immediately by [drop] (phonological deletion)
        no_elision = re.sub(r".\[drop\]", "", no_tags)
        slices.append(no_elision)
    return slices


def test_segmented_paradigm_inflection_format_ac1():
    """
    AC 1: Unit test verifies `inflect('verb_segmented', ...)` outputs expected structured format:
    `[Pro=...]...-[Root]...[drop]...-[Aspect=...]...-[Tense=...]...` for various Cherokee verb forms.
    """
    inflect_seg = get_open_inflect_graph("verb_segmented", infer_lexical_features=False)

    # 1. 1sg.A present of atateka (a-stem): k-atatek-a'a (prefix k-, no a-stem dropping for 1sg)
    pres_1sg = "[PrefixClass=a_stem][Pro=1sg.A][H_metathesis=none][H_alt=none]atatek[AspectClass=a][Aspect=present][Tense=present_a]"
    out_1sg = pynini.compose(word_fsa(pres_1sg), inflect_seg)
    forms_1sg = fsm_strings(pynini.project(out_1sg, "output").optimize())
    assert len(forms_1sg) == 1
    assert forms_1sg[0] == "[BOW][Pro=1sg.A]k-atatek-[Aspect=present]a'-[Tense=present_a]a[EOW]"

    # 2. 3sg.A present of atateka (a-stem vowel drop: a[drop]): [Pro=3sg.A]a-a[drop]tatek-[Aspect=present]a'-[Tense=present_a]a
    pres_3sg = "[PrefixClass=a_stem][Pro=3sg.A][H_metathesis=none][H_alt=none]atatek[AspectClass=a][Aspect=present][Tense=present_a]"
    out_3sg = pynini.compose(word_fsa(pres_3sg), inflect_seg)
    forms_3sg = fsm_strings(pynini.project(out_3sg, "output").optimize())
    assert len(forms_3sg) == 1
    assert forms_3sg[0] == "[BOW][Pro=3sg.A]a-a[drop]tatek-[Aspect=present]a'-[Tense=present_a]a[EOW]"

    # 3. 3sg.A immediate of atateka with apl class (both stem-initial drop a[drop] and root-final drop a[drop])
    apl_3sg = "[PrefixClass=a_stem][Pro=3sg.A][H_metathesis=none][H_alt=none]atateka[AspectClass=apl][Aspect=immediate][Tense=immediate]"
    out_apl_3sg = pynini.compose(word_fsa(apl_3sg), inflect_seg)
    forms_apl_3sg = fsm_strings(pynini.project(out_apl_3sg, "output").optimize())
    assert len(forms_apl_3sg) == 1
    assert forms_apl_3sg[0] == "[BOW][Pro=3sg.A]a-a[drop]tateka[drop]-[Aspect=immediate]hsi-[Tense=immediate][EOW]"

    # 4. 2sg.A immediate of atateka with apl class (prefix h-, no initial vowel drop, only root-final drop a[drop])
    apl_2sg = "[PrefixClass=a_stem][Pro=2sg.A][H_metathesis=none][H_alt=none]atateka[AspectClass=apl][Aspect=immediate][Tense=immediate]"
    out_apl_2sg = pynini.compose(word_fsa(apl_2sg), inflect_seg)
    forms_apl_2sg = fsm_strings(pynini.project(out_apl_2sg, "output").optimize())
    assert len(forms_apl_2sg) == 1
    assert forms_apl_2sg[0] == "[BOW][Pro=2sg.A]h-atateka[drop]-[Aspect=immediate]hsi-[Tense=immediate][EOW]"


def test_canonical_dictionary_root_extraction_ac2():
    """
    AC 2: Test helper/logic verifying extraction of canonical dictionary root from segmented output
    by removing [drop] tokens.
    """
    inflect_seg = get_open_inflect_graph("verb_segmented", infer_lexical_features=False)

    # 1. Root with initial vowel drop: atateka in 3sg.A
    pres_3sg = "[PrefixClass=a_stem][Pro=3sg.A][H_metathesis=none][H_alt=none]atateka[AspectClass=a][Aspect=present][Tense=present_a]"
    out_3sg = pynini.compose(word_fsa(pres_3sg), inflect_seg)
    seg_3sg = fsm_strings(pynini.project(out_3sg, "output").optimize())[0]
    assert "[drop]" in seg_3sg
    extracted_root = extract_canonical_root(seg_3sg)
    assert extracted_root == "atateka"

    # 2. Root with both initial and final drops: atateka with apl immediate
    apl_3sg = "[PrefixClass=a_stem][Pro=3sg.A][H_metathesis=none][H_alt=none]atateka[AspectClass=apl][Aspect=immediate][Tense=immediate]"
    out_apl = pynini.compose(word_fsa(apl_3sg), inflect_seg)
    seg_apl = fsm_strings(pynini.project(out_apl, "output").optimize())[0]
    assert seg_apl.count("[drop]") == 2
    assert extract_canonical_root(seg_apl) == "atateka"

    # 3. Consonant stem verb: tvn
    cons_pres = "[PrefixClass=cons_stem][Pro=1sg.A][H_metathesis=none][H_alt=none]tvn[AspectClass=a][Aspect=present][Tense=present_a]"
    out_cons = pynini.compose(word_fsa(cons_pres), inflect_seg)
    seg_cons = fsm_strings(pynini.project(out_cons, "output").optimize())[0]
    assert extract_canonical_root(seg_cons) == "tvn"


def test_surface_slice_extraction_and_reconstruction_ac3():
    """
    AC 3: Test helper/logic verifying extraction of surface-aligned slices by stripping
    elided phones + [drop] and tags, matching the exact surface word.
    """
    inflect_seg = get_open_inflect_graph("verb_segmented", infer_lexical_features=False)
    inflect_surf = get_open_inflect_graph("verb", infer_lexical_features=False)

    test_inputs = [
        "[PrefixClass=a_stem][Pro=1sg.A][H_metathesis=none][H_alt=none]atateka[AspectClass=a][Aspect=present][Tense=present_a]",
        "[PrefixClass=a_stem][Pro=3sg.A][H_metathesis=none][H_alt=none]atateka[AspectClass=a][Aspect=present][Tense=present_a]",
        "[PrefixClass=a_stem][Pro=3sg.A][H_metathesis=none][H_alt=none]atateka[AspectClass=apl][Aspect=immediate][Tense=immediate]",
        "[PrefixClass=a_stem][Pro=2sg.A][H_metathesis=none][H_alt=none]atateka[AspectClass=apl][Aspect=immediate][Tense=immediate]",
        "[PrefixClass=cons_stem][Pro=1sg.A][H_metathesis=none][H_alt=none]tvn[AspectClass=a][Aspect=present][Tense=present_a]",
    ]

    for inp in test_inputs:
        inp_fsa = word_fsa(inp)
        seg_out = fsm_strings(pynini.project(pynini.compose(inp_fsa, inflect_seg), "output").optimize())[0]
        surf_out = fsm_strings(pynini.project(pynini.compose(inp_fsa, inflect_surf), "output").optimize())[0]

        expected_surface = surf_out.replace("[BOW]", "").replace("[EOW]", "")
        slices = extract_surface_slices(seg_out)
        reconstructed = "".join(slices)

        assert reconstructed == expected_surface, (
            f"Surface reconstruction failed for input {inp}:\n"
            f"Segmented: {seg_out}\n"
            f"Slices: {slices}\n"
            f"Reconstructed: {reconstructed} != Expected: {expected_surface}"
        )


def test_direct_surface_to_segmented_transduction_ac4():
    """
    AC 4: Test direct transduction from surface form to segmented string via composed parse/inflect graphs:
    T_segment = PARSE(verb) o INFLECT(verb_segmented).
    """
    parse_surf = get_open_parse_graph("verb", infer_lexical_features=False, non_deterministic_cleanup=True)
    inflect_seg = get_open_inflect_graph("verb_segmented", infer_lexical_features=False)

    # Test with surface form 'atateka'a' (3sg.A present of atatek-)
    surf_word = "atateka'a"
    surf_fsa = word_fsa(surf_word)

    # 1. PARSE(verb)
    parsed = pynini.compose(surf_fsa, parse_surf)
    assert parsed.num_states() > 0

    # 2. Composed with INFLECT(verb_segmented): T_segment = PARSE(verb) o INFLECT(verb_segmented)
    segmented_fst = pynini.compose(parsed, inflect_seg)
    segmented_proj = pynini.project(segmented_fst, "output").optimize()
    assert segmented_fst.num_states() > 0

    results = fsm_strings(segmented_proj)
    assert len(results) > 0

    # 3. Verify that the expected segmented string with morpheme boundaries, tags, and [drop] is present
    expected_segmented = "[BOW][Pro=3sg.A]a-a[drop]tatek-[Aspect=present]a'-[Tense=present_a]a[EOW]"
    assert expected_segmented in results

    # 4. Verify surface slice reconstruction on the target segmented hypothesis
    slices = extract_surface_slices(expected_segmented)
    reconstructed = "".join(slices)
    assert reconstructed == surf_word
