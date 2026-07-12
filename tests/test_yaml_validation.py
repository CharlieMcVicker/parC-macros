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
