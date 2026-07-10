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
    base_dir = root_dir / "spanish-base"
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
                str(base_dir),
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
        gen_diph_fm = tmpdir_path / "Exponence" / "FeatureMarkers" / "verb_diphthong.yaml"
        ref_diph_fm = ref_dir / "Exponence" / "FeatureMarkers" / "verb_diphthong.yaml"
        assert gen_diph_fm.exists()
        assert ref_diph_fm.exists()
        assert validate_yaml_file(gen_diph_fm) is True

        with open(gen_diph_fm, "r", encoding="utf-8") as f:
            gen_diph_fm_data = yaml.safe_load(f)
        with open(ref_diph_fm, "r", encoding="utf-8") as f:
            ref_diph_fm_data = yaml.safe_load(f)
        assert gen_diph_fm_data == ref_diph_fm_data

        gen_diph_para = tmpdir_path / "Morphotactics" / "Paradigm" / "verb_diphthong_present.yaml"
        ref_diph_para = ref_dir / "Morphotactics" / "Paradigm" / "verb_diphthong_present.yaml"
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
        assert gen_wl_data == ref_wl_data, "Generated wordlist verb.csv content does not match reference"



def test_generation_cherokee():
    root_dir = Path(__file__).parent.parent
    config_dir = root_dir / "chr-config"
    base_dir = root_dir / "chr-base"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Run generation via main function
        import sys
        orig_argv = sys.argv
        try:
            sys.argv = [
                "generate_markers.py",
                str(config_dir),
                str(base_dir),
                str(tmpdir_path),
            ]
            generate_markers_main()
        finally:
            sys.argv = orig_argv

        # Check generated ContingentFeatureMarkers files
        fm_names = ["verb_aspect_contingent.yaml", "verb_person_number_contingent.yaml"]
        for name in fm_names:
            gen_file = tmpdir_path / "Exponence" / "ContingentFeatureMarkers" / name
            assert gen_file.exists(), f"Generated ContingentFeatureMarkers file {name} does not exist"
            assert validate_yaml_file(gen_file) is True

        # Check generated Paradigm files
        para_names = ["verb.yaml"]
        for name in para_names:
            gen_file = tmpdir_path / "Morphotactics" / "Paradigm" / name
            assert gen_file.exists(), f"Generated Paradigm file {name} does not exist"
            assert validate_yaml_file(gen_file) is True

        # Check updated FeatureDefinitions
        gen_fd = tmpdir_path / "Exponence" / "FeatureDefinitions" / "verb_features.yaml"
        assert gen_fd.exists()
        assert validate_yaml_file(gen_fd) is True

        with open(gen_fd, "r", encoding="utf-8") as f:
            gen_fd_data = yaml.safe_load(f)

        assert "aspect_class" in gen_fd_data["features"]
        assert "prefix_class" in gen_fd_data["features"]
        assert set(gen_fd_data["features"]["aspect_class"]) == {"ha-hi-s", "eh-vk"}
        assert set(gen_fd_data["features"]["prefix_class"]) == {"a_stem", "cons_stem"}

        # Check generated Lexicon/PartOfSpeech/verb.yaml
        gen_pos = tmpdir_path / "Lexicon" / "PartOfSpeech" / "verb.yaml"
        assert gen_pos.exists()
        assert validate_yaml_file(gen_pos) is True

        with open(gen_pos, "r", encoding="utf-8") as f:
            gen_pos_data = yaml.safe_load(f)
        assert set(gen_pos_data["lexical_features"]) == {"prefix_class", "aspect_class"}

        # Check that wordlists were copied correctly
        gen_wl = tmpdir_path / "Lexicon" / "Wordlists" / "verb.csv"
        assert gen_wl.exists(), "Generated Cherokee wordlist verb.csv does not exist"
        with open(gen_wl, "r", encoding="utf-8") as f:
            gen_wl_data = f.read()
        # Verify content matches what we moved to config/wordlists/verb.csv
        with open(config_dir / "wordlists" / "verb.csv", "r", encoding="utf-8") as f:
            expected_wl_data = f.read()
        assert gen_wl_data == expected_wl_data, "Generated Cherokee wordlist content does not match config"




