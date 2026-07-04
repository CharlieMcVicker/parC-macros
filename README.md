# parC-macros

A python package and utility suite for generating and validating feature markers in the parC configuration layout.

## Project Structure

- `parc_macros/`: The core Python package.
  - `__init__.py`: Package entrypoint exposing validation and generation APIs.
  - `generate_markers.py`: Script to generate `FeatureMarkers` config files from a metadata-annotated CSV.
  - `yaml_validation.py`: Utility to validate YAML files against JSON schemas in `schemas/`.
  - `schemas/`: Directory containing JSON schemas for different kind definitions (e.g. `FeatureMarkers`, `FeatureDefinitions`, `Rules`, `Paradigm`, `Patterns`, `Inventory`, `PartOfSpeech`).
- `tests/`: Project test suite.
  - `test_yaml_validation.py`: Unit tests validating mock data structures against JSON schemas.
  - `test_generation.py`: Integration tests validating that output generated from `test.csv` matches the `spanish-colang` reference exactly.
- `spanish-colang/`: Imported reference Spanish colang codebase showing target YAML and CSV layouts.
- `spanish-sample/`: Sample Spanish colang codebase.
- `test.csv`: Sample CSV file containing suffix mappings for verb stems (`a_stem`, `e_stem`, `i_stem`) with metadata header comments.
- `environment.yml`: Conda environment configuration file.

## Setup and Usage

### Environment Setup
Use Conda to create the environment:
```bash
conda env create -f environment.yml
conda activate parC-macros
```

### Running Tests
Execute the test suite using pytest with the project root in `PYTHONPATH`:
```bash
PYTHONPATH=. pytest
```

### Executing Code Generation
Run `generate_markers.py` passing a CSV file and output directory:
```bash
python parc_macros/generate_markers.py test.csv output_dir/
```

### Executing YAML Validation
Validate a file or all YAML files in a directory:
```bash
python parc_macros/yaml_validation.py spanish-colang/
```

## Guidelines for future AI Agents

- **YAML Schema Conformity**: All configuration files must validate against the schemas inside `parc_macros/schemas/`. When adding or editing schema constraints, make sure to update schemas correctly and verify by running `yaml_validation.py`.
- **Code Generation Flow**: The `generate_markers.py` parses comments starting with `#` to extract metadata (`kind`, `stage`, `feature`), then maps CSV columns (representing different feature values) to marker configurations. Ensure any new columns or rows preserve this mapping schema.
- **Testing Integrity**: Keep `tests/test_generation.py` updated with any new paradigms or features added to `test.csv` to ensure generation matches expected outputs exactly.
