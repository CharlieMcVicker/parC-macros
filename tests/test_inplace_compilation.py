"""
tests/test_inplace_compilation.py

Integration test suite for TASK-102.4:
- AC 1: Execute generator to produce chr-inplace-generated/ from chr-inplace-config/
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
INPLACE_CONFIG_DIR = REPO_ROOT / "chr-inplace-config"
INPLACE_GEN_DIR = REPO_ROOT / "chr-inplace-generated"


@pytest.fixture(scope="module", autouse=True)
def setup_inplace_env():
    """Ensure chr-inplace-generated exists, configure parC YAML_DIR, and restore after."""
    from parC.constants import set_yaml_dir
    from parC.grammar.paradigm_compilation import clear_all_caches

    orig_yaml_dir = os.environ.get("YAML_DIR")

    # AC 1: Generate chr-inplace-generated from chr-inplace-config
    generate_markers(str(INPLACE_CONFIG_DIR), str(INPLACE_GEN_DIR), in_place=True)

    # Clear caches and set YAML_DIR to chr-inplace-generated
    clear_all_caches()
    set_yaml_dir(str(INPLACE_GEN_DIR))
    os.environ["YAML_DIR"] = str(INPLACE_GEN_DIR)

    yield

    # Restore original YAML_DIR and clear caches
    clear_all_caches()
    if orig_yaml_dir:
        set_yaml_dir(orig_yaml_dir)
        os.environ["YAML_DIR"] = orig_yaml_dir


def test_generator_execution_ac1():
    """AC 1: Execute generator to produce chr-inplace-generated/ from chr-inplace-config/."""
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
    assert len(yaml_files) >= 14, f"Expected at least 14 YAML files, found {len(yaml_files)}"

    for yf in sorted(yaml_files):
        assert validate_yaml_file(yf) is True, f"Schema validation failed for {yf}"


def test_compile_open_inflect_graph_ac3():
    """AC 3: Compile open inflect graph with parC (infer_lexical_features=False and True) and verify zero errors."""
    from parC.grammar.paradigm_compilation import get_open_inflect_graph

    # Compile with infer_lexical_features=False
    inflect_no_infer = get_open_inflect_graph("verb", infer_lexical_features=False)
    assert inflect_no_infer is not None
    assert inflect_no_infer.num_states() > 0
    assert inflect_no_infer.num_states() == 953

    # Compile with infer_lexical_features=True
    inflect_infer = get_open_inflect_graph("verb", infer_lexical_features=True)
    assert inflect_infer is not None
    assert inflect_infer.num_states() > 0
    assert inflect_infer.num_states() == 956


def test_compile_open_parse_graph_ac4():
    """AC 4: Compile open parse graph with parC (infer_lexical_features=False and True) and verify zero errors."""
    from parC.grammar.paradigm_compilation import get_open_parse_graph

    # Compile with infer_lexical_features=False, non_deterministic_cleanup=True
    parse_no_infer = get_open_parse_graph(
        "verb", infer_lexical_features=False, non_deterministic_cleanup=True
    )
    assert parse_no_infer is not None
    assert parse_no_infer.num_states() > 0
    assert parse_no_infer.num_states() == 953

    # Compile with infer_lexical_features=True, non_deterministic_cleanup=True
    parse_infer = get_open_parse_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=True
    )
    assert parse_infer is not None
    assert parse_infer.num_states() > 0
    assert parse_infer.num_states() == 956


def test_inplace_inflection_and_parse_roundtrip():
    """Test that open inflect and open parse graphs correctly transduce in-place tag strings."""
    from parC.grammar.paradigm_compilation import get_open_inflect_graph, get_open_parse_graph
    from parC.grammar.acceptor_compilation import fsm_strings, word_fsa

    inflect_fst = get_open_inflect_graph("verb", infer_lexical_features=False)
    parse_fst = get_open_parse_graph("verb", infer_lexical_features=False, non_deterministic_cleanup=True)

    # [PrefixClass=a_stem][Pro=1sg.A] -> k
    # Root: '' (empty root)
    # [AspectClass=a][Aspect=present] -> a'
    # [TenseClass=a_present][Tense=present] -> a
    # Result: ka'a
    inner_str = "[PrefixClass=a_stem][Pro=1sg.A][AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present]"
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

