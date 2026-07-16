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


def parse_csv_with_metadata(csv_path):
    metadata = {}
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


def map_csv_to_markers(csv_file):
    """
    Parses a single CSV file containing marker/rule mapping definitions, extracts metadata,
    and maps each row to paradigm-specific features.

    This function represents the 'map' step in a map-reduce style processing of the
    configuration files. It parses the CSV file, validates the presence of critical
    metadata like 'class_feature', and constructs a localized representation of the
    paradigms, markers, and class values defined within that single file.

    Args:
        csv_file (str): Absolute or relative path to the input CSV file.

    Returns:
        dict: A dictionary containing:
            - "metadata": The parsed metadata from comments.
            - "class_feature": The category identifier (e.g., 'conjugation_class').
            - "paradigms_markers": A dictionary mapping paradigm_name to a dictionary of
              feature-to-marker lists.
            - "paradigm_names": A set of all paradigm names encountered.
    """
    metadata, fieldnames, rows = parse_csv_with_metadata(csv_file)

    csv_class_feature = metadata.get("class_feature")

    paradigms_markers = {}
    paradigm_names = set()

    if not csv_class_feature:
        # Non-contingent (general) FeatureMarkers: columns are feature values directly.
        # There is no paradigm column.
        feature_cols = fieldnames
        dummy_paradigm = ""
        paradigms_markers[dummy_paradigm] = {}
        for col in feature_cols:
            for row in rows:
                try:
                    val = row[col].strip()
                except Exception as e:
                    raise KeyError(
                        f"Column '{col}' not found in CSV file {csv_file}. Available columns: {fieldnames}"
                    ) from e
                if val or (val == "" and metadata.get("kind") != "rule"):
                    if metadata.get("kind") == "rule" and "rule" in metadata:
                        if val.upper() == "Y":
                            val = metadata["rule"]
                        else:
                            continue
                    marker_entry = {
                        "kind": metadata["kind"],
                        "value": val,
                        "stage": metadata["stage"],
                    }
                    if col not in paradigms_markers[dummy_paradigm]:
                        paradigms_markers[dummy_paradigm][col] = []
                    paradigms_markers[dummy_paradigm][col].append(marker_entry)
    else:
        id_col = fieldnames[0]
        feature_cols = fieldnames[1:]

        for row in rows:
            paradigm_name = row[id_col].strip()
            if not paradigm_name:
                continue

            paradigm_names.add(paradigm_name)

            if paradigm_name not in paradigms_markers:
                paradigms_markers[paradigm_name] = {}

            for col in feature_cols:
                try:
                    val = row[col].strip()
                except Exception as e:
                    raise KeyError(
                        f"Column '{col}' not found in CSV file {csv_file}. Available columns: {fieldnames}"
                    ) from e
                if val or (val == "" and metadata.get("kind") != "rule"):
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

    return {
        "metadata": metadata,
        "class_feature": csv_class_feature,
        "paradigms_markers": paradigms_markers,
        "paradigm_names": paradigm_names,
    }


def reduce_csv_mappings(mapped_results):
    """
    Reduces and aggregates individual CSV mapping results into global maps of
    paradigm metadata, combined markers, and class-feature associations.

    This function represents the 'reduce' step. It takes the output list from the
    map stage and merges them, ensuring that if a paradigm is defined across multiple
    CSV files (e.g. suffix definitions and phonological/diphthong rules), their
    markers are correctly accumulated under the same paradigm entry.

    Args:
        mapped_results (list of dict): The list of results returned by map_csv_to_markers.

    Returns:
        tuple: A tuple containing:
            - paradigms_metadata (dict): Aggregated metadata for each paradigm.
            - paradigms_markers (dict): Aggregated, complete list of markers per feature per paradigm.
            - class_features_paradigms (dict): Map of class features (e.g., 'conjugation_class')
              to the set of paradigm names that belong to them.
    """
    paradigms_metadata = {}
    paradigms_markers = {}
    class_features_paradigms = {}

    for res in mapped_results:
        metadata = res["metadata"]
        csv_class_feature = res["class_feature"]
        file_paradigms_markers = res["paradigms_markers"]
        paradigm_names = res["paradigm_names"]

        if csv_class_feature:
            if csv_class_feature not in class_features_paradigms:
                class_features_paradigms[csv_class_feature] = set()

            for paradigm_name in paradigm_names:
                class_features_paradigms[csv_class_feature].add(paradigm_name)

                if paradigm_name not in paradigms_metadata:
                    paradigms_metadata[paradigm_name] = metadata.copy()

                if paradigm_name not in paradigms_markers:
                    paradigms_markers[paradigm_name] = {}

                # Merge markers for this paradigm from this file
                file_markers = file_paradigms_markers.get(paradigm_name, {})
                for col, entries in file_markers.items():
                    if col not in paradigms_markers[paradigm_name]:
                        paradigms_markers[paradigm_name][col] = []
                    paradigms_markers[paradigm_name][col].extend(entries)

    return paradigms_metadata, paradigms_markers, class_features_paradigms


def generate_paradigm_configs(
    paradigm_name,
    meta,
    markers,
    pos_name,
    output_dir,
    feature_markers_keys,
    filename_suffix_keys,
    stage_order,
):
    """
    Generates and saves the FeatureMarkers and Paradigm YAML configuration files
    for a specific paradigm.

    This function creates:
    1. A FeatureMarkers YAML file (located in Exponence/FeatureMarkers) containing the
       mappings of abstract features (like person/number) to concrete morphotactic markers.
    2. A Paradigm YAML file (located in Morphotactics/Paradigm) containing references
       to the FeatureMarkers, part of speech, lexical/class filters, and optional
       stage ordering requirements for phonological rule application.

    Args:
        paradigm_name (str): The identifier of the paradigm (e.g., 'ar_regular').
        meta (dict): Metadata associated with this paradigm.
        markers (dict): The feature-to-marker mappings for this paradigm.
        pos_name (str): The name of the part of speech (e.g., 'verb').
        output_dir (str): Path to the destination directory.
        feature_markers_keys (list): Configuration keys defining which metadata keys should
          be propagated as additional feature_markers.
        filename_suffix_keys (list): Configuration keys to extract suffixes for filenames.
        stage_order (list or None): Explicit execution order for morphological/phonological stages.
    """
    # Ensure it has correct prefix
    filename_base = paradigm_name
    if not filename_base.startswith(f"{pos_name}_"):
        filename_base = f"{pos_name}_{filename_base}"

    # 1. Generate FeatureMarker YAML
    fm_dir = os.path.join(output_dir, "Exponence", "FeatureMarkers")
    os.makedirs(fm_dir, exist_ok=True)
    fm_file = os.path.join(fm_dir, f"{filename_base}.yaml")

    markers_dict = {}
    all_cols = sorted(list(set(markers.keys())))

    for col in all_cols:
        entries = markers.get(col, [])
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
    paradigm_file = os.path.join(paradigm_dir, f"{filename_base}{suffix_str}.yaml")

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


def generate_standard_feature_markers(feature_name, pos_name, markers, output_dir):
    filename_base = f"{pos_name}_{feature_name}"
    fm_dir = os.path.join(output_dir, "Exponence", "FeatureMarkers")
    os.makedirs(fm_dir, exist_ok=True)
    fm_file = os.path.join(fm_dir, f"{filename_base}.yaml")

    fm_content = {
        "kind": "FeatureMarkers",
        "feature": feature_name,
        "markers": markers,
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
    return f"${filename_base}"


def generate_contingent_configs(
    mapped_results,
    pos_name,
    output_dir,
    stage_order,
):
    """
    Generates ContingentFeatureMarkers and standard FeatureMarkers,
    and a single unified Paradigm config when use_contingent_features is enabled.
    """
    contingent_results = [r for r in mapped_results if r["class_feature"] is not None]
    non_contingent_results = [r for r in mapped_results if r["class_feature"] is None]

    contingent_groups = {}
    for res in contingent_results:
        cf = res["class_feature"]
        feat = res["metadata"]["feature"]
        key = (cf, feat)
        if key not in contingent_groups:
            contingent_groups[key] = {}
        for paradigm_name, feature_markers in res["paradigms_markers"].items():
            if paradigm_name not in contingent_groups[key]:
                contingent_groups[key][paradigm_name] = {}
            for col, entries in feature_markers.items():
                if col not in contingent_groups[key][paradigm_name]:
                    contingent_groups[key][paradigm_name][col] = []
                contingent_groups[key][paradigm_name][col].extend(entries)

    contingent_files = []
    cfm_dir = os.path.join(output_dir, "Exponence", "ContingentFeatureMarkers")
    os.makedirs(cfm_dir, exist_ok=True)

    for (cf, feat), class_mappings in sorted(contingent_groups.items()):
        filename = f"{pos_name}_{feat}_contingent.yaml"
        cfm_file = os.path.join(cfm_dir, filename)

        # Sort class names and feature values to ensure deterministic output
        sorted_mappings = {}
        for c_name in sorted(class_mappings.keys()):
            sorted_mappings[c_name] = {}
            for f_val in sorted(class_mappings[c_name].keys()):
                sorted_mappings[c_name][f_val] = class_mappings[c_name][f_val]

        cfm_content = {
            "kind": "ContingentFeatureMarkers",
            "features": [cf, feat],
            "markers": sorted_mappings,
        }

        with open(cfm_file, "w", encoding="utf-8") as f:
            f.write("# This is a ContingentFeatureMarkers config file\n")
            f.write("# Generated automatically from CSVs\n")
            yaml.dump(
                cfm_content,
                f,
                Dumper=Dumper,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        print(f"Generated ContingentFeatureMarkers: {cfm_file}")
        contingent_files.append(f"${pos_name}_{feat}_contingent")

    # Generate standard FeatureMarkers for non-contingent features
    standard_feature_refs = {}
    for res in non_contingent_results:
        feat = res["metadata"]["feature"]
        markers = res["paradigms_markers"].get("", {})
        
        # Sort marker entries for determinism
        sorted_markers = {}
        for f_val in sorted(markers.keys()):
            sorted_markers[f_val] = markers[f_val]
            
        ref = generate_standard_feature_markers(feat, pos_name, sorted_markers, output_dir)
        standard_feature_refs[feat] = ref

    # Generate a single unified Paradigm config at Morphotactics/Paradigm/{pos_name}.yaml
    paradigm_dir = os.path.join(output_dir, "Morphotactics", "Paradigm")
    os.makedirs(paradigm_dir, exist_ok=True)
    paradigm_file = os.path.join(paradigm_dir, f"{pos_name}.yaml")

    features_in_contingent = sorted(
        list(set(feat for (cf, feat) in contingent_groups.keys()))
    )
    feature_markers = {feat: None for feat in features_in_contingent}
    
    # Merge standard non-contingent feature markers references
    for feat, ref in standard_feature_refs.items():
        feature_markers[feat] = ref

    paradigm_content = {
        "kind": "Paradigm",
        "part_of_speech": f"${pos_name}",
        "feature_markers": feature_markers,
        "contingent_markers": sorted(contingent_files),
    }
    if stage_order:
        paradigm_content["stage_order"] = stage_order

    with open(paradigm_file, "w", encoding="utf-8") as f:
        f.write("# This is a Paradigm config file\n")
        f.write("# Generated automatically from CSVs\n")
        yaml.dump(
            paradigm_content,
            f,
            Dumper=Dumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    print(f"Generated Paradigm: {paradigm_file}")


def update_feature_definitions(
    output_dir, pos_name, verb_config, class_features_paradigms, config_path=None
):
    """
    Updates the global FeatureDefinitions configuration file with the dynamically
    discovered class feature values (paradigms) and configured inflectional features.

    This ensures that the YAML configurations match schema specifications and that the
    underlying parser has a full index of valid inflectional categories and lexical
    class feature values.

    Args:
        output_dir (str): Path to the destination directory.
        pos_name (str): The part of speech name.
        verb_config (dict): Global configuration dictionary.
        class_features_paradigms (dict): Map of class features to set of paradigm values.
        config_path (str, optional): Path to the config directory.
    """
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
        # Load feature acceptors if feature_acceptors subfolder exists in config_path
        feature_acceptors = {}
        if config_path and os.path.isdir(config_path):
            fa_dir = os.path.join(config_path, "feature_acceptors")
            if os.path.exists(fa_dir) and os.path.isdir(fa_dir):
                for filename in os.listdir(fa_dir):
                    if filename.endswith(".csv"):
                        fa_file = os.path.join(fa_dir, filename)
                        metadata, fieldnames, rows = parse_csv_with_metadata(fa_file)

                        feature_name = metadata.get("feature") or (
                            fieldnames[0] if fieldnames else None
                        )
                        fa_pos = metadata.get("part_of_speech")
                        if fa_pos:
                            fa_pos = fa_pos.lstrip("$")

                        # Only apply acceptors for the current POS
                        if fa_pos and fa_pos != pos_name:
                            continue

                        if not feature_name or len(fieldnames) < 2:
                            continue

                        val_col = fieldnames[0]
                        acc_col = fieldnames[1]

                        if feature_name not in feature_acceptors:
                            feature_acceptors[feature_name] = {}

                        for row in rows:
                            val = row.get(val_col, "").strip()
                            acc = row.get(acc_col, "").strip()
                            if val and acc:
                                feature_acceptors[feature_name][val] = acc

        # Add inflectional features from verb.yaml
        if "features" in verb_config:
            for feat, vals in verb_config["features"].items():
                fd_content["features"][feat] = vals

        # Add lexical features with definitions from verb.yaml
        if "lexical_features" in verb_config:
            for item in verb_config["lexical_features"]:
                if isinstance(item, dict):
                    if len(item) == 1:
                        feat = list(item.keys())[0]
                        definition = item[feat]
                        fd_content["features"][feat] = definition
                    else:
                        none_keys = [k for k, v in item.items() if v is None]
                        if none_keys:
                            feat = none_keys[0]
                            definition = {k: v for k, v in item.items() if k != feat}
                            fd_content["features"][feat] = definition


        # Combine only features that are dynamically updated (class features or feature acceptors)
        update_targets = set(class_features_paradigms.keys()) | set(
            feature_acceptors.keys()
        )

        for cf in update_targets:
            if cf not in fd_content["features"]:
                fd_content["features"][cf] = []
            
            is_dict = isinstance(fd_content["features"][cf], dict) and "values" in fd_content["features"][cf]
            if is_dict:
                cc_list = fd_content["features"][cf]["values"]
            else:
                cc_list = fd_content["features"][cf]
                if not isinstance(cc_list, list):
                    cc_list = []

            # Build map of existing values: name -> item (string or dict)
            existing_map = {}
            for item in cc_list:
                if isinstance(item, dict) and "name" in item:
                    existing_map[item["name"]] = item
                elif isinstance(item, str):
                    existing_map[item] = item

            # Add new dynamically discovered class feature values
            if cf in class_features_paradigms:
                for cc in class_features_paradigms[cf]:
                    if cc not in existing_map:
                        existing_map[cc] = cc

            # Apply/merge feature acceptors
            if cf in feature_acceptors:
                for name, acc in feature_acceptors[cf].items():
                    existing_map[name] = {"name": name, "acceptor": acc}

            # Reconstruct list sorted by name/string value
            sorted_names = sorted(list(existing_map.keys()))
            new_cc_list = []
            for name in sorted_names:
                new_cc_list.append(existing_map[name])

            if is_dict:
                fd_content["features"][cf]["values"] = new_cc_list
            else:
                fd_content["features"][cf] = new_cc_list

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


def generate_part_of_speech_config(output_dir, pos_name, verb_config):
    """
    Generates the PartOfSpeech YAML configuration file for the language parser.

    This configuration specifies the name of the part of speech, lists its relevant
    grammatical features, and includes any other structural/lexical features
    defined in the config.

    Args:
        output_dir (str): Path to the destination directory.
        pos_name (str): The part of speech name.
        verb_config (dict): Global configuration dictionary.
    """
    pos_dir = os.path.join(output_dir, "Lexicon", "PartOfSpeech")
    os.makedirs(pos_dir, exist_ok=True)
    pos_file = os.path.join(pos_dir, f"{pos_name}.yaml")

    pos_content = {
        "kind": "PartOfSpeech",
        "name": pos_name,
        "features": list(verb_config.get("features", {}).keys()),
    }
    if "lexical_features" in verb_config:
        simplified_lexical_features = []
        for item in verb_config["lexical_features"]:
            if isinstance(item, dict):
                if len(item) == 1:
                    simplified_lexical_features.append(list(item.keys())[0])
                else:
                    none_keys = [k for k, v in item.items() if v is None]
                    if none_keys:
                        simplified_lexical_features.append(none_keys[0])
                    else:
                        simplified_lexical_features.append(list(item.keys())[0])
            else:
                simplified_lexical_features.append(item)
        pos_content["lexical_features"] = simplified_lexical_features


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


def main():
    """
    Main entry point for generator. Orchestrates loading base configurations,
    mapping CSV files to individual paradigm metadata/markers, reducing those mapping results,
    generating FeatureMarkers and Paradigm configs, and writing global definitions.
    """
    if len(sys.argv) < 3:
        print(
            "Usage: python generate_markers.py <path_to_config_dir_or_csv> <output_dir>"
        )
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(config_path):
        print(f"Error: Config path not found at {config_path}")
        sys.exit(1)

    # Clean output_dir
    if os.path.exists(output_dir):
        for subdir in os.listdir(output_dir):
            if not subdir == ".cache":
                shutil.rmtree(output_dir + "/" + subdir)
    os.makedirs(output_dir, exist_ok=True)

    # Ensure full standard directory structure exists under output_dir
    standard_dirs = [
        os.path.join(output_dir, "Phonology", "Inventory"),
        os.path.join(output_dir, "Phonology", "Patterns"),
        os.path.join(output_dir, "Phonology", "Rules"),
        os.path.join(output_dir, "Exponence", "FeatureDefinitions"),
        os.path.join(output_dir, "Exponence", "FeatureMarkers"),
        os.path.join(output_dir, "Exponence", "ContingentFeatureMarkers"),
        os.path.join(output_dir, "Lexicon", "PartOfSpeech"),
        os.path.join(output_dir, "Lexicon", "Wordlists"),
        os.path.join(output_dir, "Morphotactics", "Paradigm"),
    ]
    for d in standard_dirs:
        os.makedirs(d, exist_ok=True)

    # Copy wordlists from config/wordlists to output_dir/Lexicon/Wordlists if present
    if os.path.isdir(config_path):
        wordlists_dir = os.path.join(config_path, "wordlists")
        if os.path.exists(wordlists_dir) and os.path.isdir(wordlists_dir):
            dest_wl_dir = os.path.join(output_dir, "Lexicon", "Wordlists")
            for item in os.listdir(wordlists_dir):
                s = os.path.join(wordlists_dir, item)
                d = os.path.join(dest_wl_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

    # Copy Phonology from config/Phonology to output_dir/Phonology if present
    if os.path.isdir(config_path):
        phonology_dir = os.path.join(config_path, "Phonology")
        if os.path.exists(phonology_dir) and os.path.isdir(phonology_dir):
            dest_phonology = os.path.join(output_dir, "Phonology")
            if os.path.exists(dest_phonology):
                shutil.rmtree(dest_phonology)
            shutil.copytree(phonology_dir, dest_phonology)

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
    if spec_path and os.path.exists(spec_path):
        with open(spec_path, "r", encoding="utf-8") as f:
            verb_config = yaml.safe_load(f) or {}
            if "order" in verb_config:
                stage_order = verb_config["order"]
            elif "stages" in verb_config:
                stage_order = verb_config["stages"]
    else:
        raise ValueError("Configuration file is required but not found.")

    paradigm_config = verb_config.get("paradigm", {})
    feature_markers_keys = paradigm_config.get("feature_markers_keys", [])
    filename_suffix_keys = paradigm_config.get("filename_suffix_keys", [])

    # Map Step: Parse each CSV file and extract paradigm markers
    mapped_results = [map_csv_to_markers(csv_file) for csv_file in csv_files]

    # Reduce Step: Aggregate paradigm metadata, markers, and class associations
    paradigms_metadata, paradigms_markers, class_features_paradigms = (
        reduce_csv_mappings(mapped_results)
    )

    # Always ensure Exponence/FeatureMarkers directory exists for parC compatibility
    os.makedirs(os.path.join(output_dir, "Exponence", "FeatureMarkers"), exist_ok=True)

    use_contingent_features = paradigm_config.get(
        "generate_contingent_markers", False
    ) or paradigm_config.get("use_contingent_features", False)

    # Output paradigm files
    if use_contingent_features:
        generate_contingent_configs(
            mapped_results=mapped_results,
            pos_name=pos_name,
            output_dir=output_dir,
            stage_order=stage_order,
        )

    else:
        for paradigm_name, meta in paradigms_metadata.items():
            markers = paradigms_markers.get(paradigm_name, {})
            generate_paradigm_configs(
                paradigm_name=paradigm_name,
                meta=meta,
                markers=markers,
                pos_name=pos_name,
                output_dir=output_dir,
                feature_markers_keys=feature_markers_keys,
                filename_suffix_keys=filename_suffix_keys,
                stage_order=stage_order,
            )

    # Update global FeatureDefinitions configuration
    update_feature_definitions(
        output_dir=output_dir,
        pos_name=pos_name,
        verb_config=verb_config,
        class_features_paradigms=class_features_paradigms,
        config_path=config_path,
    )

    # Generate PartOfSpeech configuration
    generate_part_of_speech_config(
        output_dir=output_dir,
        pos_name=pos_name,
        verb_config=verb_config,
    )


if __name__ == "__main__":
    main()
