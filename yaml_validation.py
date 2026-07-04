"""
YAML Validation utility for parC configuration files.
Uses JSON schemas located in the schemas/ directory to validate YAML outputs.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
from loguru import logger
from frozendict import frozendict

SCHEMA_DIR = Path(__file__).parent / "schemas"

def get_referenced_content(ref_file_path: Path, object_path: str) -> tuple[dict, str]:
    # JSON path should be in the format "definitions/{OBJECT_NAME}"
    path_parts = object_path.strip("/").split("/")
    assert (
        len(path_parts) == 2 and path_parts[0] == "definitions"
    ), "Only references to definitions are supported"
    definitions_key, object_name = path_parts

    if not ref_file_path.exists():
        raise FileNotFoundError(
            f"Referenced schema file not found: {ref_file_path}")

    with open(ref_file_path, "r", encoding="utf-8") as f:
        ref_content = json.load(f)
    content = ref_content.get(definitions_key, {}).get(object_name, None)
    if content is None:
        raise ValueError(
            f"Referenced object '{object_name}' not found in '{ref_file_path}'"
        )
    return content, object_name

def fix_refs_safe(schema: dict, schema_dir: Path) -> dict:
    """
    Safely resolves external $ref in a JSON schema by copying the
    referenced content directly into the schema definitions and
    changing the $ref to a local reference. Avoids RecursionError.
    """
    node_stack = [schema]
    inserted_content = {}

    while node_stack:
        current_node = node_stack.pop()
        if isinstance(current_node, (dict, frozendict)):
            node_stack.extend(current_node.values())

            if "$ref" in current_node:
                ref_path = current_node["$ref"]
                if ref_path.startswith("#"):
                    continue  # Local reference, skip
                
                if "#" in ref_path:
                    rel_path, object_path = ref_path.split("#")
                else:
                    rel_path = ref_path
                    object_path = "definitions" # fallback

                ref_file_path = schema_dir / rel_path

                # get referenced content to be added to schema later
                content, object_name = get_referenced_content(
                    ref_file_path, object_path
                )
                inserted_content[object_name] = content

                # change $ref to local reference
                current_node["$ref"] = f"#/definitions/{object_name}"

        elif isinstance(current_node, list):
            node_stack.extend(current_node)

    # insert referenced content into schema
    if "definitions" not in schema:
        schema["definitions"] = {}
    for object_name, content in inserted_content.items():
        schema["definitions"][object_name] = content
    return schema

def load_schema(target_kind: str) -> Optional[Dict[str, Any]]:
    schema_filename = f"{target_kind}.json"
    schema_file_path = SCHEMA_DIR / schema_filename

    if not schema_file_path.exists():
        logger.error(f"Schema file not found: {schema_file_path}")
        return None

    try:
        with open(schema_file_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        schema = fix_refs_safe(schema, SCHEMA_DIR)
        return schema
    except Exception as e:
        logger.exception(f"Failed to load schema {schema_filename}: {e}")
        return None

def validate_yaml_content(data: Dict[str, Any], file_path: Optional[Path] = None) -> bool:
    """Validates loaded YAML dict against its corresponding schema."""
    kind = data.get("kind")
    if not kind:
        logger.error(f"YAML file missing 'kind' field{f' at {file_path}' if file_path else ''}.")
        return False
    
    schema = load_schema(kind)
    if not schema:
        logger.error(f"No schema found for kind '{kind}'{f' in {file_path}' if file_path else ''}.")
        return False
        
    try:
        validate(data, schema)
        logger.info(f"Successfully validated kind '{kind}'{f' from {file_path}' if file_path else ''}.")
        return True
    except ValidationError as e:
        logger.error(f"Validation failed for kind '{kind}'{f' in {file_path}' if file_path else ''}: {e.message}")
        return False

def validate_yaml_file(file_path: Path) -> bool:
    """Loads a YAML file and validates it."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            logger.error(f"YAML file is empty: {file_path}")
            return False
        return validate_yaml_content(data, file_path)
    except Exception as e:
        logger.error(f"Failed to parse YAML file {file_path}: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python yaml_validation.py <path_to_yaml_file_or_directory>")
        sys.exit(1)
        
    target_path = Path(sys.argv[1])
    if target_path.is_file():
        success = validate_yaml_file(target_path)
        sys.exit(0 if success else 1)
    elif target_path.is_dir():
        yaml_files = list(target_path.glob("**/*.yaml")) + list(target_path.glob("**/*.yml"))
        if not yaml_files:
            print(f"No yaml files found in {target_path}")
            sys.exit(0)
            
        success = True
        for yf in yaml_files:
            if not validate_yaml_file(yf):
                success = False
        sys.exit(0 if success else 1)
    else:
        print(f"Path does not exist: {target_path}")
        sys.exit(1)
