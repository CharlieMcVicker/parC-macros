"""
parc_macros/generate_phonology.py

Dynamic in-memory generation of phonology configuration:
- Alphabet tags (PrefixClass, Pro, AspectClass, Variant, Aspect, TenseClass, Tense)
- Phoneme group patterns (PrepronominalPrefixes, Root, morpheme unions)
- Dropping rules (drop_root_final.yaml, drop_stem_initial_vowel.yaml) from annotations/CSVs
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path
from typing import Any
import yaml

from parc_macros.generate_markers import derive_open_root_template


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


def extract_phonology_data(
    config_dir: Path, verb_config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Extracts all classes, inflectional features, variants, and rule triggers
    from configuration CSV files, parameterized dynamically by verb_config slots and phonology_effects.
    """
    config_dir = Path(config_dir)

    if verb_config is None:
        for spec_name in ("verb.yaml", "verb_spec.yaml"):
            spec_file = config_dir / spec_name
            if spec_file.exists():
                try:
                    with open(spec_file, "r", encoding="utf-8") as f:
                        verb_config = yaml.safe_load(f) or {}
                    break
                except Exception:
                    pass

    slots: list[dict[str, Any]] = []
    phonology_effects: dict[str, str] = {}
    if verb_config:
        slots = verb_config.get("slots") or verb_config.get("paradigm", {}).get("slots") or []
        phonology_effects = verb_config.get("phonology_effects") or verb_config.get("phonology", {}).get("effects") or {}

    tag_groups: dict[str, list[str]] = {}
    slot_tag_groups: list[str] = []
    max_variants = 1

    if slots:
        for slot in slots:
            sources = slot.get("sources", [])
            structure = slot.get("structure", [])
            if not structure:
                continue

            for st in structure:
                tg_name = st.get("TagGroup")
                if tg_name and tg_name not in tag_groups:
                    tag_groups[tg_name] = []
                if tg_name and tg_name not in slot_tag_groups:
                    slot_tag_groups.append(tg_name)

            for src in sources:
                src_path = config_dir / src
                if not src_path.exists():
                    continue

                with open(src_path, "r", encoding="utf-8") as fh:
                    lines = [line for line in fh if line.strip() and not line.strip().startswith("#")]
                if not lines:
                    continue

                reader = csv.reader(lines)
                rows = list(reader)
                if not rows:
                    continue

                header = rows[0]
                if len(structure) == 1:
                    tg = structure[0]["TagGroup"]
                    for h in header:
                        val = h.strip()
                        if val and val not in tag_groups[tg]:
                            tag_groups[tg].append(val)
                elif len(structure) == 2:
                    cls_tg = structure[0]["TagGroup"]
                    feat_tg = structure[1]["TagGroup"]
                    for r in rows[1:]:
                        if r and r[0].strip():
                            cls_val = r[0].strip()
                            if cls_val not in tag_groups[cls_tg]:
                                tag_groups[cls_tg].append(cls_val)
                    for h in header[1:]:
                        feat_val = h.strip()
                        if feat_val and feat_val not in tag_groups[feat_tg]:
                            tag_groups[feat_tg].append(feat_val)

                    for r in rows[1:]:
                        if not r or not r[0].strip():
                            continue
                        for idx in range(1, len(header)):
                            if idx >= len(r):
                                continue
                            raw_cell = r[idx].strip()
                            if not raw_cell:
                                continue
                            cell_vars = [v.strip() for v in raw_cell.split(";")]
                            if len(cell_vars) > max_variants:
                                max_variants = len(cell_vars)

                elif len(structure) == 3:
                    cls_tg = structure[0]["TagGroup"]
                    var_tg = structure[1]["TagGroup"]
                    feat_tg = structure[2]["TagGroup"]
                    for r in rows[1:]:
                        if r and r[0].strip():
                            cls_val = r[0].strip()
                            if cls_val not in tag_groups[cls_tg]:
                                tag_groups[cls_tg].append(cls_val)
                    for h in header[1:]:
                        feat_val = h.strip()
                        if feat_val and feat_val not in tag_groups[feat_tg]:
                            tag_groups[feat_tg].append(feat_val)

                    for r in rows[1:]:
                        if not r or not r[0].strip():
                            continue
                        for idx in range(1, len(header)):
                            if idx >= len(r):
                                continue
                            raw_cell = r[idx].strip()
                            if not raw_cell:
                                continue
                            cell_vars = [v.strip() for v in raw_cell.split(";")]
                            if len(cell_vars) > max_variants:
                                max_variants = len(cell_vars)

    else:
        # Fallback if no slots defined in verb_config
        p_path = config_dir / "verb-pronominal.csv"
        if p_path.exists():
            p_cls, pros = _parse_csv_matrix(p_path)
            tag_groups["PrefixClass"] = p_cls
            tag_groups["Pro"] = pros
            slot_tag_groups.extend(["PrefixClass", "Pro"])

        a_path = config_dir / "verb-aspect.csv"
        if a_path.exists():
            a_cls, asps = _parse_csv_matrix(a_path)
            tag_groups["AspectClass"] = a_cls
            tag_groups["Aspect"] = asps
            slot_tag_groups.extend(["AspectClass", "Aspect"])

        t_path = config_dir / "verb-tense.csv"
        if t_path.exists():
            with open(t_path, "r", encoding="utf-8") as f:
                t_lines = f.readlines()
            has_class_feature = any(l.lower().startswith("# class_feature:") for l in t_lines)
            t_rows = [r for r in csv.reader(t_lines) if r and not r[0].startswith("#")]
            if t_rows:
                if has_class_feature:
                    t_cls = [r[0].strip() for r in t_rows[1:] if r and r[0].strip()]
                    t_feats = [h.strip() for h in t_rows[0][1:] if h.strip()]
                    tag_groups["TenseClass"] = t_cls
                    tag_groups["Tense"] = t_feats
                    slot_tag_groups.extend(["TenseClass", "Tense"])
                else:
                    t_feats = [h.strip() for h in t_rows[0] if h.strip()]
                    tag_groups["Tense"] = t_feats
                    slot_tag_groups.append("Tense")

    variants = list(range(2, max_variants + 1)) if max_variants > 1 else []
    if "Variant" in tag_groups or "Variant" in slot_tag_groups or variants:
        tag_groups["Variant"] = [str(v) for v in variants]
        if "Variant" not in slot_tag_groups:
            slot_tag_groups.append("Variant")

    # Map legacy keys for backward-compatibility with callers/tests
    prefix_classes = tag_groups.get("PrefixClass", [])
    pronominals = tag_groups.get("Pro", [])
    aspect_classes = tag_groups.get("AspectClass", [])
    aspects = tag_groups.get("Aspect", [])
    tense_classes = tag_groups.get("TenseClass", [])
    tenses = tag_groups.get("Tense", [])

    mark_final_triggers: list[str] = []
    mark_final_two_triggers: list[str] = []

    effects_file = None
    if phonology_effects.get("aspect_drop"):
        effects_file = config_dir / phonology_effects["aspect_drop"]
    elif phonology_effects.get("aspect_effects"):
        effects_file = config_dir / phonology_effects["aspect_effects"]
    elif (config_dir / "aspect_effects.csv").exists():
        effects_file = config_dir / "aspect_effects.csv"
    elif (config_dir / "rule_effects.csv").exists():
        effects_file = config_dir / "rule_effects.csv"

    if effects_file is not None and effects_file.exists():
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

    # Stem-initial vowel drop triggers
    drop_a_src = phonology_effects.get("drop_stem_initial_a")
    drop_first_a_csv = (
        config_dir / drop_a_src if drop_a_src else config_dir / "verb-pronominal-drop-first-a.csv"
    )
    if drop_first_a_csv.exists():
        drop_first_a_triggers = _parse_rule_triggers(drop_first_a_csv)
    else:
        drop_first_a_triggers = [("a_stem", "3sg.A"), ("a_stem", "3sg.B")]

    drop_v_src = phonology_effects.get("drop_stem_initial_v")
    drop_first_v_csv = (
        config_dir / drop_v_src if drop_v_src else config_dir / "verb-pronominal-drop-first-v.csv"
    )
    if drop_first_v_csv.exists():
        drop_first_v_triggers = _parse_rule_triggers(drop_first_v_csv)
    else:
        drop_first_v_triggers = [("v_stem", "3sg.B")]

    return {
        "tag_groups": tag_groups,
        "slot_tag_groups": slot_tag_groups,
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


def generate_slots_manifest(
    output_path: Path | str,
    verb_config: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Writes out slots.json containing:
    - slots: list of slots with name, role, rule, tags
    - template: list of template tokens
    - tag_to_slot: mapping of TagGroup to slot name
    - root_boundaries: {"left": "<H_alt>", "right": "<AspectClass>"} (derived from open_root_template position relative to <Root>)
    """
    slots_config = verb_config.get("slots") or verb_config.get("paradigm", {}).get("slots")
    if not slots_config:
        return None

    slots_list = []
    tag_to_slot = {}
    for slot in slots_config:
        slot_name = slot.get("name", "")
        role = slot.get("role", "")
        rule_raw = slot.get("rule", "")
        rule_name = rule_raw.lstrip("$")
        structure = slot.get("structure", [])
        tags = [item["TagGroup"] for item in structure if "TagGroup" in item]
        for t in tags:
            tag_to_slot[t] = slot_name
        slots_list.append({
            "name": slot_name,
            "role": role,
            "rule": rule_name,
            "tags": tags,
        })

    paradigm_config = verb_config.get("paradigm", {})
    open_root_template = paradigm_config.get("open_root_template", "")
    if not open_root_template:
        open_root_template = derive_open_root_template(verb_config)
    template_tokens = re.findall(r"<[^>]+>", open_root_template)

    root_boundaries = {"left": None, "right": None}
    if "<Root>" in template_tokens:
        root_idx = template_tokens.index("<Root>")
        if root_idx > 0:
            root_boundaries["left"] = template_tokens[root_idx - 1]
        if root_idx + 1 < len(template_tokens):
            root_boundaries["right"] = template_tokens[root_idx + 1]

    manifest = {
        "slots": slots_list,
        "template": template_tokens,
        "tag_to_slot": tag_to_slot,
        "root_boundaries": root_boundaries,
    }

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Generated slots manifest: {out_p}")
    return manifest


def generate_alphabet(
    base_alphabet_path: Path,
    output_alphabet_path: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates Inventory alphabet.yaml dynamically merging base inventory with morpheme tags.
    """
    base_alphabet_path = Path(base_alphabet_path)
    output_alphabet_path = Path(output_alphabet_path)

    with open(base_alphabet_path, "r", encoding="utf-8") as f:
        inv = yaml.safe_load(f) or {}

    tag_groups: dict[str, list[str]] = data.get("tag_groups", {})
    slot_tag_groups: list[str] = data.get("slot_tag_groups", list(tag_groups.keys()))

    filtered_refs = {f"<{tg}>" for tg in slot_tag_groups} | {"<LegacyTags>"}

    new_data: list[dict[str, Any]] = []
    for item in inv.get("data", []):
        ref = item.get("ref")
        if ref in filtered_refs:
            continue
        new_data.append(item)

    for tg in slot_tag_groups:
        vals = tag_groups.get(tg, [])
        if not vals:
            continue
        new_data.append({
            "name": tg,
            "ref": f"<{tg}>",
            "tags": [f"[{tg}={v}]" for v in vals],
        })

    inv["data"] = new_data
    output_alphabet_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_alphabet_path, "w", encoding="utf-8") as f:
        yaml.dump(inv, f, sort_keys=False, default_flow_style=False)


def generate_patterns(
    base_patterns_path: Path,
    output_patterns_path: Path,
    data: dict[str, Any],
) -> None:
    """
    Generates Patterns phoneme_groups.yaml with dynamically generated pattern groups.
    """
    base_patterns_path = Path(base_patterns_path)
    output_patterns_path = Path(output_patterns_path)

    with open(base_patterns_path, "r", encoding="utf-8") as f:
        pats_yaml = yaml.safe_load(f) or {}

    base_patterns = pats_yaml.get("patterns", [])

    tag_groups: dict[str, list[str]] = data.get("tag_groups", {})
    slot_tag_groups: list[str] = data.get("slot_tag_groups", list(tag_groups.keys()))

    # Build dynamic pattern definitions for slot TagGroups
    dynamic_tag_patterns: list[dict[str, Any]] = []
    dynamic_tg_refs = set()

    for tg in slot_tag_groups:
        vals = tag_groups.get(tg, [])
        if not vals:
            continue
        dynamic_tg_refs.add(f"<{tg}>")
        if tg == "Variant":
            # Variant pattern: optional group e.g. ([Variant=2]|[Variant=3]|[Variant=4])?
            v_pat = "(" + "|".join(f"[Variant={v}]" for v in vals) + ")?"
            dynamic_tag_patterns.append({
                "name": "Variant",
                "ref": "<Variant>",
                "pattern": v_pat,
            })
        else:
            pat_str = "|".join(f"[{tg}={v}]" for v in vals)
            dynamic_tag_patterns.append({
                "name": tg,
                "ref": f"<{tg}>",
                "pattern": pat_str,
            })

    # Compose <Morpheme> pattern dynamically:
    # Slot TagGroups (excluding Variant which expands directly if present) + base inventory tags / TagGroups
    morpheme_parts: list[str] = []
    for tg in slot_tag_groups:
        if tg == "Variant":
            continue
        vals = tag_groups.get(tg, [])
        if vals:
            morpheme_parts.append(f"<{tg}>")

    # Read base alphabet.yaml to discover additional tags and inventory TagGroups
    base_alphabet_path = base_patterns_path.parent.parent / "Inventory" / "alphabet.yaml"
    if base_alphabet_path.exists():
        with open(base_alphabet_path, "r", encoding="utf-8") as f:
            base_inv = yaml.safe_load(f) or {}
        for item in base_inv.get("data", []):
            ref = item.get("ref", "")
            tags = item.get("tags", [])
            if not tags:
                continue
            if ref in dynamic_tg_refs or ref in ("<TempTags>", "<LegacyTags>"):
                continue
            if ref:
                morpheme_parts.append(ref)
            for t in tags:
                if t not in morpheme_parts:
                    morpheme_parts.append(t)

    # If variants exist, add [Variant=N] to Morpheme union
    variants = tag_groups.get("Variant", [])
    for v in variants:
        v_tag = f"[Variant={v}]"
        if v_tag not in morpheme_parts:
            morpheme_parts.append(v_tag)

    morpheme_pattern = "|".join(morpheme_parts)

    new_patterns: list[dict[str, Any]] = []
    morpheme_added = False

    for pat in base_patterns:
        ref = pat.get("ref")
        if ref in dynamic_tg_refs:
            continue
        if ref == "<Morpheme>":
            continue
        new_patterns.append(pat)
        # Insert dynamic TagGroups right after <Root> (or after the first base patterns if <Root> is absent)
        if ref == "<Root>":
            new_patterns.extend(dynamic_tag_patterns)
            new_patterns.append({
                "name": "Morpheme",
                "ref": "<Morpheme>",
                "pattern": morpheme_pattern,
            })
            morpheme_added = True

    if not morpheme_added:
        new_patterns.extend(dynamic_tag_patterns)
        new_patterns.append({
            "name": "Morpheme",
            "ref": "<Morpheme>",
            "pattern": morpheme_pattern,
        })

    pats_yaml["kind"] = "Patterns"
    pats_yaml["patterns"] = new_patterns
    output_patterns_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_patterns_path, "w", encoding="utf-8") as f:
        yaml.dump(pats_yaml, f, sort_keys=False, default_flow_style=False)


def generate_phonology_rules(
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
                "description": "mark the final phone for deletion based on aspect triggers",
                "string_map": [["<Phone>", "[TEMP]"]],
                "right_context": drop_final_rc,
            },
            {
                "name": "mark_final_two",
                "description": "mark the final two phones for deletion based on aspect triggers",
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
                "description": "drop final root phone(s) conditioned on aspect class and aspect tags",
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
