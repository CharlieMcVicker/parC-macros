#!/usr/bin/env python3
import csv
import os
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
        'feature': 'person_number'
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
                # Map alternate names
                if key in ('operation', 'kind'):
                    metadata['kind'] = val
                elif key in ('phase', 'stage'):
                    metadata['stage'] = val
                elif key == 'feature':
                    metadata['feature'] = val
        else:
            csv_lines.append(line)
            
    reader = csv.DictReader(csv_lines)
    for row in reader:
        rows.append(row)
        
    return metadata, reader.fieldnames, rows

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_markers.py <path_to_csv> <output_dir>")
        sys.exit(1)
        
    csv_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    
    metadata, fieldnames, rows = parse_csv_with_metadata(csv_path)
    
    # First column is the identifier for the row / paradigm
    id_col = fieldnames[0]
    feature_cols = fieldnames[1:]
    
    for row in rows:
        paradigm_name = row[id_col].strip()
        if not paradigm_name:
            continue
            
        # Ensure it has 'verb_' prefix to match existing filenames if needed
        filename_base = paradigm_name
        if not filename_base.startswith('verb_'):
            filename_base = f"verb_{filename_base}"
            
        output_file = os.path.join(output_dir, f"{filename_base}.yaml")
        
        # Build markers dictionary
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
                
        yaml_content = {
            'kind': 'FeatureMarkers',
            'feature': metadata['feature'],
            'markers': markers_dict
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# This is a FeatureMarkers config file\n")
            f.write("# Generated automatically from CSV\n")
            # Sort keys is false by default or sorted for determinism
            yaml.dump(yaml_content, f, Dumper=Dumper, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
        print(f"Generated: {output_file}")

if __name__ == '__main__':
    main()
