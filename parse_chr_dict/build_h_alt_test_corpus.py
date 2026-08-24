from __future__ import annotations
import csv
import json
import re
from pathlib import Path
from typing import Dict, List

from parse_chr_dict.h_alternation import (
    _drop_first_h,
    _first_h_to_glottal,
    _drop_h_in_deaffricated_lateral,
    prevent_C_glottal_cluster,
    _is_compatible_with_vowel_restoration,
    grades_are_compatible,
)


def clean_root_tags(root_str: str) -> str:
    """Removes bracketed meta/feature tags e.g. [Pro] and [Aspect][Tense]."""
    return re.sub(r"\[.*?\]", "", root_str)


def classify_alternation_type(h_stem: str, glottal_stem: str) -> str:
    """Classifies the primary phonological alternation pathway between h_stem and glottal_stem."""
    if _drop_h_in_deaffricated_lateral(h_stem) == glottal_stem:
        return "lateral_deaffrication"
    if _drop_first_h(h_stem) == glottal_stem:
        return "drop_h"
    if prevent_C_glottal_cluster(_first_h_to_glottal(h_stem)) == glottal_stem:
        return "h_to_glottal"
    for alt in [
        _drop_first_h(h_stem),
        prevent_C_glottal_cluster(_first_h_to_glottal(h_stem)),
        _drop_h_in_deaffricated_lateral(h_stem),
        h_stem,
    ]:
        if _is_compatible_with_vowel_restoration(glottal_stem, alt):
            return "syncopation_restoration"
    return "other_complex"


def extract_h_alternation_corpus(
    roots_csv_path: str = "roots.csv",
    output_csv_path: str = "tests/data/h_alternation_test_corpus.csv",
    output_json_path: str = "tests/data/h_alternation_test_corpus.json",
) -> List[Dict[str, str]]:
    """Extracts all reconstructed Cherokee verb entries exhibiting H-alternation."""
    entries: List[Dict[str, str]] = []
    seen = set()

    with open(roots_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            h_root = row.get("h_root", "").strip()
            g_root = row.get("glottal_root", "").strip()
            if h_root and g_root and h_root != g_root:
                h_stem = clean_root_tags(h_root)
                g_stem = clean_root_tags(g_root)
                key = (row.get("entry_no", ""), h_stem, g_stem)
                if key not in seen:
                    seen.add(key)
                    alt_type = classify_alternation_type(h_stem, g_stem)
                    entry_dict = {
                        "entry_no": row.get("entry_no", ""),
                        "definition": row.get("definition", ""),
                        "present_3sg": row.get("present", ""),
                        "present_1sg": row.get("present_1sg", ""),
                        "imperfective": row.get("imperfective", ""),
                        "perfective": row.get("perfective", ""),
                        "imperative": row.get("imperative", ""),
                        "infinitive": row.get("infinitive", ""),
                        "h_root": h_root,
                        "glottal_root": g_root,
                        "h_stem": h_stem,
                        "glottal_stem": g_stem,
                        "alternation_type": alt_type,
                        "aspect_class": row.get("aspect_class", ""),
                        "prefix_class": row.get("prefix_class", ""),
                    }
                    entries.append(entry_dict)

    # Sort entries by integer entry_no where possible
    def sort_key(item: Dict[str, str]):
        try:
            return (int(item["entry_no"]), item["h_stem"])
        except ValueError:
            return (999999, item["h_stem"])

    entries.sort(key=sort_key)

    # Write CSV output
    fieldnames = [
        "entry_no",
        "definition",
        "present_3sg",
        "present_1sg",
        "imperfective",
        "perfective",
        "imperative",
        "infinitive",
        "h_root",
        "glottal_root",
        "h_stem",
        "glottal_stem",
        "alternation_type",
        "aspect_class",
        "prefix_class",
    ]
    Path(output_csv_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

    # Write JSON output
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    return entries


if __name__ == "__main__":
    extracted = extract_h_alternation_corpus()
    print(f"Successfully generated {len(extracted)} H-alternating test corpus entries.")
