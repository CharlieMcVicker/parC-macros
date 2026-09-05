"""
tests/test_clean_inplace_generation.py

Integration test suite for TASK-112:
- Generates from chr-config/ to a temporary output directory
- Asserts all generated YAML files exist and pass validate_yaml_file
- Compares generated YAMLs against chr-generated/ for 100% parity
- Compiles open inflect graph and open parse graph with parC and verifies 983 states
- End-to-end inflection and parse roundtrip verification
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest
import pynini
import yaml

from parc_macros.generate_markers import generate_markers
from parc_macros.yaml_validation import validate_yaml_file


REPO_ROOT = Path(__file__).parent.parent.resolve()
CLEAN_CONFIG_DIR = REPO_ROOT / "chr-config"
INPLACE_GEN_DIR = REPO_ROOT / "chr-generated"


@pytest.fixture(scope="module")
def generated_clean_dir():
    """Generates marker configuration from chr-config to a temporary directory."""
    tmpdir = tempfile.mkdtemp(prefix="clean_inplace_gen_")
    out_path = Path(tmpdir)

    generate_markers(str(CLEAN_CONFIG_DIR), str(out_path), in_place=True)

    yield out_path

    if out_path.exists():
        shutil.rmtree(out_path)


@pytest.fixture(scope="module", autouse=True)
def setup_clean_env(generated_clean_dir):
    """Sets up parC YAML_DIR and caches pointing to generated_clean_dir, and restores after."""
    from parC.constants import set_yaml_dir
    from parC.grammar.paradigm_compilation import clear_all_caches
    import parse_chr_dict.parse as parse_mod

    orig_yaml_dir = os.environ.get("YAML_DIR")

    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    set_yaml_dir(str(generated_clean_dir))
    os.environ["YAML_DIR"] = str(generated_clean_dir)

    yield

    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    if orig_yaml_dir:
        set_yaml_dir(orig_yaml_dir)
        os.environ["YAML_DIR"] = orig_yaml_dir


def test_clean_inplace_yamls_exist_and_validate(generated_clean_dir):
    """Asserts all required YAMLs exist and pass validate_yaml_file."""
    assert generated_clean_dir.exists()
    assert (generated_clean_dir / "Morphotactics/Paradigm/verb.yaml").exists()
    assert (generated_clean_dir / "Phonology/Inventory/alphabet.yaml").exists()
    assert (generated_clean_dir / "Phonology/Patterns/phoneme_groups.yaml").exists()
    assert (generated_clean_dir / "Phonology/Rules/pro_replace.yaml").exists()
    assert (generated_clean_dir / "Phonology/Rules/aspect_replace.yaml").exists()
    assert (generated_clean_dir / "Phonology/Rules/tense_replace.yaml").exists()
    assert (generated_clean_dir / "Phonology/Rules/drop_root_final.yaml").exists()
    assert (generated_clean_dir / "Phonology/Rules/drop_stem_initial_vowel.yaml").exists()
    assert (generated_clean_dir / "Phonology/Rules/h_alternation.yaml").exists()
    assert (generated_clean_dir / "Phonology/Rules/insert_di.yaml").exists()
    assert (generated_clean_dir / "Phonology/Rules/insert_wi.yaml").exists()
    assert (generated_clean_dir / "Exponence/FeatureDefinitions/verb_features.yaml").exists()
    assert (generated_clean_dir / "Lexicon/PartOfSpeech/verb.yaml").exists()

    yaml_files = list(generated_clean_dir.glob("**/*.yaml"))
    assert len(yaml_files) >= 13, f"Expected at least 13 YAML files, found {len(yaml_files)}"

    for yf in sorted(yaml_files):
        assert validate_yaml_file(yf) is True, f"Schema validation failed for {yf}"


def test_clean_inplace_parity_against_reference(generated_clean_dir):
    """Compares generated YAML files against chr-generated for full data parity."""
    ref_yamls = sorted([
        p.relative_to(INPLACE_GEN_DIR)
        for p in INPLACE_GEN_DIR.glob("**/*.yaml")
        if ".cache" not in p.parts
    ])

    for rel_p in ref_yamls:
        gen_file = generated_clean_dir / rel_p
        ref_file = INPLACE_GEN_DIR / rel_p

        assert gen_file.exists(), f"Generated output is missing {rel_p}"

        with open(gen_file, "r", encoding="utf-8") as f1, open(ref_file, "r", encoding="utf-8") as f2:
            gen_data = yaml.safe_load(f1)
            ref_data = yaml.safe_load(f2)

        assert gen_data == ref_data, f"YAML content mismatch in {rel_p}"


def test_clean_inplace_inflect_graph_compilation_998_states():
    """Compiles open inflect graph with parC and verifies exact 998 states."""
    from parC.grammar.paradigm_compilation import get_open_inflect_graph

    # Compile with infer_lexical_features=False
    inflect_no_infer = get_open_inflect_graph("verb", infer_lexical_features=False)
    assert inflect_no_infer is not None
    assert inflect_no_infer.num_states() == 998

    # Compile with infer_lexical_features=True
    inflect_infer = get_open_inflect_graph("verb", infer_lexical_features=True)
    assert inflect_infer is not None
    assert inflect_infer.num_states() == 998


def test_clean_inplace_parse_graph_compilation_998_states():
    """Compiles open parse graph with parC and verifies exact 998 states."""
    from parC.grammar.paradigm_compilation import get_open_parse_graph

    # Compile with infer_lexical_features=False
    parse_no_infer = get_open_parse_graph(
        "verb", infer_lexical_features=False, non_deterministic_cleanup=True
    )
    assert parse_no_infer is not None
    assert parse_no_infer.num_states() == 998

    # Compile with infer_lexical_features=True
    parse_infer = get_open_parse_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=True
    )
    assert parse_infer is not None
    assert parse_infer.num_states() == 998


def test_clean_inplace_roundtrip_inflection_and_parse():
    """Tests end-to-end transduction of in-place tag strings on graphs compiled from clean config."""
    from parC.grammar.paradigm_compilation import get_open_inflect_graph, get_open_parse_graph
    from parC.grammar.acceptor_compilation import fsm_strings, word_fsa

    inflect_fst = get_open_inflect_graph("verb", infer_lexical_features=False)
    parse_fst = get_open_parse_graph("verb", infer_lexical_features=False, non_deterministic_cleanup=True)

    tag_str = "[PrefixClass=a_stem][Pro=1sg.A][H_alt=none][AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present]"
    input_fsa = word_fsa(tag_str)
    out_fst = pynini.compose(input_fsa, inflect_fst)
    out_proj = pynini.project(out_fst, "output").optimize()
    surface_forms = fsm_strings(out_proj)

    assert surface_forms == ["[BOW]ka'a[EOW]"]

    # Parse back
    surf_fsa = word_fsa("ka'a")
    parsed_fst = pynini.compose(surf_fsa, parse_fst)
    parsed_proj = pynini.project(parsed_fst, "output").optimize()

    match = pynini.intersect(input_fsa, parsed_proj).optimize()
    assert match.num_states() > 0
