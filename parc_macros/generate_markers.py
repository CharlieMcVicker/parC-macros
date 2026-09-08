import sys
from pathlib import Path
_root = str(Path(__file__).parent.parent.resolve())
if _root not in sys.path:
    sys.path.insert(0, _root)
#!/usr/bin/env python3
import csv
import os
import shutil
import sys
import yaml
import re
from typing import Any
from parc_macros.generate_insertion_rules import generate_insertion_rules
from parc_macros.generate_morpheme_replace_rules import (
    generate_morpheme_replace_rules,
    sanitize_rule_name,
)


def derive_open_root_template(verb_config: dict[str, Any]) -> str:
    """
    Derives the full open root template from slot spec and template definition.

    If open_root_template is already explicitly present in verb_config.get("paradigm", {}),
    returns it (for backwards compatibility with fixtures like min-min-config).
    Otherwise, reads template from paradigm (or top-level) and expands each slot
    into its constituent <TagGroup> patterns defined in slots.
    """
    paradigm_config = verb_config.get("paradigm", {})
    if paradigm_config.get("open_root_template"):
        return paradigm_config["open_root_template"]
    if verb_config.get("open_root_template"):
        return verb_config["open_root_template"]

    template = paradigm_config.get("template") or verb_config.get("template")
    if not template:
        return ""

    slots = verb_config.get("slots", []) or paradigm_config.get("slots", [])
    slots_by_name = {s["name"]: s for s in slots if "name" in s}

    expanded = []
    for el in template:
        if el.startswith("slot:"):
            slot_name = el[5:]
        elif el in slots_by_name:
            slot_name = el
        else:
            slot_name = None

        if slot_name and slot_name in slots_by_name:
            for comp in slots_by_name[slot_name].get("structure", []):
                expanded.append(f"<{comp['TagGroup']}>")
        else:
            expanded.append(el)

    return "".join(expanded)


import parc_macros.generate_phonology as gp



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

    if not metadata.get("kind"):
        return {
            "metadata": metadata,
            "class_feature": None,
            "paradigms_markers": {},
            "paradigm_names": set(),
        }

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
                if val or (val == "" and metadata.get("kind") not in ("rule",)):
                    if metadata.get("kind") == "rule" and "rule" in metadata:
                        if val.upper() == "Y":
                            val = metadata["rule"]
                        else:
                            continue
                    
                    if metadata.get("kind") == "morpheme_replace":
                        morpheme_tag = metadata.get("morpheme_tag", "[Pro]")
                        tag_slug = morpheme_tag.replace("[", "").replace("]", "").lower()
                        rule_name = f"{tag_slug}_{sanitize_rule_name(val)}"
                        marker_entry = {
                            "kind": "rule",
                            "value": f"${rule_name}",
                            "stage": metadata["stage"],
                        }
                    else:
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
                if val or (val == "" and metadata.get("kind") not in ("rule",)):
                    # If kind is rule and a rule name is specified in metadata:
                    # Y means we use the rule name from metadata. N or empty means no entry.
                    if metadata.get("kind") == "rule" and "rule" in metadata:
                        if val.upper() == "Y":
                            val = metadata["rule"]
                        else:
                            # Skip N or empty
                            continue

                    if metadata.get("kind") == "morpheme_replace":
                        morpheme_tag = metadata.get("morpheme_tag", "[Pro]")
                        tag_slug = morpheme_tag.replace("[", "").replace("]", "").lower()
                        rule_name = f"{tag_slug}_{sanitize_rule_name(val)}"
                        marker_entry = {
                            "kind": "rule",
                            "value": f"${rule_name}",
                            "stage": metadata["stage"],
                        }
                    else:
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



def generate_paradigm_config(
    pos_name,
    verb_config,
    stage_order,
    mapped_results,
    output_dir,
    open_root_template,
    template=None,
):
    """
    Generates a lean unified Paradigm config using global_markers without ContingentFeatureMarkers.
    """
    paradigm_config = verb_config.get("paradigm", {})
    paradigm_dir = os.path.join(output_dir, "Morphotactics", "Paradigm")
    os.makedirs(paradigm_dir, exist_ok=True)
    paradigm_file = os.path.join(paradigm_dir, f"{pos_name}.yaml")

    # If global_markers is explicitly configured in verb.yaml, use it
    if "global_markers" in paradigm_config:
        raw_gm = paradigm_config["global_markers"]
        global_markers = []
        for item in raw_gm:
            m = dict(item)
            if "kind" not in m and str(m.get("value", "")).startswith("$"):
                m["kind"] = "rule"
            global_markers.append(m)
    else:
        # Map of stage -> rule value
        stage_to_rule = {}
        for res in mapped_results:
            meta = res.get("metadata", {})
            stg = meta.get("stage")
            if not stg:
                continue
            if meta.get("kind") == "morpheme_replace":
                morpheme_tag = meta.get("morpheme_tag", "")
                tag_slug = re.sub(r"[\[\]]", "", morpheme_tag).lower()
                stage_to_rule[stg] = f"${tag_slug}_replace"
            elif meta.get("rule"):
                r = meta["rule"]
                if not r.startswith("$"):
                    r = f"${r}"
                stage_to_rule[stg] = r

        # Default rules for well-known stages
        standard_stage_rules = {
            "final_dropping": "$drop_root_final",
            "drop_stem_initial_vowel": "$drop_stem_initial_vowel",
            "h_alternation": "$h_alternation",
            "insert_dist": "$insert_di",
            "insert_wi": "$insert_wi",
        }
        for stg, r in standard_stage_rules.items():
            if stg not in stage_to_rule:
                stage_to_rule[stg] = r

        # Check existing rules in output_dir/Phonology/Rules
        rules_dir = os.path.join(output_dir, "Phonology", "Rules")
        if os.path.exists(rules_dir):
            available_rules = set()
            for rf in os.listdir(rules_dir):
                if rf.endswith(".yaml"):
                    r_path = os.path.join(rules_dir, rf)
                    try:
                        with open(r_path, "r", encoding="utf-8") as f:
                            r_data = yaml.safe_load(f) or {}
                            for r in r_data.get("rules", []):
                                if "name" in r:
                                    available_rules.add(r["name"])
                    except Exception:
                        pass
            preferred_stage_rules = {
                "final_dropping": "drop_root_final",
                "drop_stem_initial_vowel": "drop_stem_initial_vowel",
                "h_alternation": "h_alternation",
            }
            for stg, pref in preferred_stage_rules.items():
                if pref in available_rules:
                    stage_to_rule[stg] = "$" + pref

            # Bridge case differences for insert_dist / insert_DIST
            if "insert_DIST" in stage_to_rule and "insert_dist" not in stage_to_rule:
                stage_to_rule["insert_dist"] = stage_to_rule["insert_DIST"]
            elif "insert_dist" in stage_to_rule and "insert_DIST" not in stage_to_rule:
                stage_to_rule["insert_DIST"] = stage_to_rule["insert_dist"]

            for candidate in ("insert_DIST", "insert_di", "insert_DIST1", "insert_di1"):
                if candidate in available_rules:
                    stage_to_rule["insert_dist"] = f"${candidate}"
                    stage_to_rule["insert_DIST"] = f"${candidate}"
                    break
            if "insert_wi" not in available_rules and "insert_WI" in available_rules:
                stage_to_rule["insert_wi"] = "$insert_WI"
                stage_to_rule["insert_WI"] = "$insert_WI"

        global_markers = []
        if stage_order:
            for stg in stage_order:
                if stg in stage_to_rule:
                    global_markers.append({
                        "kind": "rule",
                        "stage": stg,
                        "value": stage_to_rule[stg],
                    })

    paradigm_content = {
        "kind": "Paradigm",
        "part_of_speech": f"${pos_name}",
    }
    if stage_order:
        paradigm_content["stage_order"] = stage_order

    paradigm_content["global_markers"] = global_markers

    if open_root_template:
        paradigm_content["open_root_template"] = open_root_template

    if template is None:
        template = paradigm_config.get("template") or verb_config.get("template")
    if template:
        paradigm_content["template"] = template

    slots = verb_config.get("slots") or paradigm_config.get("slots")
    if slots:
        paradigm_content["slots"] = slots

    with open(paradigm_file, "w", encoding="utf-8") as f:
        f.write("# This is a Paradigm config file\n")
        f.write("# Generated automatically from CSVs (in-place morphemes)\n")
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
    Updates the global FeatureDefinitions configuration file with configured inflectional features.

    This ensures that the YAML configurations match schema specifications and that the
    underlying parser has a full index of valid inflectional categories.

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
                if isinstance(vals, dict) and "values" in vals:
                    fd_content["features"][feat] = vals["values"]
                else:
                    fd_content["features"][feat] = vals

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

    This configuration specifies the name of the part of speech and lists its relevant
    grammatical features.

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


def generate_markers(config_path: str, output_dir: str) -> None:
    """
    Main orchestrator for generating marker and paradigm configs from CSVs.
    """
    if not os.path.exists(config_path):
        print(f"Error: Config path not found at {config_path}")
        sys.exit(1)

    # Clean output_dir
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            if item != ".cache":
                item_path = os.path.join(output_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
    os.makedirs(output_dir, exist_ok=True)

    # Ensure full standard directory structure exists under output_dir
    standard_dirs = [
        os.path.join(output_dir, ".cache"),
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

    # Copy feature_acceptors from config/feature_acceptors to output_dir/feature_acceptors if present
    if os.path.isdir(config_path):
        fa_dir = os.path.join(config_path, "feature_acceptors")
        if os.path.exists(fa_dir) and os.path.isdir(fa_dir):
            dest_fa = os.path.join(output_dir, "feature_acceptors")
            if os.path.exists(dest_fa):
                shutil.rmtree(dest_fa)
            shutil.copytree(fa_dir, dest_fa)

    # Determine all CSVs and verb.yaml
    csv_files = []
    spec_path = None
    if os.path.isdir(config_path):
        for f in os.listdir(config_path):
            if f.endswith(".csv"):
                if f.endswith("_effects.csv") or f.endswith("-effects.csv"):
                    continue
                csv_files.append(os.path.join(config_path, f))
            elif f == "verb.yaml":
                spec_path = os.path.join(config_path, f)
            elif f == "verb_spec.yaml" and not spec_path:
                spec_path = os.path.join(config_path, f)
    else:
        # Fallback to single csv compatibility
        csv_files.append(config_path)
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

    # Phonology setup: dynamic generation
    cfg_p = Path(config_path)
    out_p = Path(output_dir)
    phonology_data = gp.extract_phonology_data(cfg_p, verb_config=verb_config)
    gp.generate_alphabet(
        cfg_p / "Phonology" / "Inventory" / "alphabet.yaml",
        out_p / "Phonology" / "Inventory" / "alphabet.yaml",
        phonology_data,
    )
    gp.generate_patterns(
        cfg_p / "Phonology" / "Patterns" / "phoneme_groups.yaml",
        out_p / "Phonology" / "Patterns" / "phoneme_groups.yaml",
        phonology_data,
    )
    gp.generate_phonology_rules(
        cfg_p,
        out_p / "Phonology" / "Rules",
        phonology_data,
    )
    gp.generate_slots_manifest(
        out_p / "slots.json",
        verb_config,
    )

    # Generate insertion rules and morpheme replace rules
    if os.path.isdir(config_path):
        generate_insertion_rules(config_path, output_dir)
        generate_morpheme_replace_rules(config_path, output_dir, verb_config=verb_config)

    # Identify optional features and modify verb_config['features']
    optional_features = []
    if "features" in verb_config:
        for feat_name, feat_def in verb_config["features"].items():
            if isinstance(feat_def, dict) and feat_def.get("optional") is True:
                optional_features.append(feat_name)
                if "values" in feat_def:
                    if "UNMARKED" not in feat_def["values"]:
                        feat_def["values"].append("UNMARKED")

    # Map Step: Parse each CSV file and extract paradigm markers
    mapped_results = [map_csv_to_markers(csv_file) for csv_file in csv_files]
    mapped_results = [
        r for r in mapped_results if not r["metadata"].get("inactive", False)
    ]

    # Reduce Step: Aggregate paradigm metadata, markers, and class associations
    paradigms_metadata, paradigms_markers, class_features_paradigms = (
        reduce_csv_mappings(mapped_results)
    )

    # Always ensure Exponence/FeatureMarkers directory exists for parC compatibility
    os.makedirs(os.path.join(output_dir, "Exponence", "FeatureMarkers"), exist_ok=True)

    open_root_template = derive_open_root_template(verb_config)
    template = paradigm_config.get("template") or verb_config.get("template")

    # Output paradigm file
    generate_paradigm_config(
        pos_name=pos_name,
        verb_config=verb_config,
        stage_order=stage_order,
        mapped_results=mapped_results,
        output_dir=output_dir,
        open_root_template=open_root_template,
        template=template,
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


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_markers.py <path_to_config_dir_or_csv> <output_dir>")
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir = sys.argv[2]
    generate_markers(config_path, output_dir)


if __name__ == "__main__":
    main()
