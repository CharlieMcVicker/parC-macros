import os
import tempfile
import yaml
from parc_macros.generate_morpheme_replace_rules import generate_morpheme_replace_rules
from parc_macros.generate_markers import parse_csv_with_metadata, main as generate_markers_main


def test_morpheme_replace_rules_generation():
    csv_content = """# kind: morpheme_replace
# morpheme_tag: [Pro]
# stage: pronominal
# feature: pronominal
# class_feature: prefix_class
paradigm,1sg.A,Edl.A,Epl.A
a_stem,k,ost,ots
v_stem,k,ost,ots
e_stem,,ost,ots
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config")
        os.makedirs(config_path, exist_ok=True)
        csv_file_path = os.path.join(config_path, "verb-pronominal.csv")
        with open(csv_file_path, "w", encoding="utf-8") as f:
            f.write(csv_content)

        # Generate replace rules
        output_dir = os.path.join(tmpdir, "output")
        generate_morpheme_replace_rules(config_path, output_dir)

        # Check rules file exists and has correct entries
        rules_path = os.path.join(output_dir, "Phonology", "Rules", "pro_replace.yaml")
        assert os.path.exists(rules_path)

        with open(rules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["kind"] == "Rules"
        rules = data["rules"]
        # Expected unique values: '', 'k', 'ost', 'ots'
        expected_rules = {
            "pro_empty": [["[Pro]", ""]],
            "pro_k": [["[Pro]", "k"]],
            "pro_ost": [["[Pro]", "ost"]],
            "pro_ots": [["[Pro]", "ots"]]
        }
        
        for rule in rules:
            name = rule["name"]
            assert name in expected_rules
            assert rule["string_map"] == expected_rules[name]

        # Verify generate_markers generates correct kind: rule referencing the replacement rule
        # We also need a dummy verb.yaml in the config directory to run generate_markers_main
        verb_yaml_content = """stages:
  - pronominal
features:
  pronominal:
    - 1sg.A
    - Edl.A
    - Epl.A
lexical_features:
  - prefix_class
paradigm:
  generate_contingent_markers: true
"""
        with open(os.path.join(config_path, "verb.yaml"), "w", encoding="utf-8") as f:
            f.write(verb_yaml_content)

        import sys
        orig_argv = sys.argv
        try:
            sys.argv = ["generate_markers.py", config_path, output_dir]
            generate_markers_main()
        finally:
            sys.argv = orig_argv

        # Check generated contingent markers YAML file
        marker_file = os.path.join(output_dir, "Exponence", "ContingentFeatureMarkers", "verb_pronominal_prefix_class_contingent.yaml")
        assert os.path.exists(marker_file)

        with open(marker_file, "r", encoding="utf-8") as f:
            marker_data = yaml.safe_load(f)

        assert marker_data["kind"] == "ContingentFeatureMarkers"
        # Verify e_stem 1sg.A is mapped to $pro_empty rule
        a_stem_1sg = marker_data["markers"]["a_stem"]["1sg.A"]
        assert len(a_stem_1sg) == 1
        assert a_stem_1sg[0]["kind"] == "rule"
        assert a_stem_1sg[0]["value"] == "$pro_k"

        e_stem_1sg = marker_data["markers"]["e_stem"]["1sg.A"]
        assert len(e_stem_1sg) == 1
        assert e_stem_1sg[0]["kind"] == "rule"
        assert e_stem_1sg[0]["value"] == "$pro_empty"
