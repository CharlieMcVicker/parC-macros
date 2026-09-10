import sys
from pathlib import Path
_root = str(Path(__file__).parent.parent.resolve())
if _root not in sys.path:
    sys.path.insert(0, _root)
"""
generate_morpheme_replace_rules.py

Reads CSV files with metadata kind: morpheme_replace from the config directory,
and generates adjacent 2-tag replacement rules in Rules format:
([PrefixClass=...][Pro=...], [AspectClass=...][Aspect=...], [TenseClass=...][Tense=...]).
"""

import csv
import io
import os
import re
from pathlib import Path
import yaml


class _LiteralStr(str):
    pass


def _literal_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


class _ReplaceRulesDumper(yaml.Dumper):
    pass


_ReplaceRulesDumper.add_representer(_LiteralStr, _literal_representer)


def sanitize_rule_name(val: str) -> str:
    """Sanitize a form value to make it a safe rule name suffix."""
    if not val:
        return "empty"
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", val)
    return sanitized


CLASS_FEATURE_TO_TAG_TITLE = {
    "prefix_class": "PrefixClass",
    "aspect_class": "AspectClass",
    "tense_present_class": "TenseClass",
    "tense_class": "TenseClass",
}


def get_class_tag_title(class_feature: str, metadata: dict | None = None) -> str:
    """Determine the class tag title (e.g. PrefixClass, AspectClass, TenseClass)."""
    if metadata and "class_tag" in metadata:
        return metadata["class_tag"].strip("[]")
    if class_feature in CLASS_FEATURE_TO_TAG_TITLE:
        return CLASS_FEATURE_TO_TAG_TITLE[class_feature]
    return "".join(part.capitalize() for part in class_feature.split("_"))


def _load_class_acceptors(config_dir: Path, class_feature_name: str) -> dict[str, str]:
    """Loads class -> right_context pattern mappings from feature_acceptors directory if available."""
    snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", class_feature_name).lower()
    candidate_paths = [
        config_dir / "feature_acceptors" / f"{snake_name}.csv",
        config_dir / "feature_acceptors" / f"{class_feature_name.lower()}.csv",
        config_dir / f"{snake_name}.csv",
    ]
    for p in candidate_paths:
        if p.exists():
            acceptors = {}
            try:
                with open(p, "r", encoding="utf-8") as afh:
                    for arow in csv.reader(afh):
                        if not arow or not arow[0].strip() or arow[0].strip().startswith("#"):
                            continue
                        cname = arow[0].strip()
                        if cname in ("prefix_class", snake_name, class_feature_name.lower(), "class", "paradigm"):
                            continue
                        cpat = arow[1].strip() if len(arow) > 1 else ""
                        if cname and cpat:
                            acceptors[cname] = cpat
                if acceptors:
                    return acceptors
            except Exception:
                pass
    return {}


def _generate_rules(csv_files: list[str], rules_out_dir: str) -> None:
    tag_mappings: dict[str, dict] = {}

    for csv_path in csv_files:
        try:
            with open(csv_path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except Exception:
            continue

        metadata = {}
        data_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                body = stripped[1:].strip()
                if ":" in body:
                    key, _, value = body.partition(":")
                    metadata[key.strip().lower()] = value.strip()
            else:
                data_lines.append(line)

        if metadata.get("kind") != "morpheme_replace":
            continue

        morpheme_tag = metadata["morpheme_tag"]
        tag_slug = re.sub(r"[\[\]]", "", morpheme_tag).lower()
        feature_tag_title = morpheme_tag.replace("[", "").replace("]", "").strip()
        class_feature = metadata.get("class_feature")
        rule_name = metadata.get("rule", f"{tag_slug}_replace").lstrip("$")

        reader = csv.DictReader(io.StringIO("".join(data_lines)))
        if not reader.fieldnames:
            continue

        if tag_slug not in tag_mappings:
            tag_mappings[tag_slug] = {
                "morpheme_tag": morpheme_tag,
                "rule_name": rule_name,
                "mappings": {},
                "class_mappings": {},
                "class_feature": class_feature,
                "class_tag_title": None,
                "class_acceptors": {},
            }

        csv_dir = Path(csv_path).parent
        if class_feature:
            class_tag_title = get_class_tag_title(class_feature, metadata)
            tag_mappings[tag_slug]["class_tag_title"] = class_tag_title
            tag_mappings[tag_slug]["class_acceptors"] = _load_class_acceptors(csv_dir, class_feature)
            id_col = reader.fieldnames[0]
            feature_cols = reader.fieldnames[1:]

            for row in reader:
                class_name = row.get(id_col, "").strip()
                if not class_name:
                    continue
                if class_name not in tag_mappings[tag_slug]["class_mappings"]:
                    tag_mappings[tag_slug]["class_mappings"][class_name] = {}

                for col in feature_cols:
                    feat_name = col.strip()
                    val = row.get(col, "").strip()
                    if ";" in val:
                        variants = val.split(";")
                        for idx, v in enumerate(variants, start=1):
                            clean_v = v.strip()
                            if idx == 1:
                                pattern = f"[{class_tag_title}={class_name}][{feature_tag_title}={feat_name}]"
                            else:
                                pattern = f"[{class_tag_title}={class_name}][Variant={idx}][{feature_tag_title}={feat_name}]"
                            tag_mappings[tag_slug]["mappings"][pattern] = clean_v
                            tag_mappings[tag_slug]["class_mappings"][class_name][pattern] = clean_v
                    else:
                        clean_v = val.strip()
                        pattern = f"[{class_tag_title}={class_name}][{feature_tag_title}={feat_name}]"
                        tag_mappings[tag_slug]["mappings"][pattern] = clean_v
                        tag_mappings[tag_slug]["class_mappings"][class_name][pattern] = clean_v
        else:
            feature_cols = reader.fieldnames
            for row in reader:
                for col in feature_cols:
                    feat_name = col.strip()
                    val = row.get(col, "").strip()
                    clean_v = val.strip()
                    pattern = f"[{feature_tag_title}={feat_name}]"
                    tag_mappings[tag_slug]["mappings"][pattern] = clean_v

    for tag_slug, info in tag_mappings.items():
        rule_name = info["rule_name"]
        rules_filename = f"{tag_slug}_replace.yaml"
        out_path = os.path.join(rules_out_dir, rules_filename)

        class_acceptors = info.get("class_acceptors", {})
        class_mappings = info.get("class_mappings", {})

        if class_acceptors and class_mappings:
            sub_rules = []
            for class_name in sorted(class_mappings.keys()):
                c_maps = class_mappings[class_name]
                sub_rule_name = f"{rule_name}_{sanitize_rule_name(class_name)}"
                string_map = [
                    [inp, val] for inp, val in sorted(c_maps.items(), key=lambda x: x[0])
                ]
                sub_rule_doc = {
                    "name": sub_rule_name,
                    "description": f"Morpheme replacement for {info['morpheme_tag']} conditioned on [{info['class_tag_title']}={class_name}]",
                    "string_map": string_map,
                }
                if class_name in class_acceptors:
                    sub_rule_doc["right_context"] = class_acceptors[class_name]
                sub_rules.append(sub_rule_doc)

            top_rule = {
                "name": rule_name,
                "description": f"Morpheme replacement rule for {info['morpheme_tag']}",
                "rule_sequence": [f"${sr['name']}" for sr in sub_rules],
            }
            doc = {
                "kind": "Rules",
                "rules": sub_rules + [top_rule],
            }
        else:
            string_map = [
                [inp, val] for inp, val in sorted(info["mappings"].items(), key=lambda x: x[0])
            ]
            doc = {
                "kind": "Rules",
                "rules": [
                    {
                        "name": rule_name,
                        "description": f"Morpheme replacement rule for {info['morpheme_tag']}",
                        "string_map": string_map,
                    }
                ],
            }

        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write("# This is a Rules config file\n")
            fh.write(
                "# Generated automatically by generate_morpheme_replace_rules.py\n"
            )
            yaml.dump(
                doc,
                fh,
                Dumper=_ReplaceRulesDumper,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        print(f"Generated morpheme replace rules: {out_path}")


def _generate_rules_from_slots(
    config_dir: Path, rules_out_dir: str, slots: list[dict]
) -> None:
    for slot in slots:
        slot_name = slot.get("name", "")
        rule_raw = slot.get("rule", f"${slot_name}_replace")
        rule_name = rule_raw.lstrip("$")
        sources = slot.get("sources", [])
        structure = slot.get("structure", [])

        if not structure:
            continue

        feature_tag_title = structure[-1]["TagGroup"]
        mappings: dict[str, str] = {}
        class_mappings: dict[str, dict[str, str]] = {}
        class_acceptors: dict[str, str] = {}
        class_tag_title: str | None = None

        for src in sources:
            src_path = config_dir / src
            if not src_path.exists():
                continue

            with open(src_path, "r", encoding="utf-8") as fh:
                data_lines = [
                    line for line in fh
                    if line.strip() and not line.strip().startswith("#")
                ]

            if not data_lines:
                continue

            reader = csv.DictReader(io.StringIO("".join(data_lines)))
            if not reader.fieldnames:
                continue

            if len(structure) == 1:
                # 1 TagGroup (e.g. Tense): [Tense={val}] -> surface
                tag_group = structure[0]["TagGroup"]
                for row in reader:
                    for col in reader.fieldnames:
                        feat_name = col.strip()
                        val = row.get(col, "").strip()
                        pattern = f"[{tag_group}={feat_name}]"
                        mappings[pattern] = val

            elif len(structure) == 2:
                # 2 TagGroups (e.g. PrefixClass, Pro): [PrefixClass={row}][Pro={col}] -> surface
                class_tag = structure[0]["TagGroup"]
                feat_tag = structure[1]["TagGroup"]
                class_tag_title = class_tag
                class_acceptors = _load_class_acceptors(config_dir, class_tag)
                id_col = reader.fieldnames[0]
                feature_cols = reader.fieldnames[1:]

                for row in reader:
                    class_name = row.get(id_col, "").strip()
                    if not class_name:
                        continue
                    if class_name not in class_mappings:
                        class_mappings[class_name] = {}
                    for col in feature_cols:
                        feat_name = col.strip()
                        val = row.get(col, "").strip()
                        pattern = f"[{class_tag}={class_name}][{feat_tag}={feat_name}]"
                        mappings[pattern] = val
                        class_mappings[class_name][pattern] = val

            elif len(structure) == 3:
                # 3 TagGroups (e.g. AspectClass, Variant, Aspect):
                # Variant 1 (optional omitted): [AspectClass={row}][Aspect={col}] -> surface
                # Variant N (optional present): [AspectClass={row}][Variant={N}][Aspect={col}] -> surface
                class_tag = structure[0]["TagGroup"]
                opt_tag = structure[1]["TagGroup"]
                feat_tag = structure[2]["TagGroup"]
                id_col = reader.fieldnames[0]
                feature_cols = reader.fieldnames[1:]

                for row in reader:
                    class_name = row.get(id_col, "").strip()
                    if not class_name:
                        continue
                    for col in feature_cols:
                        feat_name = col.strip()
                        val = row.get(col, "").strip()
                        if ";" in val:
                            variants = val.split(";")
                            for idx, v in enumerate(variants, start=1):
                                clean_v = v.strip()
                                if idx == 1:
                                    pattern = f"[{class_tag}={class_name}][{feat_tag}={feat_name}]"
                                else:
                                    pattern = f"[{class_tag}={class_name}][{opt_tag}={idx}][{feat_tag}={feat_name}]"
                                mappings[pattern] = clean_v
                        else:
                            clean_v = val.strip()
                            pattern = f"[{class_tag}={class_name}][{feat_tag}={feat_name}]"
                            mappings[pattern] = clean_v

        rules_filename = f"{rule_name}.yaml"
        out_path = os.path.join(rules_out_dir, rules_filename)

        if class_acceptors and class_mappings:
            sub_rules = []
            for class_name in sorted(class_mappings.keys()):
                c_maps = class_mappings[class_name]
                sub_rule_name = f"{rule_name}_{sanitize_rule_name(class_name)}"
                string_map = [
                    [inp, val] for inp, val in sorted(c_maps.items(), key=lambda x: x[0])
                ]
                sub_rule_doc = {
                    "name": sub_rule_name,
                    "description": f"Morpheme replacement for [{feature_tag_title}] conditioned on [{class_tag_title}={class_name}]",
                    "string_map": string_map,
                }
                if class_name in class_acceptors:
                    sub_rule_doc["right_context"] = class_acceptors[class_name]
                sub_rules.append(sub_rule_doc)

            top_rule = {
                "name": rule_name,
                "description": f"Morpheme replacement rule for [{feature_tag_title}]",
                "rule_sequence": [f"${sr['name']}" for sr in sub_rules],
            }
            doc = {
                "kind": "Rules",
                "rules": sub_rules + [top_rule],
            }
        else:
            string_map = [
                [inp, val] for inp, val in sorted(mappings.items(), key=lambda x: x[0])
            ]
            doc = {
                "kind": "Rules",
                "rules": [
                    {
                        "name": rule_name,
                        "description": f"Morpheme replacement rule for [{feature_tag_title}]",
                        "string_map": string_map,
                    }
                ],
            }

        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write("# This is a Rules config file\n")
            fh.write(
                "# Generated automatically by generate_morpheme_replace_rules.py\n"
            )
            yaml.dump(
                doc,
                fh,
                Dumper=_ReplaceRulesDumper,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        print(f"Generated morpheme replace rules: {out_path}")


def generate_morpheme_replace_rules(
    config_path: str, output_dir: str, verb_config: dict | None = None
) -> None:
    """
    Scan config directory (and subfolders) for any CSV files containing kind: morpheme_replace,
    or generate rules from slots declared in verb_config.
    Generates adjacent string_map rules:
    Grouping by morpheme slot (e.g. pro_replace, aspect_replace, tense_replace).
    """
    rules_out_dir = os.path.join(output_dir, "Phonology", "Rules")
    os.makedirs(rules_out_dir, exist_ok=True)

    cfg_dir = Path(config_path)
    if verb_config is None and cfg_dir.is_dir():
        for spec_name in ("verb.yaml", "verb_spec.yaml"):
            spec_file = cfg_dir / spec_name
            if spec_file.exists():
                try:
                    with open(spec_file, "r", encoding="utf-8") as fh:
                        verb_config = yaml.safe_load(fh) or {}
                    break
                except Exception:
                    pass

    slots = []
    if verb_config:
        slots = verb_config.get("slots") or verb_config.get("paradigm", {}).get("slots") or []

    if slots and cfg_dir.is_dir():
        _generate_rules_from_slots(cfg_dir, rules_out_dir, slots)
        return

    # Fallback to individual CSV processing
    csv_files = []
    if cfg_dir.is_dir():
        for root, _, files in os.walk(config_path):
            for f in files:
                if f.endswith(".csv"):
                    csv_files.append(os.path.join(root, f))
    else:
        csv_files.append(config_path)

    _generate_rules(csv_files, rules_out_dir)
