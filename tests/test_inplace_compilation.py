"""
tests/test_inplace_compilation.py

Integration test suite for TASK-102.4:
- AC 1: Execute generator to produce chr-generated/ from chr-config/
- AC 2: Validate all generated YAML files against parc_macros schema suite
- AC 3: Compile open inflect graph with parC (infer_lexical_features=False and True) and verify zero errors
- AC 4: Compile open parse graph with parC (infer_lexical_features=False and True) and verify zero errors
- End-to-end inflection and parse verification on in-place morpheme tags
"""

import os
from pathlib import Path
import pytest
import pynini

from parc_macros.generate_markers import generate_markers
from parc_macros.yaml_validation import validate_yaml_file


REPO_ROOT = Path(__file__).parent.parent.resolve()
INPLACE_CONFIG_DIR = REPO_ROOT / "chr-config"
INPLACE_GEN_DIR = REPO_ROOT / "chr-generated"


@pytest.fixture(scope="module", autouse=True)
def setup_inplace_env():
    """Ensure chr-generated exists, configure parC YAML_DIR, and restore after."""
    from parC.constants import set_yaml_dir
    from parC.grammar.paradigm_compilation import clear_all_caches
    import parse_chr_dict.parse as parse_mod

    orig_yaml_dir = os.environ.get("YAML_DIR")

    # AC 1: Generate chr-generated from chr-config
    generate_markers(str(INPLACE_CONFIG_DIR), str(INPLACE_GEN_DIR), in_place=True)

    # Clear caches and set YAML_DIR to chr-generated
    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    set_yaml_dir(str(INPLACE_GEN_DIR))
    os.environ["YAML_DIR"] = str(INPLACE_GEN_DIR)

    yield

    # Restore original YAML_DIR and clear caches
    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    if orig_yaml_dir:
        set_yaml_dir(orig_yaml_dir)
        os.environ["YAML_DIR"] = orig_yaml_dir


def test_generator_execution_ac1():
    """AC 1: Execute generator to produce chr-generated/ from chr-config/."""
    assert INPLACE_GEN_DIR.exists()
    assert (INPLACE_GEN_DIR / "Morphotactics/Paradigm/verb.yaml").exists()
    assert (INPLACE_GEN_DIR / "Phonology/Inventory/alphabet.yaml").exists()
    assert (INPLACE_GEN_DIR / "Phonology/Patterns/phoneme_groups.yaml").exists()
    assert (INPLACE_GEN_DIR / "Phonology/Rules/pro_replace.yaml").exists()
    assert (INPLACE_GEN_DIR / "Phonology/Rules/aspect_replace.yaml").exists()
    assert (INPLACE_GEN_DIR / "Phonology/Rules/tense_replace.yaml").exists()
    assert (INPLACE_GEN_DIR / "Exponence/FeatureDefinitions/verb_features.yaml").exists()
    assert (INPLACE_GEN_DIR / "Lexicon/PartOfSpeech/verb.yaml").exists()


def test_yaml_schema_validation_ac2():
    """AC 2: Validate all generated YAML files against parc_macros schema suite."""
    yaml_files = list(INPLACE_GEN_DIR.glob("**/*.yaml"))
    assert len(yaml_files) >= 13, f"Expected at least 13 YAML files, found {len(yaml_files)}"

    for yf in sorted(yaml_files):
        assert validate_yaml_file(yf) is True, f"Schema validation failed for {yf}"


def test_compile_open_inflect_graph_ac3():
    """AC 3: Compile open inflect graph with parC (infer_lexical_features=False and True) and verify zero errors."""
    from parC.grammar.paradigm_compilation import get_open_inflect_graph

    # Compile with infer_lexical_features=False
    inflect_no_infer = get_open_inflect_graph("verb", infer_lexical_features=False)
    assert inflect_no_infer is not None
    assert inflect_no_infer.num_states() > 0
    assert inflect_no_infer.num_states() == 940

    # Compile with infer_lexical_features=True
    inflect_infer = get_open_inflect_graph("verb", infer_lexical_features=True)
    assert inflect_infer is not None
    assert inflect_infer.num_states() > 0
    assert inflect_infer.num_states() == 940


def test_compile_open_parse_graph_ac4():
    """AC 4: Compile open parse graph with parC (infer_lexical_features=False and True) and verify zero errors."""
    from parC.grammar.paradigm_compilation import get_open_parse_graph

    # Compile with infer_lexical_features=False, non_deterministic_cleanup=True
    parse_no_infer = get_open_parse_graph(
        "verb", infer_lexical_features=False, non_deterministic_cleanup=True
    )
    assert parse_no_infer is not None
    assert parse_no_infer.num_states() > 0
    assert parse_no_infer.num_states() == 940

    # Compile with infer_lexical_features=True, non_deterministic_cleanup=True
    parse_infer = get_open_parse_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=True
    )
    assert parse_infer is not None
    assert parse_infer.num_states() > 0
    assert parse_infer.num_states() == 940


def test_inplace_inflection_and_parse_roundtrip():
    """Test that open inflect and open parse graphs correctly transduce in-place tag strings."""
    from parC.grammar.paradigm_compilation import get_open_inflect_graph, get_open_parse_graph
    from parC.grammar.acceptor_compilation import fsm_strings, word_fsa

    inflect_fst = get_open_inflect_graph("verb", infer_lexical_features=False)
    parse_fst = get_open_parse_graph("verb", infer_lexical_features=False, non_deterministic_cleanup=True)

    # [PrefixClass=a_stem][Pro=1sg.A] -> k
    # [H_alt=none] (mandatory H_alt slot)
    # Root: '' (empty root)
    # [AspectClass=a][Aspect=present] -> a'
    # [TenseClass=a_present][Tense=present] -> a
    # Result: ka'a
    inner_str = "[PrefixClass=a_stem][Pro=1sg.A][H_alt=none][AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present]"
    input_fsa = word_fsa(inner_str)
    out_fst = pynini.compose(input_fsa, inflect_fst)
    out_proj = pynini.project(out_fst, "output").optimize()
    surface_forms = fsm_strings(out_proj)

    assert surface_forms == ["[BOW]ka'a[EOW]"]

    # Invert and parse back
    surf_fsa = word_fsa("ka'a")
    parsed_fst = pynini.compose(surf_fsa, parse_fst)
    parsed_proj = pynini.project(parsed_fst, "output").optimize()

    # Verify input_fsa is accepted in the parse projection
    match = pynini.intersect(input_fsa, parsed_proj).optimize()
    assert match.num_states() > 0


def test_inplace_distributive_allomorph_realization():
    """AC 5: Verify phonological realization across indicative (te-), imperative (th-), and infinitive (tsu-) forms."""
    from parC.grammar.paradigm_compilation import get_open_inflect_graph, get_open_parse_graph
    from parC.grammar.acceptor_compilation import fsm_strings, word_fsa
    from parse_chr_dict.parse import parse, read_inplace_parse

    # 1. Imperative distributive with [DIST=di] before h yields 'th-'
    imperative_parses = parse("thatanhesaka")
    di_imperatives = [p for p in imperative_parses if "[DIST=di]" in p]
    assert len(di_imperatives) > 0
    cfg_imp = read_inplace_parse(di_imperatives[0])
    assert "[DIST=di]" in cfg_imp.prepronominal_prefixes
    assert cfg_imp.to_labels_dict()["distributive"] == "+"

    # 2. Infinitive distributive with [DIST=di] before V yields 'tsu-'
    infinitive_parses = parse("tsutanhesesti")
    di_infinitives = [p for p in infinitive_parses if "[DIST=di]" in p]
    assert len(di_infinitives) > 0
    cfg_inf = read_inplace_parse(di_infinitives[0])
    assert "[DIST=di]" in cfg_inf.prepronominal_prefixes
    assert cfg_inf.to_labels_dict()["distributive"] == "+"

    # 3. Indicative distributive with [DIST=de] yields 'te-'
    indicative_parses = parse("tetanheseka")
    de_indicatives = [p for p in indicative_parses if "[DIST=de]" in p]
    assert len(de_indicatives) > 0
    cfg_ind = read_inplace_parse(de_indicatives[0])
    assert "[DIST=de]" in cfg_ind.prepronominal_prefixes
    assert cfg_ind.to_labels_dict()["distributive"] == "+"


def test_aspect_variants_and_elimination_of_overgeneration():
    """TASK-111.4: Verify that present tense has zero variant overgeneration and infinitive variants inflect."""
    from parC.grammar.paradigm_compilation import get_open_inflect_graph
    from parC.grammar.acceptor_compilation import fsm_strings, word_fsa

    inflect_fst = get_open_inflect_graph("verb", infer_lexical_features=False)

    # 1. Present tense for class 'become' - ONLY ONE path exists (no duplicate inf2, inf3, inf4 variants!)
    # [PrefixClass=a_stem][Pro=3sg.A][H_alt=none][AspectClass=become][Aspect=present][TenseClass=a_present][Tense=present]
    pres_str = "[PrefixClass=a_stem][Pro=3sg.A][H_alt=none][AspectClass=become][Aspect=present][TenseClass=a_present][Tense=present]"
    out_fst = pynini.compose(word_fsa(pres_str), inflect_fst)
    out_forms = fsm_strings(pynini.project(out_fst, "output").optimize())
    assert len(out_forms) == 1
    assert out_forms == ["[BOW]aka[EOW]"]

    # Verify that trying to pass [Variant=2] on present tense yields no valid surface forms (tags remain unconsumed)
    invalid_pres_str = "[PrefixClass=a_stem][Pro=3sg.A][H_alt=none][AspectClass=become][Variant=2][Aspect=present][TenseClass=a_present][Tense=present]"
    invalid_fst = pynini.compose(word_fsa(invalid_pres_str), inflect_fst)
    invalid_forms = [
        f
        for f in fsm_strings(pynini.project(invalid_fst, "output").optimize())
        if "[" not in f.replace("[BOW]", "").replace("[EOW]", "")
    ]
    assert len(invalid_forms) == 0

    # 2. Infinitive forms for class 'become'
    # Default (variant 1): no [Variant=N] tag -> st
    inf1_str = "[PrefixClass=a_stem][Pro=3sg.B][H_alt=none][AspectClass=become][Aspect=infinitive][TenseClass=a_present][Tense=infinitive]"
    out1_fst = pynini.compose(word_fsa(inf1_str), inflect_fst)
    assert fsm_strings(pynini.project(out1_fst, "output").optimize()) == ["[BOW]usti[EOW]"]

    # Variant 2: [Variant=2] -> 'ist
    inf2_str = "[PrefixClass=a_stem][Pro=3sg.B][H_alt=none][AspectClass=become][Variant=2][Aspect=infinitive][TenseClass=a_present][Tense=infinitive]"
    out2_fst = pynini.compose(word_fsa(inf2_str), inflect_fst)
    assert fsm_strings(pynini.project(out2_fst, "output").optimize()) == ["[BOW]u'isti[EOW]"]

    # Variant 3: [Variant=3] -> yhst
    inf3_str = "[PrefixClass=a_stem][Pro=3sg.B][H_alt=none][AspectClass=become][Variant=3][Aspect=infinitive][TenseClass=a_present][Tense=infinitive]"
    out3_fst = pynini.compose(word_fsa(inf3_str), inflect_fst)
    assert fsm_strings(pynini.project(out3_fst, "output").optimize()) == ["[BOW]uyhsti[EOW]"]

    # Variant 4: [Variant=4] -> ist
    inf4_str = "[PrefixClass=a_stem][Pro=3sg.B][H_alt=none][AspectClass=become][Variant=4][Aspect=infinitive][TenseClass=a_present][Tense=infinitive]"
    out4_fst = pynini.compose(word_fsa(inf4_str), inflect_fst)
    assert fsm_strings(pynini.project(out4_fst, "output").optimize()) == ["[BOW]uisti[EOW]"]



