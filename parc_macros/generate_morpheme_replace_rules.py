import sys
from pathlib import Path
_root = str(Path(__file__).parent.parent.resolve())
if _root not in sys.path:
    sys.path.insert(0, _root)
"""
generate_morpheme_replace_rules.py

Reads CSV files with metadata kind: morpheme_replace from the config directory,
and generates corresponding rules in Rules format.
Supports both:
- In-place mode: adjacent 2-tag rules ([PrefixClass=...][Pro=...], [AspectClass=...][Aspect=...], [TenseClass=...][Tense=...])
- Legacy mode: single-token rules ([Pro] -> k, etc.) for backwards compatibility.
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


def is_in_place_mode(config_dir_or_config: str | os.PathLike | dict | None) -> bool:
    """
    Detect if config specifies in-place mode.
    Checks:
    - paradigm.in_place / use_in_place_tags / in_place_tags
    - open_root_template contains in-place patterns/tags
    """
    if config_dir_or_config is None:
        return False
    if isinstance(config_dir_or_config, dict):
        cfg = config_dir_or_config
    else:
        p = Path(config_dir_or_config)
        verb_yaml = p / "verb.yaml" if p.is_dir() else p
        if not verb_yaml.exists():
            verb_yaml = p / "verb_spec.yaml"
        if not verb_yaml.exists():
            return False
        try:
            with open(verb_yaml, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        except Exception:
            return False

    paradigm_cfg = cfg.get("paradigm", {})
    if (
        paradigm_cfg.get("in_place") is True
        or paradigm_cfg.get("use_in_place_tags") is True
        or paradigm_cfg.get("in_place_tags") is True
    ):
        return True

    open_root_template = paradigm_cfg.get("open_root_template", "")
    in_place_indicators = [
        "<PrefixClass>",
        "<AspectClass>",
        "<TenseClass>",
        "[PrefixClass=",
        "[AspectClass=",
        "[TenseClass=",
    ]
    if any(ind in open_root_template for ind in in_place_indicators):
        return True

    return False


def _generate_inplace_rules(csv_files: list[str], rules_out_dir: str) -> None:
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
            }

        if class_feature:
            class_tag_title = get_class_tag_title(class_feature, metadata)
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
                            clean_v = v.strip().lstrip("*@")
                            if idx == 1:
                                pattern = f"[{class_tag_title}={class_name}][{feature_tag_title}={feat_name}]"
                            else:
                                pattern = f"[{class_tag_title}={class_name}][Variant={idx}][{feature_tag_title}={feat_name}]"
                            tag_mappings[tag_slug]["mappings"][pattern] = clean_v
                    else:
                        clean_v = val.lstrip("*@")
                        pattern = f"[{class_tag_title}={class_name}][{feature_tag_title}={feat_name}]"
                        tag_mappings[tag_slug]["mappings"][pattern] = clean_v
        else:
            feature_cols = reader.fieldnames
            for row in reader:
                for col in feature_cols:
                    feat_name = col.strip()
                    val = row.get(col, "").strip()
                    clean_v = val.lstrip("*@")
                    pattern = f"[{feature_tag_title}={feat_name}]"
                    tag_mappings[tag_slug]["mappings"][pattern] = clean_v

    for tag_slug, info in tag_mappings.items():
        rule_name = info["rule_name"]
        rules_filename = f"{tag_slug}_replace.yaml"
        out_path = os.path.join(rules_out_dir, rules_filename)

        string_map = [
            [inp, val] for inp, val in sorted(info["mappings"].items(), key=lambda x: x[0])
        ]

        doc = {
            "kind": "Rules",
            "rules": [
                {
                    "name": rule_name,
                    "description": f"In-place morpheme replacement rule for {info['morpheme_tag']}",
                    "string_map": string_map,
                }
            ],
        }

        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write("# This is a Rules config file\n")
            fh.write(
                "# Generated automatically by generate_morpheme_replace_rules.py (in-place)\n"
            )
            yaml.dump(
                doc,
                fh,
                Dumper=_ReplaceRulesDumper,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        print(f"Generated in-place morpheme replace rules: {out_path}")


def _generate_legacy_rules(csv_files: list[str], rules_out_dir: str) -> None:
    tag_to_values: dict[str, set[str]] = {}

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

        if morpheme_tag not in tag_to_values:
            tag_to_values[morpheme_tag] = set()

        tag_to_values[morpheme_tag].add("")

        reader = csv.DictReader(io.StringIO("".join(data_lines)))
        if not reader.fieldnames:
            continue

        class_feature = metadata.get("class_feature")
        if class_feature:
            cols = reader.fieldnames[1:]
        else:
            cols = reader.fieldnames

        for row in reader:
            for col in cols:
                if col in row and row[col]:
                    val = row[col].strip()
                    if ";" in val:
                        for v in val.split(";"):
                            clean_v = v.strip().lstrip("*@")
                            tag_to_values[morpheme_tag].add(clean_v)
                    else:
                        clean_v = val.lstrip("*@")
                        tag_to_values[morpheme_tag].add(clean_v)

    if not tag_to_values:
        return

    for morpheme_tag, values in tag_to_values.items():
        tag_slug = re.sub(r"[\[\]]", "", morpheme_tag).lower()
        rules_filename = f"{tag_slug}_replace.yaml"
        out_path = os.path.join(rules_out_dir, rules_filename)

        rules = []
        for val in sorted(values):
            rule_name = f"{tag_slug}_{sanitize_rule_name(val)}"
            rules.append({"name": rule_name, "string_map": [[morpheme_tag, val]]})

        doc = {"kind": "Rules", "rules": rules}

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
    config_path: str, output_dir: str, in_place: bool | None = None
) -> None:
    """
    Scan config directory (and subfolders) for any CSV files containing kind: morpheme_replace.
    If in_place mode is active:
      Generates in-place adjacent 2-tag string_map rules:
      [<ClassFeatureTitle>=<class_name>][<FeatureTitle>=<feature_name>] -> surface replacement.
      Grouping by morpheme slot (e.g. pro_replace, aspect_replace, tense_replace).
    Otherwise (legacy mode):
      Extracts all unique cell values across those CSV files, grouping by morpheme_tag.
      Generates single-token Rules files (pro_replace.yaml with pro_k, pro_ost, etc.).
    """
    if in_place is None:
        in_place = is_in_place_mode(config_path)

    # Find all CSV files recursively in config_path
    csv_files = []
    for root, _, files in os.walk(config_path):
        for f in files:
            if f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))

    rules_out_dir = os.path.join(output_dir, "Phonology", "Rules")
    os.makedirs(rules_out_dir, exist_ok=True)

    if in_place:
        _generate_inplace_rules(csv_files, rules_out_dir)
    else:
        _generate_legacy_rules(csv_files, rules_out_dir)
