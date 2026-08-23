# Consumer Integration Specification: Meta-Label Query Lattice Compiler & Acceptor Filter

## Executive Overview

This specification details how the consuming application layer (e.g., Lexicon Derivation / Lexicography Orchestration Pipeline) builds **underspecified input query lattices** ($\mathcal{Q} = \text{Surface} \cdot \mathcal{L}_{\text{restricted}}$) to constrain `parC`'s inverted morphological parse graph ($\mathcal{P}$).

Following `parC`'s **Ports & Adapters Architecture**, configuration reading and I/O are performed upfront (`GrammarConfig` & `ParadigmConfig`). The domain compilation components—the 5-layered `Blueprint` engine—are instantiated as pure, in-memory domain models with explicit dependency injection and zero side effects. By consuming `parC`'s exported OpenFST/Pynini FST assets directly from pure blueprint instances, the consuming application maintains a clean separation of concerns.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CONSUMING APPLICATION LAYER                                                                       │
│                                                                                                   │
│  [MetaLabel Profile] ──▶ [MetaConstraintCompiler]                                                 │
│                                  │                                                                │
│                                  ▼ (Intersects Feature Masks via Pynini)                          │
│                        [Restricted Tag Acceptor] ──┐                                              │
│                                                    │ Concatenate                                  │
│  "surface_form" ───────────────────────────────────┴──▶ [Query Lattice Q]                         │
└───────────────────────────────────────────────────────────────────┬───────────────────────────────┘
                                                                    │ Compose (Q ∘ P)
┌───────────────────────────────────────────────────────────────────▼───────────────────────────────┐
│ parC PORTS & ADAPTERS BLUEPRINT ASSETS                                                            │
│                                                                                                   │
│  1. Upfront Config Adapter:   grammar_config = load_grammar_config(yaml_dir)                     │
│                               paradigm_config = load_paradigm_config("verb", grammar_config)      │
│                                                                                                   │
│  2. Pure Blueprint Stack:     alphabet = AlphabetBlueprint(grammar_config.inventory)             │
│                               patterns = PatternLibraryBlueprint(alphabet, ...)                   │
│                               rules = RulePipelineBlueprint(alphabet, patterns, ...)              │
│                               markers = MarkerLibraryBlueprint(alphabet, patterns, ...)           │
│                               cascade = StageCascadeBlueprint(paradigm_config, alphabet, ...)     │
│                               parser = ParsingEngineBlueprint(cascade)                            │
│                                                                                                   │
│  - Tag Morphotactic Acceptor: L_base = cascade.get_tag_domain_acceptor()                          │
│  - Inverted Parse Graph:      P = parser.build_open_parse_graph(root_regex="<Phone>*")            │
│  - Symbol Table:              syms = alphabet.get_symbol_table()                                  │
│                                                                                                   │
│  Result FST: Compact Output Parse Graph (Extracted Lexical Stems & Feature Profiles)              │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Domain Models (`dataclasses`)

The domain models define declarative constraints on feature slots, resolve interactions/defaults between meta-labels, and maintain discovered lexical state across iterative extraction passes.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class MatchMode(str, Enum):
    """Specifies how feature values should be matched in the slot."""
    EXACT = "exact"          # Matches only the specified value
    ONE_OF = "one_of"        # Matches any value in the provided list
    ANY = "any"              # Unconstrained wildcard (.*)
    EXCLUDE = "exclude"      # Must not match the provided value(s)


@dataclass
class FeatureConstraint:
    """Constraint on a single morphosyntactic or lexical slot."""
    slot_name: str                                  # e.g., "person", "number", "tense", "aspect_class"
    mode: MatchMode = MatchMode.EXACT
    values: List[str] = field(default_factory=list) # e.g., ["3", "sg"] or ["prs"]


@dataclass
class MetaLabelDefinition:
    """Definition of an abstract meta-label and its associated feature constraints."""
    id: str                                         # e.g., "META_3_PRS", "META_V_REF"
    description: Optional[str] = None
    constraints: List[FeatureConstraint] = field(default_factory=list)
    priority: int = 0


@dataclass
class MacroProfile:
    """A collection of active meta-labels applied to a reference form query."""
    name: str                                               # e.g., "citation_default_verb"
    meta_label_ids: List[str] = field(default_factory=list) # e.g., ["META_3_PRS"]
    dynamic_constraints: List[FeatureConstraint] = field(default_factory=list)


@dataclass
class ParsedLexicalProfile:
    """Discovered lexical features extracted from constrained parse results."""
    surface_form: str
    root: str
    features: Dict[str, str] = field(default_factory=dict)
    full_parse: str = ""
    confidence_weight: float = 0.0
```

---

## 2. Direct OpenFST / Pynini Integration Protocol

### Upfront Config & Pure Blueprint Instantiation

`parC` enforces upfront I/O loading. All YAML configs are parsed into strongly-typed `GrammarConfig` and `ParadigmConfig` objects before constructing domain blueprints:

```python
from parC.grammar.config_loader import load_grammar_config, load_paradigm_config
from parC.grammar.blueprints import (
    AlphabetBlueprint,
    PatternLibraryBlueprint,
    RulePipelineBlueprint,
    MarkerLibraryBlueprint,
    StageCascadeBlueprint,
    ParsingEngineBlueprint,
)

# 1. Upfront Config Load (Ports & Adapters I/O Boundary)
grammar_config = load_grammar_config(yaml_dir="config/cherokee")
paradigm_config = load_paradigm_config("verb", grammar_config)

# 2. Instantiate Pure Blueprint Layer Stack
alphabet = AlphabetBlueprint(grammar_config.inventory_configs)
patterns = PatternLibraryBlueprint(alphabet, grammar_config.patterns_configs)
rules = RulePipelineBlueprint(alphabet, patterns, grammar_config.rules_configs)
markers = MarkerLibraryBlueprint(
    alphabet,
    patterns,
    grammar_config.feature_markers_configs,
    grammar_config.contingent_marker_configs,
    grammar_config.morpheme_set_configs,
)
cascade = StageCascadeBlueprint(paradigm_config, alphabet, patterns, rules, markers)
parser = ParsingEngineBlueprint(cascade)
```

Alternatively, convenience factory methods like `ParsingEngineBlueprint.from_paradigm("verb", grammar_config=grammar_config)` can be used to construct the full stack cleanly while maintaining pure dependency injection.

### Symbol Table & Token Serialization
- **Token Syntax**: `parC` feature tags are serialized as multi-character bracketed strings: `"[feature_name=value_name]"` (e.g., `"[person=3]"`).
- **Symbol Table Handling**: When building Pynini acceptors or transducers for tag constraints, pass `token_type=syms` where `syms` is `parC`'s exported `pynini.SymbolTable`.
- **Token Concatenation**: Tags are concatenated directly without whitespace (e.g., `[pos=verb][person=3][number=sg]`).

### `parC` Blueprint Asset Exports
1. **Base Morphotactic Tag Acceptor ($\mathcal{L}_{\text{base}}$)**:
   ```python
   base_tag_acceptor = cascade.get_tag_domain_acceptor()
   ```
2. **Inverted Open Morphological Parse Graph ($\mathcal{P} = \mathcal{T}^{-1}$)**:
   ```python
   parse_graph = parser.build_open_parse_graph(root_regex="<Phone>*")
   ```
3. **Symbol Table ($\Sigma$) & $\Sigma^*$**:
   ```python
   syms = alphabet.get_symbol_table()
   sigma_star = alphabet.get_sigma_star()
   ```

---

## 3. Query Lattice Compiler (`MetaConstraintCompiler`)

The compiler loads base morphotactic acceptors exported by `parC` and applies feature-mask acceptors via direct Pynini operations (`pynini.intersect`, `pynini.concat`, `pynini.compose`).

```python
import pynini
import re
from typing import Dict, List, Optional


class MetaConstraintCompiler:
    """
    Assembles restricted tag acceptors and combines them with surface forms 
    to create underspecified parse query lattices using direct Pynini operations.
    """

    def __init__(
        self,
        base_tag_acceptor: pynini.Fst,
        sigma_star: pynini.Fst,
        symbol_table: pynini.SymbolTable,
        meta_registry: Dict[str, MetaLabelDefinition],
    ):
        self.base_tag_acceptor = base_tag_acceptor.copy()
        self.sigma_star = sigma_star
        self.symbol_table = symbol_table
        self.meta_registry = meta_registry

    def build_slot_mask(self, constraint: FeatureConstraint) -> pynini.Fst:
        """
        Compiles an unanchored feature-slot constraint acceptor:
        F_slot = Sigma* . [slot_name=value] . Sigma*
        """
        if constraint.mode == MatchMode.ONE_OF:
            slot_patterns = [f"[{constraint.slot_name}={val}]" for val in constraint.values]
            target_fsa = pynini.union(*[pynini.accep(p, token_type=self.symbol_table) for p in slot_patterns])
        elif constraint.mode == MatchMode.EXACT:
            target_fsa = pynini.accep(
                f"[{constraint.slot_name}={constraint.values[0]}]", 
                token_type=self.symbol_table
            )
        else:
            raise NotImplementedError(f"Constraint mode {constraint.mode} not supported yet.")

        return pynini.optimize(pynini.concat(self.sigma_star, pynini.concat(target_fsa, self.sigma_star)))

    def compile_restricted_tag_acceptor(self, profile: MacroProfile) -> pynini.Fst:
        """
        Intersects parC's base morphotactic tag acceptor with all active meta constraints.
        L_restricted = L_base ∩ F_1 ∩ F_2 ∩ ... ∩ F_n
        """
        restricted_fsa = self.base_tag_acceptor.copy()

        all_constraints: List[FeatureConstraint] = []
        for meta_id in profile.meta_label_ids:
            meta_def = self.meta_registry[meta_id]
            all_constraints.extend(meta_def.constraints)
        
        all_constraints.extend(profile.dynamic_constraints)

        for constraint in all_constraints:
            slot_mask = self.build_slot_mask(constraint)
            restricted_fsa = pynini.intersect(restricted_fsa, slot_mask)
            restricted_fsa.optimize()

        return restricted_fsa

    def build_query_lattice(self, surface_form: str, profile: MacroProfile) -> pynini.Fst:
        """
        Constructs the final input query FST:
        Q = accep(surface_form) . L_restricted
        """
        surface_fsa = pynini.accep(surface_form, token_type=self.symbol_table)
        tag_lattice = self.compile_restricted_tag_acceptor(profile)
        
        query_fst = pynini.concat(surface_fsa, tag_lattice)
        return pynini.optimize(query_fst)
```

---

## 4. Execution Workflow & Parse Extraction

```python
class LexiconExtractionSession:
    """Orchestrates iterative parsing and dynamic feature discovery."""

    def __init__(
        self, 
        parse_graph: pynini.Fst, 
        compiler: MetaConstraintCompiler,
        symbol_table: pynini.SymbolTable
    ):
        self.parse_graph = parse_graph
        self.compiler = compiler
        self.symbol_table = symbol_table

    def execute_constrained_parse(self, query_lattice: pynini.Fst) -> pynini.Fst:
        """Composes query lattice directly with parC inverted parse graph: Q ∘ P"""
        return pynini.optimize(pynini.compose(query_lattice, self.parse_graph))

    def extract_discovered_features(self, result_fst: pynini.Fst) -> List[ParsedLexicalProfile]:
        """Decodes OpenFST path strings and extracts root & feature dictionaries."""
        profiles = []
        
        # Project output side of FST and extract path strings
        projected = pynini.project(result_fst, project_type="output")
        path_iter = projected.paths()
        
        while not path_iter.done():
            # Decode labels using parC symbol table
            path_str = ""
            for label in path_iter.olabels():
                if label != 0:
                    path_str += self.symbol_table.find(label)
            
            # Extract bracketed tags [feat=val]
            tags = dict(re.findall(r"\[([a-zA-Z0-9_]+)=([a-zA-Z0-9_]+)\]", path_str))
            
            # Isolate root phonemes
            clean_root = re.sub(r"\[[^\]]+\]", "", path_str).replace("[BOW]", "").replace("[EOW]", "")
            
            profiles.append(ParsedLexicalProfile(
                surface_form="",
                root=clean_root,
                features=tags,
                full_parse=path_str,
                confidence_weight=float(path_iter.weight())
            ))
            path_iter.next()
            
        return profiles

    def parse_citation_and_derive_paradigm(self, citation_form: str, other_forms: List[str]):
        # 1. Parse citation form with broad meta labels
        citation_profile = MacroProfile(
            name="citation_pass",
            meta_label_ids=["META_3_PRS"]
        )
        query_lattice = self.compiler.build_query_lattice(citation_form, citation_profile)
        
        # 2. Run OpenFST composition (Q ∘ P)
        result_fst = self.execute_constrained_parse(query_lattice)
        lexical_profiles = self.extract_discovered_features(result_fst)
        
        if not lexical_profiles:
            raise ValueError(f"Form '{citation_form}' could not be parsed with profile {citation_profile}")
            
        first_profile = lexical_profiles[0]
        
        # 3. Use discovered aspect class to tightly constrain subsequent paradigm forms
        dependent_profile = MacroProfile(
            name="dependent_pass",
            meta_label_ids=["META_1SG_PRS"],
            dynamic_constraints=[
                FeatureConstraint(
                    slot_name="aspect_class", 
                    mode=MatchMode.EXACT, 
                    values=[first_profile.features.get("aspect_class", "")]
                )
            ]
        )
        
        # 4. Parse subsequent forms with zero ambiguity
        for form in other_forms:
            dep_query = self.compiler.build_query_lattice(form, dependent_profile)
            dep_result = self.execute_constrained_parse(dep_query)
            dep_profiles = self.extract_discovered_features(dep_result)
            # Process fully resolved forms...
```
