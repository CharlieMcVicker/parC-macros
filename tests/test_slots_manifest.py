import pynini
import pytest
from parC.grammar.acceptor_compilation import fsm_strings
from parse_chr_dict.parse import (
    build_root_filter_fsa,
    get_default_symbol_table,
    get_parse_graph,
    parse_surface,
)
from parse_chr_dict.slots import (
    get_root_boundary_tag_prefixes,
    get_slot_manifest,
    get_slot_name_to_tag_map,
    get_slot_tag_map,
)


def test_get_slot_manifest_default():
    manifest = get_slot_manifest()
    assert isinstance(manifest, dict)
    assert "slots" in manifest
    assert len(manifest["slots"]) >= 3

    slot_names = [s["name"] for s in manifest["slots"]]
    assert "pronominal" in slot_names
    assert "aspect" in slot_names
    assert "tense" in slot_names

    assert "template" in manifest
    assert "<H_alt>" in manifest["template"]
    assert "<AspectClass>" in manifest["template"]

    assert "root_boundaries" in manifest
    assert manifest["root_boundaries"]["left"] == "<H_alt>"
    assert manifest["root_boundaries"]["right"] == "<AspectClass>"

    assert "tag_to_slot" in manifest
    assert manifest["tag_to_slot"]["PrefixClass"] == "pronominal"
    assert manifest["tag_to_slot"]["AspectClass"] == "aspect"


def test_get_slot_manifest_fallback():
    fallback = get_slot_manifest("/nonexistent/path/slots.json")
    assert isinstance(fallback, dict)
    assert "slots" in fallback
    assert "template" in fallback
    assert "root_boundaries" in fallback
    assert fallback["root_boundaries"]["left"] == "<H_alt>"
    assert fallback["root_boundaries"]["right"] == "<AspectClass>"


def test_get_root_boundary_tag_prefixes():
    # Default manifest
    left, right = get_root_boundary_tag_prefixes()
    assert left == "[H_alt="
    assert right == "[AspectClass="

    # Custom manifest
    custom = {
        "root_boundaries": {
            "left": "<PreRootBoundary>",
            "right": "<PostRootBoundary>",
        }
    }
    c_left, c_right = get_root_boundary_tag_prefixes(custom)
    assert c_left == "[PreRootBoundary="
    assert c_right == "[PostRootBoundary="


def test_get_slot_tag_map():
    tag_map = get_slot_tag_map()
    assert tag_map["PrefixClass"] == "prefix_class"
    assert tag_map["Pro"] == "pronominal"
    assert tag_map["AspectClass"] == "aspect_class"
    assert tag_map["Variant"] == "variant"
    assert tag_map["Aspect"] == "aspect"
    assert tag_map["Tense"] == "tense"
    assert tag_map["H_alt"] == "h_alt_tag"

    name_to_tag = get_slot_name_to_tag_map()
    assert name_to_tag["prefix_class"] == "PrefixClass"
    assert name_to_tag["pronominal"] == "Pro"
    assert name_to_tag["aspect_class"] == "AspectClass"
    assert name_to_tag["variant"] == "Variant"
    assert name_to_tag["aspect"] == "Aspect"
    assert name_to_tag["tense"] == "Tense"


def test_build_root_filter_fsa_accepts_valid_and_filters_invalid():
    # Empty allowed_roots returns None
    assert build_root_filter_fsa([]) is None

    # Allowed root: tateka
    filter_fsa = build_root_filter_fsa(["tateka"])
    assert filter_fsa is not None

    base_graph = get_parse_graph()
    syms = base_graph.output_symbols() or get_default_symbol_table()

    def filter_accepts(tokens: list[str]) -> bool:
        test_fsa = pynini.accep(" ".join(tokens), token_type=syms)
        res = pynini.intersect(test_fsa, filter_fsa)
        return res.num_states() > 0 and res.start() != pynini.NO_STATE_ID

    # Valid parse string for katateka (root = tateka)
    valid_tokens = [
        "[PrefixClass=a_stem]",
        "[Pro=3sg.A]",
        "[H_alt=none]",
        *"tateka",
        "[AspectClass=a]",
        "[Aspect=completive]",
        "[Tense=immediate]",
    ]
    assert filter_accepts(valid_tokens)

    # Invalid root parse string (root = woniha)
    invalid_tokens = [
        "[PrefixClass=a_stem]",
        "[Pro=3sg.A]",
        "[H_alt=none]",
        *"woniha",
        "[AspectClass=a]",
        "[Aspect=completive]",
        "[Tense=immediate]",
    ]
    assert not filter_accepts(invalid_tokens)

    # Test via parse_surface
    results_valid = parse_surface("atateka", allowed_roots=["atateka"])
    assert len(results_valid) > 0
    assert all("atateka" in r for r in results_valid)

    results_invalid = parse_surface("atateka", allowed_roots=["woniha"])
    assert len(results_invalid) == 0
