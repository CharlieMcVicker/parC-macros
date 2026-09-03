"""
Programmatic generator and configuration utility for in-place morpheme tags.

Extracts morpheme tags, lexical classes, and phonological dropping triggers
directly from CSV data files and generates the corresponding Inventory,
Patterns, Rules, and Verb configuration files.
"""

from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path
from typing import Any
import yaml


def _parse_csv_matrix(path: Path) -> tuple[list[str], list[str]]:
    """
    Parses a CSV matrix (skipping comments) and returns (row_classes, col_features).
    """
    with open(path, "r", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    if not rows:
        raise ValueError(f"Empty CSV matrix: {path}")
    header = rows[0]
    classes = [r[0].strip() for r in rows[1:] if r and r[0].strip()]
    features = [h.strip() for h in header[1:] if h.strip()]
    return classes, features


def _parse_rule_triggers(path: Path) -> list[tuple[str, str]]:
    """
    Parses a rule trigger CSV file and returns list of (class_val, feature_val) where cell == 'Y'.
    """
    with open(path, "r", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    if not rows:
        return []
    header = [h.strip() for h in rows[0]]
    triggers: list[tuple[str, str]] = []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        cls = r[0].strip()
        for idx, feat in enumerate(header[1:], 1):
            if idx < len(r) and r[idx].strip() == "Y":
                triggers.append((cls, feat))
    return triggers


def extract_data_from_config(config_dir: Path) -> dict[str, Any]:
    """
    Extracts all classes, inflectional features, and rule triggers from config CSVs.
    """
    prefix_classes, pronominals = _parse_csv_matrix(config_dir / "verb-pronominal.csv")
    aspect_classes, aspects = _parse_csv_matrix(config_dir / "verb-aspect.csv")
    tense_classes, tenses = _parse_csv_matrix(config_dir / "verb-tense.csv")

    drop_final_triggers = _parse_rule_triggers(config_dir / "verb-aspect-drop-final.csv")
    drop_final_two_triggers = _parse_rule_triggers(config_dir / "verb-aspect-drop-final-two.csv")
    drop_first_a_triggers = _parse_rule_triggers(config_dir / "verb-pronominal-drop-first-a.csv")
    drop_first_v_triggers = _parse_rule_triggers(config_dir / "verb-pronominal-drop-first-v.csv")

    return {
        "prefix_classes": prefix_classes,
        "pronominals": pronominals,
        "aspect_classes": aspect_classes,
        "aspects": aspects,
        "tense_classes": tense_classes,
        "tenses": tenses,
        "drop_final_triggers": drop_final_triggers,
        "drop_final_two_triggers": drop_final_two_triggers,
        "drop_first_a_triggers": drop_first_a_triggers,
        "drop_first_v_triggers": drop_first_v_triggers,
    }


def generate_alphabet_yaml(
    base_alphabet_path: Path,
    output_alphabet_path: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates Inventory alphabet.yaml with in-place tags derived from CSVs.
    """
    with open(base_alphabet_path, "r", encoding="utf-8") as f:
        inv = yaml.safe_load(f)

    # Filter out old single-token Pro, Aspect, Tense nodes
    new_data: list[dict[str, Any]] = []
    for item in inv.get("data", []):
        ref = item.get("ref")
        if ref in ("<Pro>", "<Aspect>", "<Tense>"):
            continue
        new_data.append(item)

    # In-place tags
    prefix_class_tags = [f"[PrefixClass={c}]" for c in data["prefix_classes"]]
    pro_tags = [f"[Pro={p}]" for p in data["pronominals"]]
    aspect_class_tags = [f"[AspectClass={c}]" for c in data["aspect_classes"]]
    aspect_tags = [f"[Aspect={a}]" for a in data["aspects"]]
    tense_class_tags = [f"[TenseClass={c}]" for c in data["tense_classes"]]
    tense_tags = [f"[Tense={t}]" for t in data["tenses"]]

    new_data.append({
        "name": "PrefixClass",
        "ref": "<PrefixClass>",
        "tags": prefix_class_tags,
    })
    new_data.append({
        "name": "Pro",
        "ref": "<Pro>",
        "tags": pro_tags,
    })
    new_data.append({
        "name": "AspectClass",
        "ref": "<AspectClass>",
        "tags": aspect_class_tags,
    })
    new_data.append({
        "name": "Aspect",
        "ref": "<Aspect>",
        "tags": aspect_tags,
    })
    new_data.append({
        "name": "TenseClass",
        "ref": "<TenseClass>",
        "tags": tense_class_tags,
    })
    new_data.append({
        "name": "Tense",
        "ref": "<Tense>",
        "tags": tense_tags,
    })
    # Preserve legacy tags
    new_data.append({
        "name": "Legacy Tags",
        "ref": "<LegacyTags>",
        "tags": ["[Pro]", "[Aspect]", "[Tense]"],
    })

    inv["data"] = new_data
    with open(output_alphabet_path, "w", encoding="utf-8") as f:
        yaml.dump(inv, f, sort_keys=False, default_flow_style=False)


def generate_phoneme_groups_yaml(
    base_groups_path: Path,
    output_groups_path: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates Patterns phoneme_groups.yaml with in-place pattern definitions.
    """
    with open(base_groups_path, "r", encoding="utf-8") as f:
        pats_yaml = yaml.safe_load(f)

    # Base patterns to retain
    retained_patterns: list[dict[str, Any]] = []
    for pat in pats_yaml.get("patterns", []):
        ref = pat.get("ref")
        # Keep Consonants (<C>), H_ALT, NotLar, SonH, HTarget
        if ref in ("<C>", "<H_ALT>", "<NotLar>", "<SonH>", "<HTarget>"):
            retained_patterns.append(pat)

    # Define new patterns
    prefix_class_pat = "|".join(f"[PrefixClass={c}]" for c in data["prefix_classes"])
    pro_pat = "|".join(f"[Pro={p}]" for p in data["pronominals"])
    aspect_class_pat = "|".join(f"[AspectClass={c}]" for c in data["aspect_classes"])
    aspect_pat = "|".join(f"[Aspect={a}]" for a in data["aspects"])
    tense_class_pat = "|".join(f"[TenseClass={c}]" for c in data["tense_classes"])
    tense_pat = "|".join(f"[Tense={t}]" for t in data["tenses"])

    new_patterns: list[dict[str, Any]] = [
        retained_patterns[0],  # Consonants (<C>)
        {
            "name": "PrepronominalPrefixes",
            "ref": "<PrepronominalPrefixes>",
            "pattern": "[WI]?[DIST]?",
        },
        {
            "name": "Root",
            "ref": "<Root>",
            "pattern": "<V>?(<C>+<V>)*<C>*",
        },
        {
            "name": "PrefixClass",
            "ref": "<PrefixClass>",
            "pattern": prefix_class_pat,
        },
        {
            "name": "Pro",
            "ref": "<Pro>",
            "pattern": pro_pat,
        },
        {
            "name": "AspectClass",
            "ref": "<AspectClass>",
            "pattern": aspect_class_pat,
        },
        {
            "name": "Aspect",
            "ref": "<Aspect>",
            "pattern": aspect_pat,
        },
        {
            "name": "TenseClass",
            "ref": "<TenseClass>",
            "pattern": tense_class_pat,
        },
        {
            "name": "Tense",
            "ref": "<Tense>",
            "pattern": tense_pat,
        },
        {
            "name": "Morpheme",
            "ref": "<Morpheme>",
            "pattern": "<PrefixClass>|<Pro>|<AspectClass>|<Aspect>|<TenseClass>|<Tense>|<PPP>|<H_ALT>|[WI]|[DIST]",
        },
    ]
    # Append the remaining retained patterns (<H_ALT>, <NotLar>, <SonH>, <HTarget>)
    new_patterns.extend(retained_patterns[1:])

    pats_yaml["patterns"] = new_patterns
    with open(output_groups_path, "w", encoding="utf-8") as f:
        yaml.dump(pats_yaml, f, sort_keys=False, default_flow_style=False)


def update_verb_yaml(verb_yaml_path: Path) -> None:
    """
    Updates open_root_template in verb.yaml to the in-place template
    while preserving comments and whitespace.
    """
    with open(verb_yaml_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_template = "<PrepronominalPrefixes><PrefixClass><Pro><H_alt><Root><AspectClass><Aspect><TenseClass><Tense>"
    # Pattern to match open_root_template: ...
    subbed = re.sub(
        r"open_root_template:\s*[\"'].*?[\"'].*",
        f'open_root_template: "{new_template}"',
        content,
    )
    if subbed == content:
        # Fallback if no quotes
        subbed = re.sub(
            r"open_root_template:.*",
            f'open_root_template: "{new_template}"',
            content,
        )

    with open(verb_yaml_path, "w", encoding="utf-8") as f:
        f.write(subbed)


def generate_drop_root_final_yaml(
    output_path: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates drop_root_final.yaml using local trigger contexts derived from CSVs.
    Note: delete_temp_marker is defined in drop_stem_initial_vowel.yaml.
    """
    # Build right context for drop_final (1 phone)
    drop_final_branches = [
        f"[AspectClass={cls}][Aspect={feat}]"
        for cls, feat in data["drop_final_triggers"]
    ]
    drop_final_rc = "|".join(drop_final_branches)

    # Build right context for drop_final_two (2 phones)
    drop_final_two_branches = [
        f"[AspectClass={cls}][Aspect={feat}]"
        for cls, feat in data["drop_final_two_triggers"]
    ]
    drop_final_two_rc = "|".join(drop_final_two_branches)

    rules = {
        "kind": "Rules",
        "rules": [
            {
                "name": "mark_final",
                "description": "mark the final phone for deletion based on in-place aspect triggers",
                "string_map": [["<Phone>", "[TEMP]"]],
                "right_context": drop_final_rc,
            },
            {
                "name": "mark_final_two",
                "description": "mark the final two phones for deletion based on in-place aspect triggers",
                "string_map": [["<Phone><Phone>?", "[TEMP]"]],
                "right_context": drop_final_two_rc,
            },
            {
                "name": "drop_final",
                "description": "drop final phone",
                "rule_sequence": [
                    "$mark_final",
                    "$delete_temp_marker",
                ],
            },
            {
                "name": "drop_final_two",
                "description": "drop final two phones",
                "rule_sequence": [
                    "$mark_final_two",
                    "$delete_temp_marker",
                ],
            },
            {
                "name": "drop_root_final",
                "description": "drop final root phone(s) conditioned on in-place aspect class and aspect tags",
                "rule_sequence": [
                    "$drop_final_two",
                    "$drop_final",
                ],
            },
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(rules, f, sort_keys=False, default_flow_style=False)


def generate_drop_stem_initial_vowel_yaml(
    output_path: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates drop_stem_initial_vowel.yaml using local trigger contexts derived from CSVs.
    """
    # Group triggers by prefix class for initial a
    a_branches = [
        f"[PrefixClass={cls}][Pro={pro}]<H_ALT>?"
        for cls, pro in data["drop_first_a_triggers"]
    ]
    drop_a_lc = "|".join(a_branches)

    # Triggers for initial v
    v_branches = [
        f"[PrefixClass={cls}][Pro={pro}]<H_ALT>?"
        for cls, pro in data["drop_first_v_triggers"]
    ]
    drop_v_lc = "|".join(v_branches)

    rules = {
        "kind": "Rules",
        "rules": [
            {
                "name": "mark_stem_initial_a",
                "description": "mark the first a with [TEMP] at start of stem",
                "string_map": [["a", "[TEMP]"]],
                "left_context": drop_a_lc,
            },
            {
                "name": "mark_stem_initial_v",
                "description": "mark the first v with [TEMP] at start of stem",
                "string_map": [["v", "[TEMP]"]],
                "left_context": drop_v_lc,
            },
            {
                "name": "delete_temp_marker",
                "description": "delete the temporary marker [TEMP]",
                "input_pattern": "[TEMP]",
                "output_pattern": "",
            },
            {
                "name": "drop_stem_initial_a",
                "description": "drop only the first a at start of stem",
                "rule_sequence": [
                    "$mark_stem_initial_a",
                    "$delete_temp_marker",
                ],
            },
            {
                "name": "drop_stem_initial_v",
                "description": "drop only the first v at start of stem",
                "rule_sequence": [
                    "$mark_stem_initial_v",
                    "$delete_temp_marker",
                ],
            },
            {
                "name": "drop_stem_initial_vowel",
                "description": "drop stem initial vowel (a or v) based on pronominal triggers",
                "rule_sequence": [
                    "$drop_stem_initial_a",
                    "$drop_stem_initial_v",
                ],
            },
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(rules, f, sort_keys=False, default_flow_style=False)


def update_h_alternation_yaml(h_alt_path: Path) -> None:
    """
    Updates left_context in delete_h_none and delete_temp_tags in h_alternation.yaml
    to match the in-place <Pro> pattern.
    """
    if not h_alt_path.exists():
        return
    with open(h_alt_path, "r", encoding="utf-8") as f:
        h_alt = yaml.safe_load(f)

    for rule in h_alt.get("rules", []):
        if rule.get("name") in ("delete_h_none", "delete_temp_tags"):
            rule["left_context"] = "<Pro>|[Pro]"

    with open(h_alt_path, "w", encoding="utf-8") as f:
        yaml.dump(h_alt, f, sort_keys=False, default_flow_style=False)


def configure_inplace_config(source_dir: Path, target_dir: Path) -> None:
    """
    Copies source config to target and applies all programmatic in-place transformations.
    """
    if source_dir.resolve() != target_dir.resolve():
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)
        cache_dir = target_dir / ".cache"
        if cache_dir.exists():
            shutil.rmtree(cache_dir)

    data = extract_data_from_config(target_dir)

    # 1. Update Inventory/alphabet.yaml
    generate_alphabet_yaml(
        target_dir / "Phonology/Inventory/alphabet.yaml",
        target_dir / "Phonology/Inventory/alphabet.yaml",
        data,
    )

    # 2. Update Patterns/phoneme_groups.yaml
    generate_phoneme_groups_yaml(
        target_dir / "Phonology/Patterns/phoneme_groups.yaml",
        target_dir / "Phonology/Patterns/phoneme_groups.yaml",
        data,
    )

    # 3. Update verb.yaml
    update_verb_yaml(target_dir / "verb.yaml")

    # 4. Update drop_root_final.yaml
    generate_drop_root_final_yaml(
        target_dir / "Phonology/Rules/drop_root_final.yaml",
        data,
    )

    # 5. Update drop_stem_initial_vowel.yaml
    generate_drop_stem_initial_vowel_yaml(
        target_dir / "Phonology/Rules/drop_stem_initial_vowel.yaml",
        data,
    )

    # 6. Update h_alternation.yaml for <Pro> left_context
    update_h_alternation_yaml(target_dir / "Phonology/Rules/h_alternation.yaml")


if __name__ == "__main__":
    import sys

    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("chr-config")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("chr-inplace-config")
    configure_inplace_config(src, dst)
    print(f"Successfully configured in-place grammar from {src} to {dst}")
