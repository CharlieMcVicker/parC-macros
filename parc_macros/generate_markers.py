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
        print("Usage: python generate_markers.py <path_to_csv> <base_dir> <output_dir>")
        sys.exit(1)
        
    csv_path = sys.argv[1]
    base_dir = sys.argv[2]
    output_dir = sys.argv[3]
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
        
    if not os.path.exists(base_dir):
        print(f"Error: Base directory not found at {base_dir}")
        sys.exit(1)
        
    # Copy base_dir to output_dir
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    shutil.copytree(base_dir, output_dir)
    
    metadata, fieldnames, rows = parse_csv_with_metadata(csv_path)
    
    # First column is the identifier for the row / paradigm
    id_col = fieldnames[0]
    feature_cols = fieldnames[1:]
    
    new_conjugation_classes = []
    
    for row in rows:
        paradigm_name = row[id_col].strip()
        if not paradigm_name:
            continue
            
        new_conjugation_classes.append(paradigm_name)
        
        # Ensure it has 'verb_' prefix
        filename_base = paradigm_name
        if not filename_base.startswith('verb_'):
            filename_base = f"verb_{filename_base}"
            
        # 1. Generate FeatureMarker YAML
        fm_dir = os.path.join(output_dir, "Exponence", "FeatureMarkers")
        os.makedirs(fm_dir, exist_ok=True)
        fm_file = os.path.join(fm_dir, f"{filename_base}.yaml")
        
        markers_dict = {}
        for col in feature_cols:
            val = row[col].strip()
            if val:
                markers_dict[col] = [
                    {
                        'kind': metadata['kind'],
                        'value': val,
                        'stage': metadata['stage']
                    }
                ]
            else:
                markers_dict[col] = None
                
        fm_content = {
            'kind': 'FeatureMarkers',
            'feature': metadata['feature'],
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
        paradigm_file = os.path.join(paradigm_dir, f"{filename_base}_{metadata['tense']}.yaml")
        
        paradigm_content = {
            'kind': 'Paradigm',
            'part_of_speech': metadata['part_of_speech'],
            'feature_markers': {
                metadata['feature']: f"${filename_base}",
                'tense': metadata['tense'],
                'mood': metadata['mood']
            },
            'filter': {
                'lexical_features': {
                    'conjugation_class': paradigm_name
                }
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
            
        if fd_content and 'features' in fd_content and 'conjugation_class' in fd_content['features']:
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

if __name__ == '__main__':
    main()
