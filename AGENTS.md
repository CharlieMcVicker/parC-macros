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

<!-- ast-outline:start -->
## Code exploration — prefer `ast-outline` over full reads

For `.cs`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`, `.hh`, `.py`, `.pyi`,
`.ts`, `.tsx`, `.js`, `.jsx`, `.java`, `.kt`, `.kts`, `.scala`, `.sc`,
`.go`, `.rs`, `.php`, `.phtml`, `.rb`, `.rake`, `.gemspec`, `.ex`, `.exs`,
`.lua`, `.gd`, `.swift`, `.css`, `.scss`, `.sql`, `.html`, `.htm`, `.vue`,
`.md`, and `.yaml`/`.yml` files, read structure with `ast-outline` before
opening full contents.

Pick the smallest of these that answers your question — they're a
broad-to-narrow menu, not a sequence; skip straight to `show` when
you already know the symbol:

1. **Unfamiliar directory** — `ast-outline digest <paths…>`: one-page map
   of every file's types and public methods. Each file is tagged with a
   size label — `[tiny]` / `[medium]` / `[large]` / `[huge]` — plus
   `[broken]` when parse errors may have left the outline partial.
   `[huge]` files (≥100k tokens) collapse to header-only in the digest;
   call `ast-outline outline <path>` on them when you need full structure.
   Tune density with `--format=names|compact|default|wide` (alias
   `--oneline`=`names`) — `wide` adds private members and fields.

2. **File-level shape** — `ast-outline <paths…>`: signatures with line
   ranges, no bodies (2–10× smaller than a full read on non-trivial
   files). A `# WARNING: N parse errors` line in the header means the
   outline is partial — read the source for the affected region.

3. **One method, type, markdown heading, or yaml key** —
   `ast-outline show <file> <Symbol>`. Suffix matching: `TakeDamage`
   for one method; `User` for an entire type — class, struct, interface,
   trait, enum (whole body, useful when a file holds several types);
   `Player.TakeDamage` when ambiguous. Multiple at once:
   `ast-outline show Player.cs TakeDamage Heal Die`.
   Don't know the file? Pass a directory or glob instead —
   `ast-outline show src/ User` locates it, no separate search call.
   For markdown, the symbol is heading text and matching is
   case-insensitive substring — `"installation"` finds
   `"2.1 Installation (macOS / Linux)"`. For yaml, the symbol is a
   dotted key path (`spec.containers[0].image`) — `show` matches keys,
   not values, so for free-text search inside values use `grep`.
   For css/scss, the symbol is a selector token (`.btn-primary`,
   `$var`) — pseudos and attribute filters are stripped, so
   `.btn-primary` finds the rule even when it carries `:hover` or
   nests in `.modal`.
   For html, the symbol is a CSS-selector token (`#hero`, `.site-nav`,
   `form`, `section#hero`, `[rel=stylesheet]`) — same vocabulary as
   css/scss; pseudo-classes and descendant combinators aren't
   supported (use the tag/id/class/attribute form the outline shows).
   For sql, the symbol is a table or column name (`users`,
   `users.email`) — `show users` returns the table definition,
   `show users.email` returns one column line.
   Add `--signature` to `show` (only there) to return header only
   (docs + attrs + signature, no body) — useful after `digest`, when
   you have the name and want the contract, not the implementation.

4. **Where a symbol appears** —
   `ast-outline grep <pattern> <paths…>`: matches grouped by enclosing
   class/function. Definitions are tagged `[def]`, imports `[import]`;
   calls and refs carry no tag (inferable from `(` after symbol).
   Use for "where is X defined", "who calls Y", "is Z dead code" —
   scope in the output spares follow-up reads. Comments filtered;
   string literals searched and tagged `[string]`, so config keys,
   translation strings and reflection targets are found too. Batch
   via repeatable `-e`:
   `ast-outline grep User.save -e User.load -e User.delete src/`.
   Narrow by classification with `--kind def|call|ref|import` (also
   accepts `--kind def,call`) — drops the post-filter step when you
   only want definitions, only call sites, etc. The split is syntactic:
   `call` is an identifier followed by `(`, `ref` is every other
   mention. So a method's usages are nearly all `call` (`ref` catches
   method references like `Foo::bar`), while a type's usages are nearly
   all `ref`, with `call` catching constructor calls. To count every
   usage, drop `--kind` and read `kind_counts` from `--json`.
   POSIX flags `-w` (whole word), `-l` (paths only), `-c` (counts),
   `-m N` (cap per file) work as in `grep` / `rg`. For non-symbol
   patterns use your default search strategy.

`outline` and `digest` accept multiple paths in one call (files and
directories, mixed languages OK) — batch instead of looping. Type
headers in both renderers carry inheritance as `: Base, Trait`, so the
shape of class hierarchies is visible without a separate query.

The renderers emit a compact skeleton (signatures + line ranges, no
bodies), so output is usually small — narrow with the tool's own flags
before piping to `head`. A `grep | head` cut is the costly one: it
hides matches the header still counts in `(N matches)`, so results look
complete but aren't — cap per file with `-m N` instead.

Narrow the walk with repeatable `--exclude <glob>`
(`.gitignore`-syntax, anchored at the project root) on `outline` /
`digest` / `grep` — e.g. `--exclude tests/ --exclude '*.gen.*'` to
skip test trees and generated files in one call. `!pattern` negates;
`.gitignore` is still honored by default — `--exclude` adds to it.

When you need to know **what a file pulls in** or **where a referenced
type / function comes from**, add `--imports` to `outline` or `digest`.
The file header gets an `imports:` line listing every
`import` / `use` / `using` statement verbatim in the language's native
syntax — `from .core import X`, `use foo::Bar`,
`import { X } from './foo'`, `use App\Foo`, `require_once 'config.php'`,
`require "json"`.
Read the imports, then call `outline` / `show` on the source file
instead of grepping for the definition. Skip the flag for routine
structure reads — it adds one line per file.

A trailing `[+ N conditional includes]` on the imports line means
N more dependencies live inside `if` / `try` / loop / function bodies
— read the file directly when you need the full dependency picture.

Fall back to a full read only when you need context beyond the body
`show` returned. `ast-outline help` for flags.
<!-- ast-outline:end -->
