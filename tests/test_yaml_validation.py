import pytest
from parc_macros.yaml_validation import validate_yaml_content


def test_valid_feature_definitions():
    valid_data = {
        "kind": "FeatureDefinitions",
        "features": {
            "person": ["1sg", "2sg", "3sg"],
            "number": ["sg", "pl"]
        }
    }
    assert validate_yaml_content(valid_data) is True

def test_valid_feature_definitions_with_acceptor():
    valid_data = {
        "kind": "FeatureDefinitions",
        "features": {
            "prefix_class": [
                "normal",
                {
                    "name": "e_stem",
                    "acceptor": "e<Phone>*"
                }
            ]
        }
    }
    assert validate_yaml_content(valid_data) is True

def test_invalid_feature_definitions_missing_fields():
    invalid_data = {
        "kind": "FeatureDefinitions"
        # missing features
    }
    assert validate_yaml_content(invalid_data) is False

def test_invalid_feature_definitions_wrong_type():
    invalid_data = {
        "kind": "FeatureDefinitions",
        "features": {
            "person": "not-an-array"
        }
    }
    assert validate_yaml_content(invalid_data) is False

def test_valid_rules():
    valid_data = {
        "kind": "Rules",
        "rules": [
            {
                "name": "a_to_b",
                "input_pattern": "a",
                "output_pattern": "b"
            }
        ]
    }
    assert validate_yaml_content(valid_data) is True


def test_chr_inplace_config_yamls():
    from pathlib import Path
    import yaml
    from parc_macros.yaml_validation import validate_yaml_file

    config_dir = Path(__file__).parent.parent / "chr-inplace-config"
    assert config_dir.exists(), "chr-inplace-config directory must exist"

    # Validate verb.yaml
    verb_yaml = config_dir / "verb.yaml"
    assert verb_yaml.exists()
    with open(verb_yaml, "r", encoding="utf-8") as f:
        verb_data = yaml.safe_load(f)
    assert (
        verb_data["paradigm"]["open_root_template"]
        == "<PrepronominalPrefixes><PrefixClass><Pro><H_ALT>?<Root><AspectClass><Aspect><TenseClass><Tense>"
    )

    # Validate all Phonology YAML files with schema validator
    phonology_yamls = list((config_dir / "Phonology").glob("**/*.yaml"))
    assert len(phonology_yamls) == 5, f"Expected 5 phonology yaml files, found {len(phonology_yamls)}"
    for yf in phonology_yamls:
        assert validate_yaml_file(yf) is True, f"Validation failed for {yf}"

    # Verify Patterns
    patterns_yaml = config_dir / "Phonology/Patterns/phoneme_groups.yaml"
    with open(patterns_yaml, "r", encoding="utf-8") as f:
        pat_data = yaml.safe_load(f)
    pat_map = {p["ref"]: p["pattern"] for p in pat_data["patterns"]}
    assert pat_map["<PrepronominalPrefixes>"] == "[WI]?[DIST]?"
    assert pat_map["<Root>"] == "<V>?(<C>+<V>)*<C>*"
    assert "<PrefixClass>" in pat_map
    assert "<Pro>" in pat_map
    assert "<AspectClass>" in pat_map
    assert "<Aspect>" in pat_map
    assert "<TenseClass>" in pat_map
    assert "<Tense>" in pat_map
    assert "<Morpheme>" in pat_map

    # Verify Inventory
    alphabet_yaml = config_dir / "Phonology/Inventory/alphabet.yaml"
    with open(alphabet_yaml, "r", encoding="utf-8") as f:
        inv_data = yaml.safe_load(f)
    inv_map = {node["ref"]: node.get("tags", []) for node in inv_data["data"]}
    assert len(inv_map["<PrefixClass>"]) == 7
    assert len(inv_map["<Pro>"]) == 22
    assert len(inv_map["<AspectClass>"]) == 92
    assert len(inv_map["<Aspect>"]) == 5
    assert len(inv_map["<TenseClass>"]) == 2
    assert len(inv_map["<Tense>"]) == 7

