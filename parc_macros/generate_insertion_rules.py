"""
generate_insertion_rules.py

Reads insert_*.csv files from an 'insertions/' subdirectory of the config
directory and generates corresponding Phonology/Rules/insert_*.yaml files
in the output directory.

CSV format
----------
Each CSV file must begin with metadata comment lines:
  # kind: insertion
  # rule: <TopLevelRuleName>

Followed by a header row and data rows with columns:
  tag, rule_name, l_context, r_context, content

Each data row becomes one named sub-rule (string_map + optional contexts).
The top-level rule is a rule_sequence over all sub-rule names, named after
the ``# rule:`` metadata value.

Example
-------
  # kind: insertion
  # rule: insert_WI
  tag,rule_name,l_context,r_context,content
  [WI],insert_wi_v_h,,"<V>|h",w
  [WI],insert_wi_default,,,wi

Produces Rules/insert_wi.yaml with rules:
  - insert_wi_v_h  (string_map [WI]->w, right_context "<V>|h")
  - insert_wi_default  (string_map [WI]->wi)
  - insert_WI  (rule_sequence over the above)
"""

import csv
import io
import os
import sys

import yaml


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------

class _LiteralStr(str):
    """Scalar that renders as a YAML literal block (|)."""


def _literal_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


class _InsertionDumper(yaml.Dumper):
    pass


_InsertionDumper.add_representer(_LiteralStr, _literal_representer)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _parse_csv(csv_path: str):
    """
    Parse an insert_*.csv file.

    Returns
    -------
    top_rule_name : str
        Value of the ``# rule:`` metadata header.
    rows : list[dict]
        One dict per data row with keys: tag, rule_name, l_context,
        r_context, content.
    """
    metadata = {}
    data_lines = []

    with open(csv_path, encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("#"):
                # Parse "# key: value" style metadata
                body = stripped[1:].strip()
                if ":" in body:
                    key, _, value = body.partition(":")
                    metadata[key.strip()] = value.strip()
            else:
                data_lines.append(line)

    if metadata.get("kind") != "insertion":
        raise ValueError(
            f"{csv_path}: expected '# kind: insertion' in metadata, "
            f"got {metadata!r}"
        )

    top_rule_name = metadata.get("rule")
    if not top_rule_name:
        raise ValueError(
            f"{csv_path}: missing '# rule: <name>' metadata header"
        )

    reader = csv.DictReader(io.StringIO("".join(data_lines)))
    required_cols = {"tag", "rule_name", "l_context", "r_context", "content"}
    rows = []
    for i, row in enumerate(reader, start=1):
        missing = required_cols - set(row.keys())
        if missing:
            raise ValueError(
                f"{csv_path} row {i}: missing columns {missing}"
            )
        rows.append(
            {
                "tag": row["tag"].strip(),
                "rule_name": row["rule_name"].strip(),
                "l_context": row["l_context"].strip(),
                "r_context": row["r_context"].strip(),
                "content": row["content"].strip(),
            }
        )

    if not rows:
        raise ValueError(f"{csv_path}: no data rows found")

    return top_rule_name, rows


# ---------------------------------------------------------------------------
# YAML generation
# ---------------------------------------------------------------------------

def _build_yaml_doc(top_rule_name: str, rows: list) -> dict:
    """
    Construct the YAML document dict from parsed CSV rows.

    Each row becomes a sub-rule dict; the final entry is the top-level
    rule_sequence.
    """
    rules = []
    sub_rule_names = []

    for row in rows:
        sub_rule: dict = {
            "name": row["rule_name"],
            "string_map": [[row["tag"], row["content"]]],
        }

        if row["l_context"]:
            sub_rule["left_context"] = row["l_context"]

        if row["r_context"]:
            sub_rule["right_context"] = row["r_context"]

        rules.append(sub_rule)
        sub_rule_names.append(f"${row['rule_name']}")

    # Top-level rule_sequence
    rules.append(
        {
            "name": top_rule_name,
            "rule_sequence": sub_rule_names,
        }
    )

    return {"kind": "Rules", "rules": rules}


def _write_yaml(doc: dict, out_path: str) -> None:
    """Serialise *doc* to *out_path* with a generated-file header."""
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("# This is a Rules config file\n")
        fh.write("# Generated automatically by generate_insertion_rules.py\n")
        yaml.dump(
            doc,
            fh,
            Dumper=_InsertionDumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_insertion_rules(config_path: str, output_dir: str) -> None:
    """
    Scan *config_path*/insertions/ for insert_*.csv files and write
    generated YAML to *output_dir*/Phonology/Rules/.

    Parameters
    ----------
    config_path : str
        Path to the config directory (e.g., ``min-min-insertion-config/``).
    output_dir : str
        Path to the output directory (e.g., ``min-min-insertion-generated/``).
    """
    insertions_dir = os.path.join(config_path, "insertions")
    if not os.path.isdir(insertions_dir):
        # No insertions/ folder — nothing to do.
        return

    rules_out_dir = os.path.join(output_dir, "Phonology", "Rules")
    os.makedirs(rules_out_dir, exist_ok=True)

    csv_files = sorted(
        f for f in os.listdir(insertions_dir) if f.startswith("insert_") and f.endswith(".csv")
    )

    if not csv_files:
        return

    for csv_filename in csv_files:
        csv_path = os.path.join(insertions_dir, csv_filename)
        stem = os.path.splitext(csv_filename)[0]  # e.g. "insert_wi"
        yaml_filename = stem + ".yaml"
        out_path = os.path.join(rules_out_dir, yaml_filename)

        top_rule_name, rows = _parse_csv(csv_path)
        doc = _build_yaml_doc(top_rule_name, rows)
        _write_yaml(doc, out_path)
        print(f"Generated insertion rules: {out_path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_insertion_rules.py <config_dir> <output_dir>")
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(config_path):
        print(f"Error: config directory not found: {config_path}")
        sys.exit(1)

    generate_insertion_rules(config_path, output_dir)


if __name__ == "__main__":
    main()
