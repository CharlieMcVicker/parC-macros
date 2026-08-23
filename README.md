# parC-macros

A python package and utility suite for generating and validating feature markers in the parC configuration layout.

## Project Structure

- `parse_chr_dict/`: Cherokee dictionary parsing and root derivation module.
  - `meta_label_compiler.py`: FST tag acceptor compiler (`MetaConstraintCompiler`), meta-label registry (`META_LABELS`), structured `Pronominal` handling, and the 4-step multi-form derivation engine (`derive_lexical_features_4step`).
  - `parse.py`: OpenFST parse graph extraction and root template derivation.
  - `reconstruct.py`: Forward inflection validation (`MetaLabelCombination`) supporting `[PRONOUN_SET=...]`, `[PLURAL=...]`, and `[OBJECT_ANIMACY=...]` meta-labels.
  - `__main__.py`: Main CLI workflow running 4-step multi-form derivation per entry type (`Eventful`, `StativeFutProg`, `StativeNoImp`) across `chr-corpus/corpus.csv`.
- `tests/`: Project test suite.
  - `test_meta_label_compiler.py`: Unit tests covering meta-label FST compilation, Pronominal filters, query lattice composition, multi-form derivation, and real corpus entry tests (including plural entry 355, dual entry 598, and animate entries 776 & 788).
  - `test_parse_chr_dict_baseline.py`: Baseline regression suite for Cherokee dictionary parsing.
- `spanish-colang/`: Imported reference Spanish colang codebase showing target YAML and CSV layouts.
- `spanish-sample/`: Sample Spanish colang codebase.
- `test.csv`: Sample CSV file containing suffix mappings for verb stems (`a_stem`, `e_stem`, `i_stem`) with metadata header comments.
- `environment.yml`: Conda environment configuration file.

## Cherokee Dictionary Parsing & Meta-Label FST Engine

The `parse_chr_dict` module implements a high-performance Finite State Transducer (FST) query lattice composition engine using `pynini` to parse multi-form Cherokee verb entries, derive un-mutated lexical roots, and infer underlying grammatical meta-labels.

### Key Architectural Concepts

1. **Meta-Label FST Acceptor System (`meta_label_compiler.py`)**:
   - Maps high-level grammatical meta-label flags (`[FORM=3RD_PRES]`, `[FORM=1ST_PRES]`, `[PRONOUN_SET=A]`, `[PLURAL=TRUE]`, `[OBJECT_ANIMACY=ANIMATE]`, etc.) into target feature tag lattices.
   - Compiles tag acceptors $\mathcal{L}_{\text{restricted}} = \mathcal{L}_{\text{base}} \cap \bigcap F_{\text{meta}} \cap \bigcap F_{\text{dynamic}}$ and intersects them directly with surface FSAs to construct query lattices $Q = \text{surface} \cdot \mathcal{L}_{\text{restricted}}$.
   - Executes $Q \circ P$ composition via Pynini to prune invalid parse paths at the FST level (~0.21s/row throughput).

2. **Pronominal Struct & Filters**:
   - Structured `@dataclass(frozen=True) class Pronominal` categorizing person (`1st`, `2nd`, `3rd`), number (`sg`, `dl`, `ns`, `pl`), and pronoun set (`A`, `B`, `transitive`).
   - Supports singular, plural (`3ns.A`, `1pl.A`, `Epl.A`), dual (`2dl.A`, `1dl.A`, `Edl.A`), and transitive animate prefixes (`1sg>3sg`, `2sg>3sg`).

3. **4-Step Multi-Form Derivation Engine (`derive_lexical_features_4step`)**:
   - **Step 1**: Parse initial form (`3rd_present`) using `[FORM=3RD_PRES]`.
   - **Step 2**: Run meta-label FST backwards on parse candidates to infer active meta-labels (`[PRONOUN_SET=A]`, `[PLURAL=TRUE/FALSE]`, `[OBJECT_ANIMACY=ANIMATE/INANIMATE]`).
   - **Step 3**: Extract restricted lexical feature sets (`aspect_class`, `prefix_class`, `tense_present_class`).
   - **Step 4**: Parse subsequent forms (`1st_present`, `imperfective`, `completive`, `imperative`, `infinitive`) by composing dynamic constraint masks and propagating unambiguous meta-labels. Supports stem-class compatibility between `k_a_stem` (ka- present) and `a_stem` (u- completive/infinitive) across forms.

4. **Reconstruction & Validation (`reconstruct.py`)**:
   - `MetaLabelCombination` tracks `set_a`, `plural`, and `animate_objects` combinations and inflects derived roots forward via `inflect()`.
   - Validates candidate specifications against reference corpus forms, supporting `k_a_stem` prefix aliases and 2nd person transitive imperative fallbacks.
   - Entry types starting with `Stative` enforce strict `aspect_class.startswith("stative")` filtering in `__main__.py`.

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

### Executing Cherokee Dictionary Parsing
Run the full dictionary parsing and root derivation module:
```bash
PYTHONPATH=. python3 -m parse_chr_dict
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
- **Testing Integrity**: Keep `tests/test_meta_label_compiler.py` and `tests/test_parse_chr_dict_baseline.py` updated with any new paradigms or features added to `parse_chr_dict` to ensure derivation matches expected outputs exactly.
