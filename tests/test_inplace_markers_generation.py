"""
tests/test_inplace_markers_generation.py

Unit and integration tests for TASK-102.3:
- In-place 2-tag string_map rules generation (AC 1)
- Paradigm YAML with stage-ordered global_markers without ContingentFeatureMarkers (AC 2)
- Backwards compatibility with standard trailing-label configs (AC 3)
- JSON schema validation of generated YAML files (AC 4)
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest
import yaml

from parc_macros.generate_markers import generate_markers, generate_inplace_paradigm_config
from parc_macros.generate_morpheme_replace_rules import (
    generate_morpheme_replace_rules,
    is_in_place_mode,
    get_class_tag_title,
)
from parc_macros.yaml_validation import validate_yaml_file, validate_yaml_content


def test_is_in_place_mode_detection():
    """Verify in-place mode detection across configs and templates."""
    # chr-inplace-config has <PrefixClass> in open_root_template
    assert is_in_place_mode("chr-inplace-config") is True

    # Legacy configs should be detected as False
    assert is_in_place_mode("chr-config") is False
    assert is_in_place_mode("spanish-config") is False
    assert is_in_place_mode("min-min-config") is False

    # Dictionary configs
    assert is_in_place_mode({"paradigm": {"in_place": True}}) is True
    assert is_in_place_mode({"paradigm": {"use_in_place_tags": True}}) is True
    assert is_in_place_mode({"paradigm": {"open_root_template": "<PrefixClass><Pro><Root>"}}) is True
    assert is_in_place_mode({"paradigm": {"open_root_template": "[WI]?[DIST]?[Pro]<Root>[Aspect]"}}) is False
    assert is_in_place_mode(None) is False


def test_get_class_tag_title():
    """Verify mapping from class feature names to tag titles."""
    assert get_class_tag_title("prefix_class") == "PrefixClass"
    assert get_class_tag_title("aspect_class") == "AspectClass"
    assert get_class_tag_title("tense_present_class") == "TenseClass"
    assert get_class_tag_title("tense_class") == "TenseClass"
    assert get_class_tag_title("custom_stem_class") == "CustomStemClass"
    assert get_class_tag_title("custom", {"class_tag": "[MyClassTag]"}) == "MyClassTag"


def test_inplace_2_tag_rules_generation_ac1():
    """
    AC 1: Support generating in-place 2-tag string_map rules:
    ([PrefixClass=...][Pro=...], [AspectClass=...][Aspect=...], [TenseClass=...][Tense=...])
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        generate_morpheme_replace_rules("chr-inplace-config", tmp_dir, in_place=True)

        rules_dir = Path(tmp_dir) / "Phonology/Rules"
        assert rules_dir.exists()

        # 1. Check pro_replace.yaml
        pro_file = rules_dir / "pro_replace.yaml"
        assert pro_file.exists()
        with open(pro_file, "r", encoding="utf-8") as f:
            pro_rules = yaml.safe_load(f)
        assert validate_yaml_content(pro_rules) is True
        assert len(pro_rules["rules"]) == 1
        rule = pro_rules["rules"][0]
        assert rule["name"] == "pro_replace"
        pro_map = dict(rule["string_map"])
        # Check specific known mappings
        assert pro_map["[PrefixClass=a_stem][Pro=1sg.A]"] == "k"
        assert pro_map["[PrefixClass=cons_stem][Pro=1sg.A]"] == "tsi"
        assert pro_map["[PrefixClass=e_stem][Pro=3sg.A]"] == ""

        # 2. Check aspect_replace.yaml
        aspect_file = rules_dir / "aspect_replace.yaml"
        assert aspect_file.exists()
        with open(aspect_file, "r", encoding="utf-8") as f:
            aspect_rules = yaml.safe_load(f)
        assert validate_yaml_content(aspect_rules) is True
        aspect_map = dict(aspect_rules["rules"][0]["string_map"])
        assert aspect_map["[AspectClass=become][Aspect=completive]"] == "ts"
        assert aspect_map["[AspectClass=a][Aspect=present]"] == "a'"
        assert aspect_map["[AspectClass=a][Aspect=completive]"] == ""

        # 3. Check tense_replace.yaml
        tense_file = rules_dir / "tense_replace.yaml"
        assert tense_file.exists()
        with open(tense_file, "r", encoding="utf-8") as f:
            tense_rules = yaml.safe_load(f)
        assert validate_yaml_content(tense_rules) is True
        tense_map = dict(tense_rules["rules"][0]["string_map"])
        assert tense_map["[TenseClass=a_present][Tense=present]"] == "a"
        assert tense_map["[TenseClass=a_present][Tense=immediate]"] == ""
        assert tense_map["[TenseClass=i_present][Tense=present]"] == "i"


def test_inplace_paradigm_generation_ac2():
    """
    AC 2: Support generating Paradigm YAML with stage-ordered global_markers
    and without ContingentFeatureMarkers when in in-place mode.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "out"
        generate_markers("chr-inplace-config", str(out_dir))

        # ContingentFeatureMarkers directory should be empty
        cfm_dir = out_dir / "Exponence/ContingentFeatureMarkers"
        assert len(list(cfm_dir.glob("*.yaml"))) == 0

        # Paradigm file should exist and contain stage-ordered global_markers
        paradigm_file = out_dir / "Morphotactics/Paradigm/verb.yaml"
        assert paradigm_file.exists()
        with open(paradigm_file, "r", encoding="utf-8") as f:
            paradigm_data = yaml.safe_load(f)

        assert paradigm_data["kind"] == "Paradigm"
        assert paradigm_data["part_of_speech"] == "$verb"
        assert "contingent_markers" not in paradigm_data
        assert "global_markers" in paradigm_data

        expected_stages = [
            "final_dropping",
            "aspect_suffix",
            "h_alternation",
            "drop_stem_initial_vowel",
            "pronominal",
            "tense",
            "insert_dist",
            "insert_wi",
        ]
        assert paradigm_data["stage_order"] == expected_stages

        gm = paradigm_data["global_markers"]
        assert len(gm) == len(expected_stages)
        # Stage order of global_markers must match stage_order
        for idx, stage in enumerate(expected_stages):
            assert gm[idx]["stage"] == stage
            assert gm[idx]["kind"] == "rule"
            assert gm[idx]["value"].startswith("$")

        # Specific stage rule associations
        gm_map = {m["stage"]: m["value"] for m in gm}
        assert gm_map["final_dropping"] == "$drop_root_final"
        assert gm_map["aspect_suffix"] == "$aspect_replace"
        assert gm_map["h_alternation"] == "$h_alternation"
        assert gm_map["drop_stem_initial_vowel"] == "$drop_stem_initial_vowel"
        assert gm_map["pronominal"] == "$pro_replace"
        assert gm_map["tense"] == "$tense_replace"


def test_explicit_global_markers_in_verb_yaml_ac2():
    """Verify explicit global_markers defined in verb.yaml are preserved."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg_dir = Path(tmp_dir) / "cfg"
        shutil.copytree("chr-inplace-config", str(cfg_dir))

        # Inject explicit custom global_markers in verb.yaml
        verb_yaml = cfg_dir / "verb.yaml"
        with open(verb_yaml, "r", encoding="utf-8") as f:
            v_data = yaml.safe_load(f)

        custom_gm = [
            {"stage": "final_dropping", "value": "$drop_root_final"},
            {"stage": "aspect_suffix", "value": "$aspect_replace"},
            {"stage": "h_alternation", "value": "$h_alternation"},
            {"stage": "drop_stem_initial_vowel", "value": "$drop_stem_initial_vowel"},
            {"stage": "pronominal", "value": "$pro_replace"},
            {"stage": "tense", "value": "$tense_replace"},
            {"stage": "insert_dist", "value": "$insert_di"},
            {"stage": "insert_wi", "value": "$insert_wi"},
        ]
        v_data["paradigm"]["global_markers"] = custom_gm
        with open(verb_yaml, "w", encoding="utf-8") as f:
            yaml.dump(v_data, f)

        out_dir = Path(tmp_dir) / "out"
        generate_markers(str(cfg_dir), str(out_dir))

        paradigm_file = out_dir / "Morphotactics/Paradigm/verb.yaml"
        with open(paradigm_file, "r", encoding="utf-8") as f:
            res = yaml.safe_load(f)

        assert res["global_markers"][6]["value"] == "$insert_di"
        assert res["global_markers"][7]["value"] == "$insert_wi"


def test_backwards_compatibility_ac3():
    """
    AC 3: Ensure strict backwards compatibility with standard trailing-label configs
    (spanish-config, chr-config, min-min-config).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. chr-config
        chr_out = Path(tmp_dir) / "chr_out"
        generate_markers("chr-config", str(chr_out))
        cfm_files = list((chr_out / "Exponence/ContingentFeatureMarkers").glob("*.yaml"))
        assert len(cfm_files) == 3, f"Expected 3 CFM files for chr-config, got {len(cfm_files)}"
        with open(chr_out / "Morphotactics/Paradigm/verb.yaml", "r", encoding="utf-8") as f:
            chr_paradigm = yaml.safe_load(f)
        assert "contingent_markers" in chr_paradigm
        assert "global_markers" not in chr_paradigm

        # 2. min-min-config
        min_out = Path(tmp_dir) / "min_out"
        generate_markers("min-min-config", str(min_out))
        assert (min_out / "Morphotactics/Paradigm/verb.yaml").exists()

        # 3. spanish-config
        sp_out = Path(tmp_dir) / "sp_out"
        generate_markers("spanish-config", str(sp_out))
        sp_paradigms = list((sp_out / "Morphotactics/Paradigm").glob("*.yaml"))
        assert len(sp_paradigms) >= 4


def test_yaml_schema_validation_ac4():
    """
    AC 4: Verify generated YAML configs pass JSON schema validation.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "out"
        generate_markers("chr-inplace-config", str(out_dir))

        all_yamls = list(out_dir.glob("**/*.yaml"))
        assert len(all_yamls) >= 10, f"Expected >= 10 YAML files, found {len(all_yamls)}"

        for yf in all_yamls:
            assert validate_yaml_file(yf) is True, f"Schema validation failed for {yf}"
