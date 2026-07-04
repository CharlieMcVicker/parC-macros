import os
import pytest
import shutil
import tempfile
import yaml
from pathlib import Path
from parc_macros import generate_markers_main, validate_yaml_file

def test_generation_exact_match():
    # We will use the test.csv which has features for a_stem, e_stem, and i_stem,
    # generate the FeatureMarkers yaml files, and check that they match the reference
    # files in spanish-colang/Exponence/FeatureMarkers/ exactly (modulo formatting, but let's parse and check semantic/bit-by-bit equivalence).
    
    csv_path = Path(__file__).parent.parent / "test.csv"
    ref_dir = Path(__file__).parent.parent / "spanish-colang/Exponence/FeatureMarkers"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Run generation
        # We call the main method with arguments
        import sys
        orig_argv = sys.argv
        try:
            sys.argv = ["generate_markers.py", str(csv_path), str(tmpdir_path)]
            generate_markers_main()
        finally:
            sys.argv = orig_argv
            
        # Check generated files
        generated_files = list(tmpdir_path.glob("*.yaml"))
        assert len(generated_files) == 3
        
        for gen_file in generated_files:
            # Validate each generated file against schema
            assert validate_yaml_file(gen_file) is True
            
            # Compare content with reference file
            ref_file = ref_dir / gen_file.name
            assert ref_file.exists(), f"Reference file {ref_file.name} does not exist"
            
            with open(gen_file, "r", encoding="utf-8") as f:
                gen_data = yaml.safe_load(f)
                
            with open(ref_file, "r", encoding="utf-8") as f:
                ref_data = yaml.safe_load(f)
                
            # Deeply assert equality of the dictionaries
            assert gen_data == ref_data, f"Data in {gen_file.name} does not match reference"
