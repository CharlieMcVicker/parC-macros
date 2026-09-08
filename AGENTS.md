# AGENTS.md

Guidance and operational constraints for AI coding agents working in `parC-macros`.

## 1. Core Architecture & System Invariants

- **Dual Package Architecture**:
  - `parc_macros/`: Generic, language-agnostic code generator and schema validator for the `parC` FST framework. Reads configuration tables/templates and compiles in-place morpheme YAMLs.
  - `parse_chr_dict/`: Domain-specific Cherokee dictionary parsing and lexical root derivation engine using `pynini` (OpenFST) and `parC`.
- **Underlying Engine (`parC`)**: External core engine installed in editable mode (`parC` conda environment). Interfaced via pure blueprint compilation APIs (`StageCascadeBlueprint`, `word_fsa`, `get_open_parse_graph`).
- **In-Place Morpheme Invariant**:
  - Word template: `<PrepronominalPrefixes><PrefixClass><Pro><H_alt><Root><AspectClass><Variant><Aspect><Tense>`
  - Morpheme tags sit directly at their physical linear slot in the word template. Trailing feature tags after `[EOW]` (`[prefix_class=...]`, `[aspect_class=...]`, etc.) are strictly prohibited to prevent Cartesian FST state space explosion.
- **Phonological Tagging Conventions**:
  - H-alternation: Lowercase tags only (`[H_alt=none]`, `[H_alt=drop]`, `[H_alt=glot]`, `[H_alt=lat]`, `[H_alt=a]`, `[H_alt=e]`, `[H_alt=i]`, `[H_alt=o]`, `[H_alt=u]`, `[H_alt=v]`). Legacy uppercase tags (`[H_DROP]`, `[H_GLOT]`, etc.) or generic `[H_alt=vowel]` are obsolete and deleted.
  - Tense: Split into `[Tense=present_a]` and `[Tense=present_i]`. `TenseClass` is completely eliminated.
  - Stative verbs: Stative aspect classes (`chr-config/verb-aspect-stative.csv`) are restricted to `present` and `incompletive`. In `parse_chr_dict`, statives enforce `aspect_class.startswith("stative")` and `INCOMPLETIVE_ASSERTIVE_3RD`.
- **Data Flow**:
  - `chr-data/classes.csv` -> `parse_chr_dict/create_aspect_class_csv.py` -> `chr-config/verb-aspect*.csv` + `chr-config/aspect_effects.csv`.
  - `chr-config/` -> `parc_macros/generate_markers.py` -> `chr-generated/`.
  - `chr-generated/` + `chr-corpus/corpus.csv` -> `parse_chr_dict/__main__.py` -> `roots.csv` + `errors.csv`.

## 2. Directory Boundaries & Layering Rules

- **Zero Coupling Between Macro & Parsing Packages**: `parc_macros/` MUST NEVER import `parse_chr_dict/`. `parse_chr_dict/` MUST NEVER import `parc_macros/`.
- **Generic Generator Boundary**: `parc_macros/` must remain language-agnostic; no Cherokee-specific heuristics, rules, or character stripping belong in `parc_macros/`.
- **Source of Truth vs. Generated Artifacts**:
  - `chr-config/` is the single source of truth for grammar specifications, CSV matrices, and hand-crafted phonology rules (`Phonology/Rules/h_alternation.yaml`).
  - `chr-generated/` contains compiled YAML assets. NEVER edit files in `chr-generated/` directly; always edit `chr-config/` or generator scripts, then regenerate.
- **Task Management Boundary**: All task tracking is strictly managed via Backlog CLI in `backlog/`. Never manually edit `backlog/tasks/*.md` files directly.

## 3. Exact Verification & Execution Commands

Always run inside the `parC` conda environment with `PYTHONPATH=.`.

### Verification & Testing
```bash
# Syntax & bytecode verification across all packages
python -m py_compile parc_macros/*.py parse_chr_dict/*.py tests/*.py

# Run full test suite (129 tests, ~4.6s)
PYTHONPATH=. pytest

# Targeted single-file test runs
PYTHONPATH=. pytest tests/test_derive_pipeline.py
PYTHONPATH=. pytest tests/test_clean_inplace_generation.py
PYTHONPATH=. pytest tests/test_h_alternation_targeted.py
PYTHONPATH=. pytest tests/test_acceptors.py

# Targeted single test function
PYTHONPATH=. pytest tests/test_derive_pipeline.py -k test_real_plural_verb_entry_355
```

### Build, Generation & Validation
```bash
# Regenerate all grammar YAML assets from chr-config/ into chr-generated/
python parc_macros/generate_markers.py chr-config chr-generated

# Regenerate aspect CSV matrices and effect triggers from chr-data/
python parse_chr_dict/create_aspect_class_csv.py

# Validate generated YAML configurations against JSON schemas
python parc_macros/yaml_validation.py chr-generated/
```

### Execution
```bash
# Run full dictionary derivation workflow (reads chr-corpus/corpus.csv; ~2 min)
YAML_DIR=chr-generated/ python -u -m parse_chr_dict
# or execute convenience script:
./parse_dict.sh

# Interactive or single-word morpheme segmentation CLI
PYTHONPATH=. python -m parse_chr_dict.segment "katateka"
```

## 4. Anti-Patterns & Negative Rules

- **DO NOT** edit files in `chr-generated/` directly. Always edit `chr-config/` or generator code and regenerate.
- **DO NOT** add trailing feature tags (`[prefix_class=...]`, `[aspect_class=...]`, etc.) after `[EOW]`. All tags must be local in-place morphemes.
- **DO NOT** resurrect legacy uppercase tags (`[H_DROP]`, `[H_GLOT]`, `[H_LAT]`) or generic `[H_alt=vowel]`.
- **DO NOT** create barrel files (`__init__.py` re-exporting submodules). `parse_chr_dict/__init__.py` is empty; keep imports explicit from source modules.
- **DO NOT** introduce cross-imports between `parc_macros` and `parse_chr_dict`.
- **DO NOT** mutate domain models in `parse_chr_dict/types.py`. `ParseData`, `LexicalVerb`, `VerbForm`, and `Pronominal` are `@dataclass(frozen=True)`.
- **DO NOT** forget cache invalidation when switching `YAML_DIR` or reloading FSTs in test fixtures: call `parC.grammar.paradigm_compilation.clear_all_caches()` and reset `parse_mod.PARSE_GRAPH = None`.
- **DO NOT** use inline imports inside functions or methods. All module imports must be declared at the top of the file to ensure explicit dependencies and prevent hidden initialization overhead.
- **DO NOT** leave temporary profiling `.prof` files, debug print statements, or scratch scripts committed in source directories.

## 5. Internal-Only / No Backwards-Compatibility Policy

- **Aggressive Deletion Over Deprecation**: This is an internal-only codebase. When changing an API, function signature, or data structure, delete the replaced code immediately.
- **Zero Legacy Shims**: Do not add compatibility shims, fallback parameters, aliases, or dual-path branching (e.g., supporting both old and new tag styles).
- **Direct Caller Refactoring**: Update all callers, test cases, and fixtures across the repo in the same change.
- **No Dead Code Retention**: Remove obsolete test suites, unused helper routines, and orphaned scripts immediately (per precedent in Tasks 131, 133, 135-140).

## 6. Project Structure & Key Features

```text
parC-macros/
├── chr-config/           # Source of truth: verb.yaml, CSV matrices, Phonology/Rules/
├── chr-generated/        # Compiled parC YAML assets (DO NOT EDIT; build artifact)
├── chr-corpus/           # corpus.csv (708 dictionary entries)
├── chr-data/             # classes.csv (source inflectional classification)
├── parc_macros/          # Generic YAML/FST generator (language-agnostic)
│   ├── generate_markers.py # Main grammar compiler
│   ├── yaml_validation.py  # JSON schema validator (parc_macros/schemas/)
│   └── generate_*_rules.py # Phonology, insertion & replace rule generators
├── parse_chr_dict/       # Cherokee root derivation & FST parsing engine
│   ├── __main__.py       # Full corpus batch pipeline -> roots.csv, errors.csv
│   ├── types.py          # Frozen domain models (LexicalVerb, VerbForm, Pronominal)
│   ├── derive.py         # Multi-form surface parsing & hypothesis pruning
│   ├── parse.py          # OpenFST graph construction & surface parsing
│   ├── reconstruct.py    # Forward inflection & candidate hypothesis validation
│   ├── acceptors.py      # Form-specific morphotactic query lattices
│   ├── h_alternation.py  # H-alternation phonological rule handler
│   └── segment.py        # CLI interactive morpheme segmenter
└── tests/                # Pytest suite (primarily test_derive_pipeline.py)
```

### Updating the File Tree
Keep this tree curated to core architecture files only. Do not expand build artifacts (`chr-generated/`), raw data, or internal sub-helpers.

