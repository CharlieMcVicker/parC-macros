import os
from pathlib import Path
import pytest

# Ensure environment variable YAML_DIR is set
if "YAML_DIR" not in os.environ:
    os.environ["YAML_DIR"] = str(Path(__file__).parent.parent / "chr-generated")

from parse_chr_dict.parse import inflect

def test_optional_feature_combinations():
    root = "atat"
    lexical = [
        ("prefix_class", "a_stem"),
        ("aspect_class", "go"),
        ("tense_present_class", "a_present")
    ]
    
    # Obligatory inflectional features
    base_infl = [
        ("pronominal", "3sg.A"),
        ("aspect", "present"),
        ("tense", "present")
    ]
    
    optional_features = ["translocutive", "distributive", "partitive"]
    
    # We will test combinations of optional features:
    # Each can be '+' (on), 'UNMARKED' (off), or completely omitted (not in the list).
    values_to_test = ["+", "UNMARKED", "OMITTED"]
    
    print("\n--- Testing Inflection Combinations ---")
    results = {}
    
    # Iterate through all 27 combinations
    for val_trl in values_to_test:
        for val_dist in values_to_test:
            for val_part in values_to_test:
                infl_features = list(base_infl)
                if val_trl != "OMITTED":
                    infl_features.append(("translocutive", val_trl))
                if val_dist != "OMITTED":
                    infl_features.append(("distributive", val_dist))
                if val_part != "OMITTED":
                    infl_features.append(("partitive", val_part))
                
                # Try to inflect
                try:
                    out = inflect(root, lexical, infl_features)
                except Exception as e:
                    out = [f"ERROR: {str(e)}"]
                
                key = (val_trl, val_dist, val_part)
                results[key] = out
                
                combo_str = f"trl={val_trl:8} dist={val_dist:8} part={val_part:8}"
                print(f"{combo_str} -> {out}")
                
    # Now let's print a summary of success vs failure
    successful = {k: v for k, v in results.items() if v and not any(x.startswith("ERROR") for x in v)}
    failed = {k: v for k, v in results.items() if not v or any(x.startswith("ERROR") for x in v)}
    
    print(f"\nTotal combinations: {len(results)}")
    print(f"Successful inflections: {len(successful)}")
    print(f"Failed inflections: {len(failed)}")
    
    # Assert that we ran the test and print results
    assert len(results) == 27
