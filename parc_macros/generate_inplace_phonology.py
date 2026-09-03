"""
parc_macros/generate_inplace_phonology.py

Dynamic in-memory generation of in-place phonology configuration:
- Alphabet tags (PrefixClass, Pro, AspectClass, Variant, Aspect, TenseClass, Tense, LegacyTags)
- Phoneme group patterns (PrepronominalPrefixes, Root, morpheme unions)
- Dropping rules (drop_root_final.yaml, drop_stem_initial_vowel.yaml) from annotations/CSVs
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


def extract_inplace_data(config_dir: Path) -> dict[str, Any]:
    """
    Extracts all classes, inflectional features, variants, and rule triggers
    from configuration CSV files.
    """
    config_dir = Path(config_dir)

    # 1. Pronominals and prefix classes
    prefix_classes, pronominals = _parse_csv_matrix(config_dir / "verb-pronominal.csv")

    # 2. Tenses and tense classes
    tense_classes, tenses = _parse_csv_matrix(config_dir / "verb-tense.csv")

    # 3. Aspects, aspect classes, variants, and drop-final triggers from verb-aspect.csv
    aspect_csv_path = config_dir / "verb-aspect.csv"
    with open(aspect_csv_path, "r", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]

    if not rows:
        raise ValueError(f"Empty aspect CSV: {aspect_csv_path}")

    header = rows[0]
    aspect_classes = [r[0].strip() for r in rows[1:] if r and r[0].strip()]
    aspects = [h.strip() for h in header[1:] if h.strip()]

    max_variants = 1
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        for idx in range(1, len(header)):
            if idx >= len(r):
                continue
            raw_cell = r[idx].strip()
            if not raw_cell:
                continue
            cell_variants = [v.strip() for v in raw_cell.split(";")]
            if len(cell_variants) > max_variants:
                max_variants = len(cell_variants)

    variants = list(range(2, max_variants + 1)) if max_variants > 1 else []

    mark_final_triggers: list[str] = []
    mark_final_two_triggers: list[str] = []

    effects_file = None
    if (config_dir / "aspect_effects.csv").exists():
        effects_file = config_dir / "aspect_effects.csv"
    elif (config_dir / "rule_effects.csv").exists():
        effects_file = config_dir / "rule_effects.csv"

    if effects_file is not None:
        with open(effects_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(r for r in f if not r.startswith("#"))
            for row in reader:
                cls = row["aspect_class"].strip()
                feat = row["aspect"].strip()
                var = row.get("variant", "").strip()
                eff = row["effect"].strip()
                if var and var != "1":
                    trigger = f"[AspectClass={cls}][Variant={var}][Aspect={feat}]"
                else:
                    trigger = f"[AspectClass={cls}][Aspect={feat}]"
                if eff == "drop_final":
                    mark_final_triggers.append(trigger)
                elif eff == "drop_final_two":
                    mark_final_two_triggers.append(trigger)
    else:
        # Fallback to verb-aspect-drop-final.csv if present
        if (config_dir / "verb-aspect-drop-final.csv").exists():
            raw_triggers = _parse_rule_triggers(config_dir / "verb-aspect-drop-final.csv")
            for cls_expr, feat in raw_triggers:
                m = re.match(r"^([^\[]+)(\[Variant=\d+\])?", cls_expr)
                if m:
                    base_cls, var_tag = m.groups()
                    var_tag = var_tag or ""
                    mark_final_triggers.append(f"[AspectClass={base_cls}]{var_tag}[Aspect={feat}]")
                else:
                    mark_final_triggers.append(f"[AspectClass={cls_expr}][Aspect={feat}]")

        # Fallback to verb-aspect-drop-final-two.csv if present
        if (config_dir / "verb-aspect-drop-final-two.csv").exists():
            raw_triggers = _parse_rule_triggers(config_dir / "verb-aspect-drop-final-two.csv")
            for cls_expr, feat in raw_triggers:
                m = re.match(r"^([^\[]+)(\[Variant=\d+\])?", cls_expr)
                if m:
                    base_cls, var_tag = m.groups()
                    var_tag = var_tag or ""
                    mark_final_two_triggers.append(f"[AspectClass={base_cls}]{var_tag}[Aspect={feat}]")
                else:
                    mark_final_two_triggers.append(f"[AspectClass={cls_expr}][Aspect={feat}]")

    # 4. Stem-initial vowel drop triggers
    drop_first_a_csv = config_dir / "verb-pronominal-drop-first-a.csv"
    if drop_first_a_csv.exists():
        drop_first_a_triggers = _parse_rule_triggers(drop_first_a_csv)
    else:
        drop_first_a_triggers = [("a_stem", "3sg.A"), ("a_stem", "3sg.B")]

    drop_first_v_csv = config_dir / "verb-pronominal-drop-first-v.csv"
    if drop_first_v_csv.exists():
        drop_first_v_triggers = _parse_rule_triggers(drop_first_v_csv)
    else:
        drop_first_v_triggers = [("v_stem", "3sg.B")]

    return {
        "prefix_classes": prefix_classes,
        "pronominals": pronominals,
        "aspect_classes": aspect_classes,
        "aspects": aspects,
        "tense_classes": tense_classes,
        "tenses": tenses,
        "variants": variants,
        "mark_final_triggers": mark_final_triggers,
        "mark_final_two_triggers": mark_final_two_triggers,
        "drop_first_a_triggers": drop_first_a_triggers,
        "drop_first_v_triggers": drop_first_v_triggers,
    }


def generate_inplace_alphabet(
    base_alphabet_path: Path,
    output_alphabet_path: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates Inventory alphabet.yaml dynamically merging base inventory with in-place tags.
    """
    base_alphabet_path = Path(base_alphabet_path)
    output_alphabet_path = Path(output_alphabet_path)

    with open(base_alphabet_path, "r", encoding="utf-8") as f:
        inv = yaml.safe_load(f) or {}

    filtered_refs = {
        "<PrefixClass>",
        "<Pro>",
        "<AspectClass>",
        "<Variant>",
        "<Aspect>",
        "<TenseClass>",
        "<Tense>",
        "<LegacyTags>",
    }

    new_data: list[dict[str, Any]] = []
    for item in inv.get("data", []):
        ref = item.get("ref")
        if ref in filtered_refs:
            continue
        new_data.append(item)

    # PrefixClass
    new_data.append({
        "name": "PrefixClass",
        "ref": "<PrefixClass>",
        "tags": [f"[PrefixClass={c}]" for c in data["prefix_classes"]],
    })

    # Pro
    new_data.append({
        "name": "Pro",
        "ref": "<Pro>",
        "tags": [f"[Pro={p}]" for p in data["pronominals"]],
    })

    # AspectClass
    new_data.append({
        "name": "AspectClass",
        "ref": "<AspectClass>",
        "tags": [f"[AspectClass={c}]" for c in data["aspect_classes"]],
    })

    # Variant
    variants = data.get("variants", [])
    if variants:
        new_data.append({
            "name": "Variant",
            "ref": "<Variant>",
            "tags": [f"[Variant={v}]" for v in variants],
        })

    # Aspect
    new_data.append({
        "name": "Aspect",
        "ref": "<Aspect>",
        "tags": [f"[Aspect={a}]" for a in data["aspects"]],
    })

    # TenseClass
    new_data.append({
        "name": "TenseClass",
        "ref": "<TenseClass>",
        "tags": [f"[TenseClass={c}]" for c in data["tense_classes"]],
    })

    # Tense
    new_data.append({
        "name": "Tense",
        "ref": "<Tense>",
        "tags": [f"[Tense={t}]" for t in data["tenses"]],
    })

    # Legacy Tags
    new_data.append({
        "name": "Legacy Tags",
        "ref": "<LegacyTags>",
        "tags": ["[Pro]", "[Aspect]", "[Tense]"],
    })

    inv["data"] = new_data
    output_alphabet_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_alphabet_path, "w", encoding="utf-8") as f:
        yaml.dump(inv, f, sort_keys=False, default_flow_style=False)


# Alias for compatibility
generate_inplace_inventory = generate_inplace_alphabet


def generate_inplace_patterns(
    base_patterns_path: Path,
    output_patterns_path: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates Patterns phoneme_groups.yaml with dynamically generated in-place pattern groups.
    """
    base_patterns_path = Path(base_patterns_path)
    output_patterns_path = Path(output_patterns_path)

    with open(base_patterns_path, "r", encoding="utf-8") as f:
        pats_yaml = yaml.safe_load(f) or {}

    retained_map: dict[str, dict[str, Any]] = {}
    for pat in pats_yaml.get("patterns", []):
        ref = pat.get("ref")
        if ref in ("<C>", "<NotLar>", "<SonH>", "<HTarget>", "<H_alt>", "<H_ALT>"):
            retained_map[ref] = pat

    c_pat = retained_map.get("<C>", {
        "name": "Consonants",
        "pattern": "<Stops>|<Frc>|<Son>|<N>",
        "ref": "<C>",
    })

    not_lar_pat = retained_map.get("<NotLar>", {
        "name": "NotLar",
        "pattern": "{tkmnslyw}|<V>",
        "ref": "<NotLar>",
    })

    son_h_pat = retained_map.get("<SonH>", {
        "name": "SonH",
        "pattern": "nh|lh|yh|wh|mh",
        "ref": "<SonH>",
    })

    h_target_pat = retained_map.get("<HTarget>", {
        "name": "HTarget",
        "pattern": "h<V>|<SonH>",
        "ref": "<HTarget>",
    })

    prefix_class_pat = "|".join(f"[PrefixClass={c}]" for c in data["prefix_classes"])
    pro_pat = "|".join(f"[Pro={p}]" for p in data["pronominals"])
    aspect_class_pat = "|".join(f"[AspectClass={c}]" for c in data["aspect_classes"])
    aspect_pat = "|".join(f"[Aspect={a}]" for a in data["aspects"])
    tense_class_pat = "|".join(f"[TenseClass={c}]" for c in data["tense_classes"])
    tense_pat = "|".join(f"[Tense={t}]" for t in data["tenses"])

    variants = data.get("variants", [])
    variant_pat = (
        "(" + "|".join(f"[Variant={v}]" for v in variants) + ")?"
        if variants
        else "([Variant=2]|[Variant=3]|[Variant=4])?"
    )
    variant_morphemes = (
        "|" + "|".join(f"[Variant={v}]" for v in variants) if variants else ""
    )

    morpheme_pat = (
        f"<PrefixClass>|<Pro>|<AspectClass>|<Aspect>|<TenseClass>|<Tense>"
        f"|<PPP>|<H_alt>|[WI]|[DIST]|[DIST=de]|[DIST=di]{variant_morphemes}"
    )

    new_patterns: list[dict[str, Any]] = [
        c_pat,
        {
            "name": "PrepronominalPrefixes",
            "ref": "<PrepronominalPrefixes>",
            "pattern": "[WI]?([DIST=de]|[DIST=di])?",
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
            "name": "Variant",
            "ref": "<Variant>",
            "pattern": variant_pat,
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
            "pattern": morpheme_pat,
        },
        {
            "name": "H_alt",
            "ref": "<H_alt>",
            "pattern": "<H_alt>",
        },
        not_lar_pat,
        son_h_pat,
        h_target_pat,
    ]

    pats_yaml["kind"] = "Patterns"
    pats_yaml["patterns"] = new_patterns
    output_patterns_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_patterns_path, "w", encoding="utf-8") as f:
        yaml.dump(pats_yaml, f, sort_keys=False, default_flow_style=False)


def generate_inplace_rules(
    config_dir: Path,
    output_rules_dir: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates drop_root_final.yaml and drop_stem_initial_vowel.yaml,
    and copies other rule YAML files (e.g. h_alternation.yaml).
    """
    config_dir = Path(config_dir)
    output_rules_dir = Path(output_rules_dir)
    output_rules_dir.mkdir(parents=True, exist_ok=True)

    # 1. drop_root_final.yaml
    drop_final_rc = "|".join(data.get("mark_final_triggers", []))
    drop_final_two_rc = "|".join(data.get("mark_final_two_triggers", []))

    drop_root_final_yaml = {
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
    with open(output_rules_dir / "drop_root_final.yaml", "w", encoding="utf-8") as f:
        yaml.dump(drop_root_final_yaml, f, sort_keys=False, default_flow_style=False)

    # 2. drop_stem_initial_vowel.yaml
    drop_a_branches = [
        f"[PrefixClass={cls}][Pro={pro}]<H_alt>?"
        for cls, pro in data.get("drop_first_a_triggers", [])
    ]
    drop_a_lc = "|".join(drop_a_branches) if drop_a_branches else "[PrefixClass=a_stem][Pro=3sg.A]<H_alt>?|[PrefixClass=a_stem][Pro=3sg.B]<H_alt>?"

    drop_v_branches = [
        f"[PrefixClass={cls}][Pro={pro}]<H_alt>?"
        for cls, pro in data.get("drop_first_v_triggers", [])
    ]
    drop_v_lc = "|".join(drop_v_branches) if drop_v_branches else "[PrefixClass=v_stem][Pro=3sg.B]<H_alt>?"

    drop_stem_initial_vowel_yaml = {
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
    with open(output_rules_dir / "drop_stem_initial_vowel.yaml", "w", encoding="utf-8") as f:
        yaml.dump(drop_stem_initial_vowel_yaml, f, sort_keys=False, default_flow_style=False)

    # 3. Copy rule YAMLs from config_dir (e.g. h_alternation.yaml)
    src_rules = config_dir / "Phonology" / "Rules"
    if src_rules.exists():
        for rf in src_rules.glob("*.yaml"):
            if rf.name not in ("drop_root_final.yaml", "drop_stem_initial_vowel.yaml"):
                shutil.copy2(rf, output_rules_dir / rf.name)
