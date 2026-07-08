#!/usr/bin/env python3
import csv
import os
import shutil
import sys
import yaml


# To ensure beautiful YAML output
class Dumper(yaml.SafeDumper):
    pass


def dict_representer(dumper, data):
    return dumper.represent_dict(data.items())


Dumper.add_representer(dict, dict_representer)


def parse_csv_with_metadata(csv_path, default_metadata=None):
    metadata = {}
    if default_metadata:
        metadata.update(default_metadata)
    rows = []

    with open(csv_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    csv_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            # Parse metadata comment, e.g. "# kind: suffix" or "# stage: suffix"
            comment_content = stripped[1:].strip()
            if ":" in comment_content:
                key, val = comment_content.split(":", 1)
                key = key.strip().lower()
                val = val.strip()
                # Map keys
                if key in ("operation", "kind"):
                    metadata["kind"] = val
                elif key in ("phase", "stage"):
                    metadata["stage"] = val
                elif key == "feature":
                    metadata["feature"] = val
                elif key == "rule":
                    metadata["rule"] = val
                elif key == "part_of_speech":
                    metadata["part_of_speech"] = val
                elif key == "class_feature":
                    metadata["class_feature"] = val
                else:
                    metadata[key] = val
        else:
            csv_lines.append(line)

    reader = csv.DictReader(csv_lines)
    for row in reader:
        rows.append(row)

    return metadata, reader.fieldnames, rows


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: python generate_markers.py <path_to_config_dir_or_csv> <base_dir> <output_dir>"
        )
        sys.exit(1)

    config_path = sys.argv[1]
    base_dir = sys.argv[2]
    output_dir = sys.argv[3]

    if not os.path.exists(config_path):
        print(f"Error: Config path not found at {config_path}")
        sys.exit(1)

    if not os.path.exists(base_dir):
        print(f"Error: Base directory not found at {base_dir}")
        sys.exit(1)

    # Copy base_dir to output_dir
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    shutil.copytree(base_dir, output_dir)

    # 1. Determine all CSVs and verb.yaml
    csv_files = []
    spec_path = None
    if os.path.isdir(config_path):
        for f in os.listdir(config_path):
            if f.endswith(".csv"):
                csv_files.append(os.path.join(config_path, f))
            elif f == "verb.yaml":
                spec_path = os.path.join(config_path, f)
            elif f == "verb_spec.yaml" and not spec_path:
                spec_path = os.path.join(config_path, f)
    else:
        # Fallback to single csv compatibility
        csv_files.append(config_path)
        # Try to look for verb.yaml or verb_spec.yaml in the same directory
        parent_dir = os.path.dirname(config_path)
        possible_spec = os.path.join(parent_dir, "verb.yaml")
        if os.path.exists(possible_spec):
            spec_path = possible_spec
        else:
            possible_spec = os.path.join(parent_dir, "verb_spec.yaml")
            if os.path.exists(possible_spec):
                spec_path = possible_spec

    pos_name = "verb"
    if spec_path:
        pos_name = os.path.splitext(os.path.basename(spec_path))[0]
        if pos_name.endswith("_spec"):
            pos_name = pos_name[:-5]

    # Load verb.yaml / verb_spec.yaml if it exists
    stage_order = None
    verb_config = {}
    csv_defaults = {}
    if spec_path and os.path.exists(spec_path):
        with open(spec_path, "r", encoding="utf-8") as f:
            verb_config = yaml.safe_load(f) or {}
            if "order" in verb_config:
                stage_order = verb_config["order"]
            elif "stages" in verb_config:
                stage_order = verb_config["stages"]
            csv_defaults = verb_config.get("defaults", {})
    else:
        raise ValueError("Configuration file is required but not found.")

    paradigm_config = verb_config.get("paradigm", {})
    feature_markers_keys = paradigm_config.get("feature_markers_keys", [])
    filename_suffix_keys = paradigm_config.get("filename_suffix_keys", [])

    if "part_of_speech" not in csv_defaults:
        csv_defaults["part_of_speech"] = f"${pos_name}"

    # We will gather all paradigms, and all markers for each paradigm
    # Structure:
    # paradigms_metadata = { paradigm_name: { 'part_of_speech': ..., 'tense': ..., 'mood': ..., 'feature': ... } }
    # paradigms_markers = { paradigm_name: { feature_value: [ {kind, value, stage}, ... ] } }
    paradigms_metadata = {}
    paradigms_markers = {}
    class_features_paradigms = {}

    for csv_file in csv_files:
        metadata, fieldnames, rows = parse_csv_with_metadata(csv_file, csv_defaults)

        csv_class_feature = metadata.get("class_feature")
        if not csv_class_feature:
            raise ValueError(
                f"Required 'class_feature' metadata is missing in CSV file: {csv_file}"
            )

        if csv_class_feature not in class_features_paradigms:
            class_features_paradigms[csv_class_feature] = set()

        id_col = fieldnames[0]
        feature_cols = fieldnames[1:]

        for row in rows:
            paradigm_name = row[id_col].strip()
            if not paradigm_name:
                continue

            class_features_paradigms[csv_class_feature].add(paradigm_name)

            if paradigm_name not in paradigms_metadata:
                paradigms_metadata[paradigm_name] = metadata.copy()

            if paradigm_name not in paradigms_markers:
                paradigms_markers[paradigm_name] = {}

            for col in feature_cols:
                try:
                    val = row[col].strip()
                except Exception as e:
                    raise KeyError(
                        f"Column '{col}' not found in CSV file {csv_file}. Available columns: {fieldnames}"
                    )
                if val:
                    # If kind is rule and a rule name is specified in metadata:
                    # Y means we use the rule name from metadata. N or empty means no entry.
                    if metadata.get("kind") == "rule" and "rule" in metadata:
                        if val.upper() == "Y":
                            val = metadata["rule"]
                        else:
                            # Skip N or empty
                            continue

                    marker_entry = {
                        "kind": metadata["kind"],
                        "value": val,
                        "stage": metadata["stage"],
                    }
                    if col not in paradigms_markers[paradigm_name]:
                        paradigms_markers[paradigm_name][col] = []
                    paradigms_markers[paradigm_name][col].append(marker_entry)

    new_class_values = list(paradigms_metadata.keys())

    # Write the config files for each paradigm
    for paradigm_name, meta in paradigms_metadata.items():
        # Ensure it has correct prefix
        filename_base = paradigm_name
        if not filename_base.startswith(f"{pos_name}_"):
            filename_base = f"{pos_name}_{filename_base}"

        # 1. Generate FeatureMarker YAML
        fm_dir = os.path.join(output_dir, "Exponence", "FeatureMarkers")
        os.makedirs(fm_dir, exist_ok=True)
        fm_file = os.path.join(fm_dir, f"{filename_base}.yaml")

        markers_dict = {}
        # Make sure all markers from the CSVs are in markers_dict
        # We need to preserve the features. We also need to map any empty features to null.
        # But wait! A paradigm might have entries in one CSV (like suffix) and another CSV (like diphthong).
        # We need to collect all possible feature values (columns) from all columns across all CSVs.
        # For simplicity, we can use the keys from paradigms_markers[paradigm_name].
        # But to be safe, let's output null for any of the standard feature values if they don't exist.
        # Standard values for person_number are 1sg, 2sg, 3sg, 1pl, 2pl, 3pl.
        all_cols = sorted(list(set(paradigms_markers[paradigm_name].keys())))

        for col in all_cols:
            entries = paradigms_markers[paradigm_name].get(col, [])
            if entries:
                markers_dict[col] = entries
            else:
                markers_dict[col] = None

        fm_content = {
            "kind": "FeatureMarkers",
            "feature": meta["feature"],
            "markers": markers_dict,
        }

        with open(fm_file, "w", encoding="utf-8") as f:
            f.write("# This is a FeatureMarkers config file\n")
            f.write("# Generated automatically from CSV\n")
            yaml.dump(
                fm_content,
                f,
                Dumper=Dumper,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        print(f"Generated FeatureMarkers: {fm_file}")

        # 2. Generate Paradigm YAML
        paradigm_dir = os.path.join(output_dir, "Morphotactics", "Paradigm")
        os.makedirs(paradigm_dir, exist_ok=True)
        suffixes = [meta[k] for k in filename_suffix_keys if k in meta]
        suffix_str = f"_{'_'.join(suffixes)}" if suffixes else ""
        paradigm_file = os.path.join(
            paradigm_dir, f"{filename_base}{suffix_str}.yaml"
        )

        paradigm_content = {
            "kind": "Paradigm",
            "part_of_speech": meta["part_of_speech"],
            "feature_markers": {
                meta["feature"]: f"${filename_base}",
            },
        }
        for key in feature_markers_keys:
            if key in meta:
                paradigm_content["feature_markers"][key] = meta[key]

        # Add stage_order if defined and this paradigm has markers in multiple stages
        # Or should we only add it if the paradigm has markers spanning multiple stages?
        # Let's count how many distinct stages are actually used in markers_dict for this paradigm.
        used_stages = set()
        for col, entries in markers_dict.items():
            if entries:
                for entry in entries:
                    if "stage" in entry:
                        used_stages.add(entry["stage"])

        if stage_order and len(used_stages) > 1:
            paradigm_content["stage_order"] = stage_order

        # Add filter
        paradigm_content["filter"] = {
            "lexical_features": {meta["class_feature"]: paradigm_name}
        }

        with open(paradigm_file, "w", encoding="utf-8") as f:
            f.write("# This is a Paradigm config file\n")
            f.write("# Generated automatically from CSV\n")
            yaml.dump(
                paradigm_content,
                f,
                Dumper=Dumper,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        print(f"Generated Paradigm: {paradigm_file}")

    # 3. Update Exponence/FeatureDefinitions/{pos_name}_features.yaml
    fd_file = os.path.join(
        output_dir, "Exponence", "FeatureDefinitions", f"{pos_name}_features.yaml"
    )
    if os.path.exists(fd_file):
        with open(fd_file, "r", encoding="utf-8") as f:
            fd_content = yaml.safe_load(f)
    else:
        fd_content = {"kind": "FeatureDefinitions", "features": {}}
        os.makedirs(os.path.dirname(fd_file), exist_ok=True)

    if fd_content and "features" in fd_content:
        # Add inflectional features from verb.yaml
        if "features" in verb_config:
            for feat, vals in verb_config["features"].items():
                fd_content["features"][feat] = vals

        # Update all class features found
        for cf, new_vals in class_features_paradigms.items():
            if cf not in fd_content["features"]:
                fd_content["features"][cf] = []
            cc_list = fd_content["features"][cf]
            if not isinstance(cc_list, list):
                cc_list = []
            for cc in sorted(list(new_vals)):
                if cc not in cc_list:
                    cc_list.append(cc)
            fd_content["features"][cf] = cc_list

        with open(fd_file, "w", encoding="utf-8") as f:
            f.write("# This is a FeatureDefinitions config file\n")
            f.write("# Generated/Updated automatically from CSV\n")
            yaml.dump(
                fd_content,
                f,
                Dumper=Dumper,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        print(f"Updated FeatureDefinitions: {fd_file}")

    # 4. Generate Lexicon/PartOfSpeech/{pos_name}.yaml
    pos_dir = os.path.join(output_dir, "Lexicon", "PartOfSpeech")
    os.makedirs(pos_dir, exist_ok=True)
    pos_file = os.path.join(pos_dir, f"{pos_name}.yaml")

    pos_content = {
        "kind": "PartOfSpeech",
        "name": pos_name,
        "features": list(verb_config.get("features", {}).keys()),
    }
    if "lexical_features" in verb_config:
        pos_content["lexical_features"] = verb_config["lexical_features"]

    with open(pos_file, "w", encoding="utf-8") as f:
        f.write("# This is a PartOfSpeech config file\n")
        f.write("# Generated automatically from config/verb.yaml\n")
        yaml.dump(
            pos_content,
            f,
            Dumper=Dumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    print(f"Generated PartOfSpeech: {pos_file}")


if __name__ == "__main__":
    main()
