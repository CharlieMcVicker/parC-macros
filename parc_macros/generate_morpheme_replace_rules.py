"""
generate_morpheme_replace_rules.py

Reads CSV files with metadata kind: morpheme_replace from the config directory,
gathers all unique cell values across all cells, and generates corresponding rules in Rules format.
"""

import csv
import io
import os
import re
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
    # Keep alphanumeric characters and underscores, replace others with underscore
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", val)
    return sanitized


def generate_morpheme_replace_rules(config_path: str, output_dir: str) -> None:
    """
    Scan config directory (and subfolders) for any CSV files containing kind: morpheme_replace.
    Extracts all unique non-empty cell values across those CSV files, grouping by morpheme_tag.
    Generates a single Rules file for each unique morpheme_tag.
    """
    # Find all CSV files recursively in config_path
    csv_files = []
    for root, _, files in os.walk(config_path):
        for f in files:
            if f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))

    # We map morpheme_tag -> set of unique values
    tag_to_values = {}

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

        # Always ensure the empty/null replacement exists if there are rules
        tag_to_values[morpheme_tag].add("")

        reader = csv.DictReader(io.StringIO("".join(data_lines)))
        if not reader.fieldnames:
            continue

        # Non-contingent has no paradigm column (class_feature is missing), contingent has class_feature/paradigm column
        # Let's inspect fields
        class_feature = metadata.get("class_feature")
        if class_feature:
            # Contingent: first column is the class/paradigm name, rest are features
            cols = reader.fieldnames[1:]
        else:
            # Non-contingent: all columns are features
            cols = reader.fieldnames

        for row in reader:
            for col in cols:
                if col in row and row[col]:
                    val = row[col].strip()
                    tag_to_values[morpheme_tag].add(val)

    if not tag_to_values:
        return

    rules_out_dir = os.path.join(output_dir, "Phonology", "Rules")
    os.makedirs(rules_out_dir, exist_ok=True)

    for morpheme_tag, values in tag_to_values.items():
        # Sanitize tag for filename, e.g., "[Pro]" -> "pro"
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
