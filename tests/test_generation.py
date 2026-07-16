import os
import pytest
import shutil
import tempfile
import yaml
from pathlib import Path
from parc_macros import generate_markers_main, validate_yaml_file


def test_generation_exact_match():
    # Paths to source files and directories
    root_dir = Path(__file__).parent.parent
    csv_path = root_dir / "spanish-config/verb-suffix.csv"
    ref_dir = root_dir / "spanish-reference"

    class_feature = "conjugation_class"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Run generation via the refactored main function
        import sys

        orig_argv = sys.argv
        try:
            sys.argv = [
                "generate_markers.py",
                str(csv_path.parent),
                str(tmpdir_path),
            ]
            generate_markers_main()
        finally:
            sys.argv = orig_argv

        # 1. Check generated FeatureMarkers files
        fm_names = ["verb_a_stem.yaml", "verb_e_stem.yaml", "verb_i_stem.yaml"]
        for name in fm_names:
            gen_file = tmpdir_path / "Exponence" / "FeatureMarkers" / name
            ref_file = ref_dir / "Exponence" / "FeatureMarkers" / name

            assert (
                gen_file.exists()
            ), f"Generated FeatureMarkers file {name} does not exist"
            assert (
                ref_file.exists()
            ), f"Reference FeatureMarkers file {name} does not exist"
            assert validate_yaml_file(gen_file) is True

            with open(gen_file, "r", encoding="utf-8") as f:
                gen_data = yaml.safe_load(f)
            with open(ref_file, "r", encoding="utf-8") as f:
                ref_data = yaml.safe_load(f)

            assert (
                gen_data == ref_data
            ), f"Data in FeatureMarkers {name} does not match reference"

        # 2. Check generated Paradigm files
        para_names = [
            "verb_a_stem_present.yaml",
            "verb_e_stem_present.yaml",
            "verb_i_stem_present.yaml",
        ]
        for name in para_names:
            gen_file = tmpdir_path / "Morphotactics" / "Paradigm" / name
            ref_file = ref_dir / "Morphotactics" / "Paradigm" / name

            assert gen_file.exists(), f"Generated Paradigm file {name} does not exist"
            assert ref_file.exists(), f"Reference Paradigm file {name} does not exist"
            assert validate_yaml_file(gen_file) is True

            with open(gen_file, "r", encoding="utf-8") as f:
                gen_data = yaml.safe_load(f)
            with open(ref_file, "r", encoding="utf-8") as f:
                ref_data = yaml.safe_load(f)

            assert (
                gen_data == ref_data
            ), f"Data in Paradigm {name} does not match reference"

        # 3. Check updated FeatureDefinitions
        gen_fd = tmpdir_path / "Exponence" / "FeatureDefinitions" / "verb_features.yaml"
        ref_fd = ref_dir / "Exponence" / "FeatureDefinitions" / "verb_features.yaml"

        assert gen_fd.exists()
        assert ref_fd.exists()
        assert validate_yaml_file(gen_fd) is True

        with open(gen_fd, "r", encoding="utf-8") as f:
            gen_fd_data = yaml.safe_load(f)
        with open(ref_fd, "r", encoding="utf-8") as f:
            ref_fd_data = yaml.safe_load(f)

        # Compare class_feature list as sets since ordering does not affect correctness
        gen_cc = gen_fd_data["features"].get(class_feature, [])
        ref_cc = ref_fd_data["features"].get(class_feature, [])
        assert set(gen_cc) == set(ref_cc), f"{class_feature} values do not match"

        del gen_fd_data["features"][class_feature]
        del ref_fd_data["features"][class_feature]
        assert (
            gen_fd_data == ref_fd_data
        ), "Data in verb_features.yaml does not match reference"

        # 4. Check generated diphthong FeatureMarkers and Paradigm
        gen_diph_fm = (
            tmpdir_path / "Exponence" / "FeatureMarkers" / "verb_diphthong.yaml"
        )
        ref_diph_fm = ref_dir / "Exponence" / "FeatureMarkers" / "verb_diphthong.yaml"
        assert gen_diph_fm.exists()
        assert ref_diph_fm.exists()
        assert validate_yaml_file(gen_diph_fm) is True

        with open(gen_diph_fm, "r", encoding="utf-8") as f:
            gen_diph_fm_data = yaml.safe_load(f)
        with open(ref_diph_fm, "r", encoding="utf-8") as f:
            ref_diph_fm_data = yaml.safe_load(f)
        assert gen_diph_fm_data == ref_diph_fm_data

        gen_diph_para = (
            tmpdir_path / "Morphotactics" / "Paradigm" / "verb_diphthong_present.yaml"
        )
        ref_diph_para = (
            ref_dir / "Morphotactics" / "Paradigm" / "verb_diphthong_present.yaml"
        )
        assert gen_diph_para.exists()
        assert ref_diph_para.exists()
        assert validate_yaml_file(gen_diph_para) is True

        with open(gen_diph_para, "r", encoding="utf-8") as f:
            gen_diph_para_data = yaml.safe_load(f)
        with open(ref_diph_para, "r", encoding="utf-8") as f:
            ref_diph_para_data = yaml.safe_load(f)
        assert gen_diph_para_data == ref_diph_para_data

        # 5. Check generated Lexicon/PartOfSpeech/verb.yaml
        gen_pos = tmpdir_path / "Lexicon" / "PartOfSpeech" / "verb.yaml"
        ref_pos = ref_dir / "Lexicon" / "PartOfSpeech" / "verb.yaml"
        assert gen_pos.exists()
        assert ref_pos.exists()
        assert validate_yaml_file(gen_pos) is True

        with open(gen_pos, "r", encoding="utf-8") as f:
            gen_pos_data = yaml.safe_load(f)
        with open(ref_pos, "r", encoding="utf-8") as f:
            ref_pos_data = yaml.safe_load(f)
        assert gen_pos_data == ref_pos_data

        # 6. Check that wordlists were copied correctly
        gen_wl = tmpdir_path / "Lexicon" / "Wordlists" / "verb.csv"
        ref_wl = ref_dir / "Lexicon" / "Wordlists" / "verb.csv"
        assert gen_wl.exists(), "Generated wordlist verb.csv does not exist"
        assert ref_wl.exists(), "Reference wordlist verb.csv does not exist"
        with open(gen_wl, "r", encoding="utf-8") as f:
            gen_wl_data = f.read()
        with open(ref_wl, "r", encoding="utf-8") as f:
            ref_wl_data = f.read()
        assert (
            gen_wl_data == ref_wl_data
        ), "Generated wordlist verb.csv content does not match reference"

        # 7. Check that Phonology was copied correctly
        gen_phon = tmpdir_path / "Phonology"
        ref_phon = ref_dir / "Phonology"
        assert gen_phon.exists(), "Generated Phonology directory does not exist"
        assert ref_phon.exists(), "Reference Phonology directory does not exist"
        for root, dirs, files in os.walk(ref_phon):
            for file in files:
                rel_path = Path(root).relative_to(ref_phon) / file
                gen_file = gen_phon / rel_path
                ref_file = ref_phon / rel_path
                assert (
                    gen_file.exists()
                ), f"Generated Phonology file {rel_path} does not exist"
                with open(gen_file, "r", encoding="utf-8") as f:
                    gen_content = f.read()
                with open(ref_file, "r", encoding="utf-8") as f:
                    ref_content = f.read()
                assert (
                    gen_content == ref_content
                ), f"Content of Phonology file {rel_path} does not match reference"


def test_generation_with_feature_acceptors():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "output"
        os.makedirs(config_dir)

        # 1. Create a minimal verb.yaml
        verb_yaml_content = {
            "kind": "PartOfSpeech",
            "name": "verb",
            "features": {"tense": ["present", "past"], "mood": ["indicative"]},
            "paradigm": {
                "feature_markers_keys": ["tense", "mood"],
                "filename_suffix_keys": ["tense", "mood"],
            },
        }
        with open(config_dir / "verb.yaml", "w", encoding="utf-8") as f:
            yaml.dump(verb_yaml_content, f)

        # 2. Create a minimal CSV file for paradigm definition
        csv_content = """# class_feature: prefix_class
# kind: prefix
# stage: prefix
# feature: tense
# part_of_speech: $verb
# tense: present
# mood: indicative
prefix_class,present,past
e_stem,e,ed
normal,n,nd
"""
        with open(config_dir / "verb-present.csv", "w", encoding="utf-8") as f:
            f.write(csv_content)

        # 3. Create the feature_acceptors subfolder and CSV
        fa_dir = config_dir / "feature_acceptors"
        os.makedirs(fa_dir)

        fa_csv_content = """# feature: prefix_class
# part_of_speech: $verb
prefix_class,acceptor
e_stem,e<Phone>*
"""
        with open(fa_dir / "prefix_class.csv", "w", encoding="utf-8") as f:
            f.write(fa_csv_content)

        # Run generation
        import sys

        orig_argv = sys.argv
        try:
            sys.argv = [
                "generate_markers.py",
                str(config_dir),
                str(output_dir),
            ]
            generate_markers_main()
        finally:
            sys.argv = orig_argv

        # Check updated FeatureDefinitions
        gen_fd = output_dir / "Exponence" / "FeatureDefinitions" / "verb_features.yaml"
        assert gen_fd.exists()
        assert validate_yaml_file(gen_fd) is True

        with open(gen_fd, "r", encoding="utf-8") as f:
            gen_fd_data = yaml.safe_load(f)

        assert "prefix_class" in gen_fd_data["features"]
        prefix_class_vals = gen_fd_data["features"]["prefix_class"]

        # Should contain "normal" (as string) and {"name": "e_stem", "acceptor": "e<Phone>*"} (as dict)
        assert len(prefix_class_vals) == 2
        # Verify ordering is sorted by name
        assert prefix_class_vals[0] == {"name": "e_stem", "acceptor": "e<Phone>*"}
        assert prefix_class_vals[1] == "normal"


def test_generation_with_optional_features():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "output"
        os.makedirs(config_dir)

        # 1. Create a verb.yaml with optional features
        verb_yaml_content = {
            "kind": "PartOfSpeech",
            "name": "verb",
            "features": {
                "tense": ["present", "past"],
                "mood": ["indicative"],
                "translocutive": {
                    "values": ["+"],
                    "optional": True
                }
            },
            "paradigm": {
                "generate_contingent_markers": True
            },
        }
        with open(config_dir / "verb.yaml", "w", encoding="utf-8") as f:
            yaml.dump(verb_yaml_content, f)

        # 2. Create a minimal CSV file for standard optional features (non-contingent)
        csv_content = """# kind: prefix
# stage: prefix
# feature: translocutive
# part_of_speech: $verb
# translocutive: +
translocutive,marker
+,w
"""
        with open(config_dir / "verb-translocutive.csv", "w", encoding="utf-8") as f:
            f.write(csv_content)

        # Run generation
        import sys
        orig_argv = sys.argv
        try:
            sys.argv = [
                "generate_markers.py",
                str(config_dir),
                str(output_dir),
            ]
            generate_markers_main()
        finally:
            sys.argv = orig_argv

        # Check FeatureDefinitions: translocutive values should have + and UNMARKED
        gen_fd = output_dir / "Exponence" / "FeatureDefinitions" / "verb_features.yaml"
        assert gen_fd.exists()
        assert validate_yaml_file(gen_fd) is True

        with open(gen_fd, "r", encoding="utf-8") as f:
            gen_fd_data = yaml.safe_load(f)

        assert "translocutive" in gen_fd_data["features"]
        translocutive_def = gen_fd_data["features"]["translocutive"]
        assert isinstance(translocutive_def, list)
        assert "UNMARKED" in translocutive_def
        assert "+" in translocutive_def

        # Check standard FeatureMarkers file generated for translocutive
        gen_fm = output_dir / "Exponence" / "FeatureMarkers" / "verb_translocutive.yaml"
        assert gen_fm.exists()
        assert validate_yaml_file(gen_fm) is True

        with open(gen_fm, "r", encoding="utf-8") as f:
            gen_fm_data = yaml.safe_load(f)

        assert "UNMARKED" in gen_fm_data["markers"]
        assert gen_fm_data["markers"]["UNMARKED"] == []


def test_generation_with_contingent_optional_features():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "output"
        os.makedirs(config_dir)

        # 1. Create a verb.yaml with optional features and generate_contingent_markers: true
        verb_yaml_content = {
            "kind": "PartOfSpeech",
            "name": "verb",
            "features": {
                "tense": ["present", "past"],
                "distributive": {
                    "values": ["+"],
                    "optional": True
                }
            },
            "paradigm": {
                "generate_contingent_markers": True
            },
        }
        with open(config_dir / "verb.yaml", "w", encoding="utf-8") as f:
            yaml.dump(verb_yaml_content, f)

        # 2. Create a minimal CSV file for contingent optional feature
        csv_content = """# class_feature: tense
# kind: rule
# stage: distributive
# feature: distributive
# part_of_speech: $verb
# tense: present
# distributive: +
tense,distributive
present,$insert_DIST1
"""
        with open(config_dir / "verb-distributive.csv", "w", encoding="utf-8") as f:
            f.write(csv_content)

        # Run generation
        import sys
        orig_argv = sys.argv
        try:
            sys.argv = [
                "generate_markers.py",
                str(config_dir),
                str(output_dir),
            ]
            generate_markers_main()
        finally:
            sys.argv = orig_argv

        # Check ContingentFeatureMarkers
        gen_cfm = output_dir / "Exponence" / "ContingentFeatureMarkers" / "verb_distributive_tense_contingent.yaml"
        assert gen_cfm.exists()
        assert validate_yaml_file(gen_cfm) is True

        with open(gen_cfm, "r", encoding="utf-8") as f:
            gen_cfm_data = yaml.safe_load(f)

        # Present class value should map distributive values + and UNMARKED
        assert "present" in gen_cfm_data["markers"]
        assert "UNMARKED" in gen_cfm_data["markers"]["present"]
        assert gen_cfm_data["markers"]["present"]["UNMARKED"] == []


