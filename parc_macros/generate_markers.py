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
    metadata = {
        'kind': 'suffix',
        'stage': 'suffix',
        'feature': 'person_number',
        'part_of_speech': '$verb',
        'tense': 'present',
        'mood': 'indicative'
    }
    rows = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    csv_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            # Parse metadata comment, e.g. "# kind: suffix" or "# stage: suffix"
            comment_content = stripped[1:].strip()
            if ':' in comment_content:
                key, val = comment_content.split(':', 1)
                key = key.strip().lower()
                val = val.strip()
                # Map keys
                if key in ('operation', 'kind'):
                    metadata['kind'] = val
                elif key in ('phase', 'stage'):
                    metadata['stage'] = val
                elif key == 'feature':
                    metadata['feature'] = val
                elif key == 'rule':
                    metadata['rule'] = val
                elif key == 'part_of_speech':
                    metadata['part_of_speech'] = val
                elif key == 'tense':
                    metadata['tense'] = val
                elif key == 'mood':
                    metadata['mood'] = val
        else:
            csv_lines.append(line)
            
    reader = csv.DictReader(csv_lines)
    for row in reader:
        rows.append(row)
        
    return metadata, reader.fieldnames, rows

def main():
    if len(sys.argv) < 4:
        print("Usage: python generate_markers.py <path_to_config_dir_or_csv> <base_dir> <output_dir>")
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
            if f.endswith('.csv'):
                csv_files.append(os.path.join(config_path, f))
            elif f == 'verb.yaml':
                spec_path = os.path.join(config_path, f)
            elif f == 'verb_spec.yaml' and not spec_path:
                spec_path = os.path.join(config_path, f)
    else:
        # Fallback to single csv compatibility
        csv_files.append(config_path)
        # Try to look for verb.yaml or verb_spec.yaml in the same directory
        parent_dir = os.path.dirname(config_path)
        possible_spec = os.path.join(parent_dir, 'verb.yaml')
        if os.path.exists(possible_spec):
            spec_path = possible_spec
        else:
            possible_spec = os.path.join(parent_dir, 'verb_spec.yaml')
            if os.path.exists(possible_spec):
                spec_path = possible_spec

    # Load verb.yaml / verb_spec.yaml if it exists
    stage_order = None
    verb_config = {}
    if spec_path and os.path.exists(spec_path):
        with open(spec_path, 'r', encoding='utf-8') as f:
            verb_config = yaml.safe_load(f) or {}
            if 'order' in verb_config:
                stage_order = verb_config['order']
            elif 'stages' in verb_config:
                stage_order = verb_config['stages']

    # We will gather all paradigms, and all markers for each paradigm
    # Structure:
    # paradigms_metadata = { paradigm_name: { 'part_of_speech': ..., 'tense': ..., 'mood': ..., 'feature': ... } }
    # paradigms_markers = { paradigm_name: { feature_value: [ {kind, value, stage}, ... ] } }
    paradigms_metadata = {}
    paradigms_markers = {}

    for csv_file in csv_files:
        metadata, fieldnames, rows = parse_csv_with_metadata(csv_file)
        id_col = fieldnames[0]
        feature_cols = fieldnames[1:]

        for row in rows:
            paradigm_name = row[id_col].strip()
            if not paradigm_name:
                continue

            if paradigm_name not in paradigms_metadata:
                paradigms_metadata[paradigm_name] = {
                    'part_of_speech': metadata['part_of_speech'],
                    'tense': metadata['tense'],
                    'mood': metadata['mood'],
                    'feature': metadata['feature']
                }

            if paradigm_name not in paradigms_markers:
                paradigms_markers[paradigm_name] = {}

            for col in feature_cols:
                val = row[col].strip()
                if val:
                    # If kind is rule and a rule name is specified in metadata:
                    # Y means we use the rule name from metadata. N or empty means no entry.
                    if metadata.get('kind') == 'rule' and 'rule' in metadata:
                        if val.upper() == 'Y':
                            val = metadata['rule']
                        else:
                            # Skip N or empty
                            continue
                            
                    marker_entry = {
                        'kind': metadata['kind'],
                        'value': val,
                        'stage': metadata['stage']
                    }
                    if col not in paradigms_markers[paradigm_name]:
                        paradigms_markers[paradigm_name][col] = []
                    paradigms_markers[paradigm_name][col].append(marker_entry)

    new_conjugation_classes = list(paradigms_metadata.keys())

    # Write the config files for each paradigm
    for paradigm_name, meta in paradigms_metadata.items():
        # Ensure it has 'verb_' prefix
        filename_base = paradigm_name
        if not filename_base.startswith('verb_'):
            filename_base = f"verb_{filename_base}"

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
        standard_cols = ['1sg', '2sg', '3sg', '1pl', '2pl', '3pl']
        all_cols = sorted(list(set(standard_cols + list(paradigms_markers[paradigm_name].keys()))))

        for col in all_cols:
            entries = paradigms_markers[paradigm_name].get(col, [])
            if entries:
                markers_dict[col] = entries
            else:
                markers_dict[col] = None

        fm_content = {
            'kind': 'FeatureMarkers',
            'feature': meta['feature'],
            'markers': markers_dict
        }

        with open(fm_file, 'w', encoding='utf-8') as f:
            f.write("# This is a FeatureMarkers config file\n")
            f.write("# Generated automatically from CSV\n")
            yaml.dump(fm_content, f, Dumper=Dumper, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"Generated FeatureMarkers: {fm_file}")

        # 2. Generate Paradigm YAML
        paradigm_dir = os.path.join(output_dir, "Morphotactics", "Paradigm")
        os.makedirs(paradigm_dir, exist_ok=True)
        paradigm_file = os.path.join(paradigm_dir, f"{filename_base}_{meta['tense']}.yaml")

        paradigm_content = {
            'kind': 'Paradigm',
            'part_of_speech': meta['part_of_speech'],
            'feature_markers': {
                meta['feature']: f"${filename_base}",
                'tense': meta['tense'],
                'mood': meta['mood']
            }
        }

        # Add stage_order if defined and this paradigm has markers in multiple stages
        # Or should we only add it if the paradigm has markers spanning multiple stages?
        # Let's count how many distinct stages are actually used in markers_dict for this paradigm.
        used_stages = set()
        for col, entries in markers_dict.items():
            if entries:
                for entry in entries:
                    if 'stage' in entry:
                        used_stages.add(entry['stage'])
        
        if stage_order and len(used_stages) > 1:
            paradigm_content['stage_order'] = stage_order

        # Add filter
        paradigm_content['filter'] = {
            'lexical_features': {
                'conjugation_class': paradigm_name
            }
        }

        with open(paradigm_file, 'w', encoding='utf-8') as f:
            f.write("# This is a Paradigm config file\n")
            f.write("# Generated automatically from CSV\n")
            yaml.dump(paradigm_content, f, Dumper=Dumper, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"Generated Paradigm: {paradigm_file}")

    # 3. Update Exponence/FeatureDefinitions/verb_features.yaml
    fd_file = os.path.join(output_dir, "Exponence", "FeatureDefinitions", "verb_features.yaml")
    if os.path.exists(fd_file):
        with open(fd_file, 'r', encoding='utf-8') as f:
            fd_content = yaml.safe_load(f)
    else:
        fd_content = {
            'kind': 'FeatureDefinitions',
            'features': {
                'conjugation_class': []
            }
        }
        os.makedirs(os.path.dirname(fd_file), exist_ok=True)
            
    if fd_content and 'features' in fd_content:
        # Add inflectional features from verb.yaml
        if 'features' in verb_config:
            for feat, vals in verb_config['features'].items():
                fd_content['features'][feat] = vals
        
        # Update conjugation_class
        if 'conjugation_class' in fd_content['features']:
            cc_list = fd_content['features']['conjugation_class']
            if not isinstance(cc_list, list):
                cc_list = []
            for cc in new_conjugation_classes:
                if cc not in cc_list:
                    cc_list.append(cc)
            fd_content['features']['conjugation_class'] = cc_list
        
        with open(fd_file, 'w', encoding='utf-8') as f:
            f.write("# This is a FeatureDefinitions config file\n")
            f.write("# Generated/Updated automatically from CSV\n")
            yaml.dump(fd_content, f, Dumper=Dumper, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
        print(f"Updated FeatureDefinitions: {fd_file}")

    # 4. Generate Lexicon/PartOfSpeech/verb.yaml
    pos_dir = os.path.join(output_dir, "Lexicon", "PartOfSpeech")
    os.makedirs(pos_dir, exist_ok=True)
    pos_file = os.path.join(pos_dir, "verb.yaml")
    
    pos_content = {
        'kind': 'PartOfSpeech',
        'name': 'verb',
        'features': list(verb_config.get('features', {}).keys())
    }
    if 'lexical_features' in verb_config:
        pos_content['lexical_features'] = verb_config['lexical_features']
        
    with open(pos_file, 'w', encoding='utf-8') as f:
        f.write("# This is a PartOfSpeech config file\n")
        f.write("# Generated automatically from config/verb.yaml\n")
        yaml.dump(pos_content, f, Dumper=Dumper, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Generated PartOfSpeech: {pos_file}")

if __name__ == '__main__':
    main()
