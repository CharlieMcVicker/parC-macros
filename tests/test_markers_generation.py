"""
tests/test_inplace_markers_generation.py

Unit and integration tests for TASK-102.3:
- In-place 2-tag string_map rules generation (AC 1)
- Paradigm YAML with stage-ordered global_markers without ContingentFeatureMarkers (AC 2)
- Backwards compatibility with standard trailing-label configs (AC 3)
- JSON schema validation of generated YAML files (AC 4)
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
import pytest
import yaml

from parc_macros.generate_markers import (
    derive_open_root_template,
    generate_markers,
    generate_paradigm_config,
)
from parc_macros.generate_morpheme_replace_rules import (
    generate_morpheme_replace_rules,
    get_class_tag_title,
)
from parc_macros.yaml_validation import validate_yaml_file, validate_yaml_content


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
        generate_morpheme_replace_rules("chr-config", tmp_dir)

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
        assert tense_map["[Tense=present_a]"] == "a"
        assert tense_map["[Tense=immediate]"] == ""
        assert tense_map["[Tense=present_i]"] == "i"


def test_inplace_paradigm_generation_ac2():
    """
    AC 2: Support generating Paradigm YAML with stage-ordered global_markers
    and without ContingentFeatureMarkers when in in-place mode.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "out"
        generate_markers("chr-config", str(out_dir))

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
            "tense",
            "h_alternation",
            "tag_h_metathesis",
            "drop_stem_initial_vowel",
            "pronominal",
            "h_metathesis",
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
        assert gm_map["tag_h_metathesis"] == "$tag_h_metathesis"
        assert gm_map["drop_stem_initial_vowel"] == "$drop_stem_initial_vowel"
        assert gm_map["pronominal"] == "$pro_replace"
        assert gm_map["h_metathesis"] == "$h_metathesis"
        assert gm_map["tense"] == "$tense_replace"


def test_explicit_global_markers_in_verb_yaml_ac2():
    """Verify explicit global_markers defined in verb.yaml are preserved."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg_dir = Path(tmp_dir) / "cfg"
        shutil.copytree("chr-config", str(cfg_dir))

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


def test_yaml_schema_validation_ac4():
    """
    AC 4: Verify generated YAML configs pass JSON schema validation.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "out"
        generate_markers("chr-config", str(out_dir))

        all_yamls = list(out_dir.glob("**/*.yaml"))
        assert len(all_yamls) >= 10, f"Expected >= 10 YAML files, found {len(all_yamls)}"

        for yf in all_yamls:
            assert validate_yaml_file(yf) is True, f"Schema validation failed for {yf}"


def test_inplace_aspect_variants_generation_task_111_2():
    """
    TASK-111.2: Verify that generate_morpheme_replace_rules supports [Variant=N] tags in in-place rules:
    - Semicolon-delimited values in CSV feature cells produce [AspectClass=Class][Variant=N][Aspect=Feature] for N >= 2
    - Default variant 1 and non-varying features emit standard 2-tag [AspectClass=Class][Aspect=Feature] rules
    - Non-varying classes (e.g. prefix_class, tense_class) emit clean 2-tag rules without [Variant=N]
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        generate_morpheme_replace_rules("chr-config", tmp_dir)

        rules_dir = Path(tmp_dir) / "Phonology/Rules"
        aspect_file = rules_dir / "aspect_replace.yaml"
        assert aspect_file.exists()

        with open(aspect_file, "r", encoding="utf-8") as f:
            aspect_data = yaml.safe_load(f)
        assert validate_yaml_content(aspect_data) is True

        aspect_map = dict(aspect_data["rules"][0]["string_map"])

        # 1. Non-varying cell: 'become' present is 'k'
        assert aspect_map["[AspectClass=become][Aspect=present]"] == "k"
        assert "[AspectClass=become][Variant=2][Aspect=present]" not in aspect_map

        # 2. Varying cell with multiple variants: 'become' infinitive is 'st;'ist;yhst;ist'
        assert aspect_map["[AspectClass=become][Aspect=infinitive]"] == "st"
        assert aspect_map["[AspectClass=become][Variant=2][Aspect=infinitive]"] == "'ist"
        assert aspect_map["[AspectClass=become][Variant=3][Aspect=infinitive]"] == "yhst"
        assert aspect_map["[AspectClass=become][Variant=4][Aspect=infinitive]"] == "ist"

        # 3. Row with leading empty variant: 'sk-s-hst' immediate is ';hi'
        assert aspect_map["[AspectClass=sk-s-hst][Aspect=immediate]"] == ""
        assert aspect_map["[AspectClass=sk-s-hst][Variant=2][Aspect=immediate]"] == "hi"

        # 4. Row with trailing empty variant: 'go' present is 'ek;'
        assert aspect_map["[AspectClass=go][Aspect=present]"] == "ek"
        assert aspect_map["[AspectClass=go][Variant=2][Aspect=present]"] == ""

        # 5. Verify non-varying classes (prefix_class, tense_present_class) emit clean 2-tag rules without [Variant=N]
        pro_file = rules_dir / "pro_replace.yaml"
        with open(pro_file, "r", encoding="utf-8") as f:
            pro_data = yaml.safe_load(f)
        pro_map = dict(pro_data["rules"][0]["string_map"])
        for pattern in pro_map.keys():
            assert "[Variant=" not in pattern, f"Unexpected Variant tag in pro rule: {pattern}"
            assert pattern.startswith("[PrefixClass=") and "[Pro=" in pattern

        tense_file = rules_dir / "tense_replace.yaml"
        with open(tense_file, "r", encoding="utf-8") as f:
            tense_data = yaml.safe_load(f)
        tense_map = dict(tense_data["rules"][0]["string_map"])
        for pattern in tense_map.keys():
            assert "[Variant=" not in pattern, f"Unexpected Variant tag in tense rule: {pattern}"
            assert pattern.startswith("[Tense=") and "[TenseClass=" not in pattern


def test_slots_json_manifest_generation():
    """Verify slots.json generation with slot definitions, template tokens, and root boundaries."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "out"
        generate_markers("chr-config", str(out_dir))

        slots_file = out_dir / "slots.json"
        assert slots_file.exists()
        with open(slots_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "slots" in data
        assert len(data["slots"]) == 3
        slot_names = [s["name"] for s in data["slots"]]
        assert slot_names == ["pronominal", "aspect", "tense"]

        # Check tag_to_slot
        assert data["tag_to_slot"]["PrefixClass"] == "pronominal"
        assert data["tag_to_slot"]["Pro"] == "pronominal"
        assert data["tag_to_slot"]["AspectClass"] == "aspect"
        assert data["tag_to_slot"]["Variant"] == "aspect"
        assert data["tag_to_slot"]["Aspect"] == "aspect"
        assert data["tag_to_slot"]["Tense"] == "tense"

        # Check template
        expected_template = [
            "<PrepronominalPrefixes>",
            "<PrefixClass>",
            "<Pro>",
            "<H_metathesis>",
            "<H_alt>",
            "<Root>",
            "<AspectClass>",
            "<Variant>",
            "<Aspect>",
            "<Tense>",
        ]
        assert data["template"] == expected_template

        # Check root boundaries
        assert data["root_boundaries"] == {
            "left": "<H_alt>",
            "right": "<AspectClass>",
        }


def test_paradigm_yaml_contains_slots_and_validates():
    """Verify Morphotactics/Paradigm/verb.yaml contains slots and validates against Paradigm.json."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "out"
        generate_markers("chr-config", str(out_dir))

        paradigm_file = out_dir / "Morphotactics/Paradigm/verb.yaml"
        assert paradigm_file.exists()
        with open(paradigm_file, "r", encoding="utf-8") as f:
            paradigm_data = yaml.safe_load(f)

        assert "slots" in paradigm_data
        assert len(paradigm_data["slots"]) == 3
        assert validate_yaml_content(paradigm_data) is True


def test_derive_open_root_template():
    """
    Test derive_open_root_template() with:
    - Backwards compatibility (explicit open_root_template in paradigm or verb_config)
    - Slot expansion with single tag group (e.g. tense -> <Tense>)
    - Slot expansion with composite tag groups (e.g. pronominal -> <PrefixClass><Pro>)
    - Slot expansion with optional tag group (e.g. aspect -> <AspectClass><Variant><Aspect>)
    - Direct pattern elements (<Pattern>)
    - slot:name and plain name slot references
    - Empty or missing template fallback
    """
    # 1. Backwards compatibility: explicit open_root_template preserved
    cfg_legacy = {
        "paradigm": {
            "open_root_template": "[WI]?[DIST]?<Phone>*"
        }
    }
    assert derive_open_root_template(cfg_legacy) == "[WI]?[DIST]?<Phone>*"

    # 2. Template expansion with single, composite, and optional tag groups
    cfg_dynamic = {
        "slots": [
            {
                "name": "pronominal",
                "structure": [
                    {"TagGroup": "PrefixClass", "optional": False},
                    {"TagGroup": "Pro", "optional": False},
                ],
            },
            {
                "name": "aspect",
                "structure": [
                    {"TagGroup": "AspectClass", "optional": False},
                    {"TagGroup": "Variant", "optional": True},
                    {"TagGroup": "Aspect", "optional": False},
                ],
            },
            {
                "name": "tense",
                "structure": [
                    {"TagGroup": "Tense", "optional": False},
                ],
            },
        ],
        "paradigm": {
            "template": [
                "<PrepronominalPrefixes>",
                "slot:pronominal",
                "<H_alt>",
                "<Root>",
                "slot:aspect",
                "tense",  # plain name reference
            ]
        },
    }
    derived = derive_open_root_template(cfg_dynamic)
    expected = "<PrepronominalPrefixes><PrefixClass><Pro><H_alt><Root><AspectClass><Variant><Aspect><Tense>"
    assert derived == expected

    # 3. Empty or missing template fallback
    assert derive_open_root_template({}) == ""
    assert derive_open_root_template({"paradigm": {}}) == ""


