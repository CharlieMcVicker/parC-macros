from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import functools
import re

import pynini
from parC.grammar.paradigm_compilation import (
    get_open_parse_graph,
    word_fsa,
    fsa,
    get_symbol_table,
    get_sigma_star,
)
from parC.grammar.acceptor_compilation import fsm_strings
from parse_chr_dict.parse import feature_tag, read_labels, str_to_lexical_hashable
from parse_chr_dict.types import (
    ParseData,
    InPlaceParseConfig,
    VerbTemplate,
    AspectVariants,
    VerbMetadata,
    LexicalVerb,
    DerivationHypothesis,
    LexicalVerbHypothesis,
    LexicalVerbEntry,
)
from parse_chr_dict.h_alternation import (
    H_ALT_TAGS,
    is_h_alternation_trigger,
    validate_h_alternation_trigger,
    strip_h_alt_tags,
    determine_h_alt_glottal_root,
)




class MatchMode(str, Enum):
    """Specifies how feature values should be matched in the slot."""
    EXACT = "exact"
    ONE_OF = "one_of"
    ANY = "any"
    EXCLUDE = "exclude"


@dataclass(frozen=True)
class Pronominal:
    """Structured representation of a pronominal tag (e.g. 3sg.A, 1sg>3sg, 3ns.B)."""
    tag: str
    person: str        # "1st", "2nd", "3rd"
    number: str        # "sg", "ns", "pl"
    pronoun_set: str   # "A", "B", "transitive"

    @classmethod
    @functools.lru_cache(maxsize=256)
    def from_tag(cls, tag: str) -> Pronominal:
        if ">" in tag:
            subj = tag.split(">")[0]
            person = "1st" if subj.startswith("1") else "2nd" if subj.startswith("2") else "3rd"
            return cls(tag=tag, person=person, number="sg", pronoun_set="transitive")

        # Standard tags: 3sg.A, 1sg.B, 3ns.A, Epl.A, etc.
        parts = tag.split(".")
        prefix = parts[0]
        pronoun_set = parts[1] if len(parts) > 1 else "A"

        if prefix.startswith("1") or prefix.startswith("E") or prefix.startswith("I"):
            person = "1st"
            number = "sg" if prefix == "1sg" else "dl" if "dl" in prefix else "pl"
        elif prefix.startswith("2"):
            person = "2nd"
            number = "sg" if prefix == "2sg" else "dl" if "dl" in prefix else "pl"
        elif prefix.startswith("3"):
            person = "3rd"
            number = "sg" if "sg" in prefix else "dl" if "dl" in prefix else "ns" if "ns" in prefix else "pl"
        else:
            person, number = "3rd", "sg"

        return cls(tag=tag, person=person, number=number, pronoun_set=pronoun_set)


ALL_PRONOMINALS: List[Pronominal] = [
    Pronominal.from_tag(t) for t in [
        "3sg.A", "3sg.B", "1sg.A", "1sg.B", "2sg.A", "2sg.B",
        "3ns.A", "3ns.B", "3dl.A", "3dl.B",
        "1pl.A", "1pl.B", "1dl.A", "1dl.B",
        "2pl.A", "2pl.B", "2dl.A", "2dl.B",
        "Epl.A", "Epl.B", "Edl.A", "Edl.B",
        "Ipl.A", "Ipl.B", "Idl.A", "Idl.B",
        "1sg>3sg", "2sg>3sg",
    ]
]


def filter_pronominals(
    person: Optional[str] = None,
    number: Optional[str] = None,
    pronoun_set: Optional[str] = None,
    exclude_transitive: bool = False,
) -> List[str]:
    """Filters PRONOMINAL tags using clean functional predicates."""
    res = ALL_PRONOMINALS
    if person is not None:
        res = [p for p in res if p.person == person]
    if number is not None:
        res = [p for p in res if p.number == number]
    if pronoun_set is not None:
        if pronoun_set == "A":
            res = [p for p in res if p.pronoun_set in ("A", "transitive")]
        else:
            res = [p for p in res if p.pronoun_set == pronoun_set]
    if exclude_transitive:
        res = [p for p in res if p.pronoun_set != "transitive"]
    return [p.tag for p in res]


@dataclass
class FeatureConstraint:
    """Constraint on a single morphosyntactic or lexical slot."""
    slot_name: str
    mode: MatchMode = MatchMode.EXACT
    values: List[str] = field(default_factory=list)


@dataclass
class MetaLabelDefinition:
    """Definition of an abstract meta-label and its associated feature constraints."""
    id: str
    description: Optional[str] = None
    constraints: List[FeatureConstraint] = field(default_factory=list)
    priority: int = 0


@dataclass
class FormParsingSpec:
    """Specification of a form parsing layout."""
    corpus_key: str
    name: str
    meta_label_id: str
    person: str
    allows_set_a: bool


@dataclass
class EntryTypeSpec:
    """Specifies entry type and associated forms."""
    name: str
    forms: List[str]

    def get_forms_from_parses(self, form_parses: dict) -> List[Set]:
        return [form_parses[name][1] for name in self.forms if name in form_parses]


FORMS_TO_PARSE: List[FormParsingSpec] = [
    FormParsingSpec(
        corpus_key="present",
        name="3rd_present",
        meta_label_id="[FORM=3RD_PRES]",
        person="3rd",
        allows_set_a=True,
    ),
    FormParsingSpec(
        corpus_key="present_1sg",
        name="1st_present",
        meta_label_id="[FORM=1ST_PRES]",
        person="1st",
        allows_set_a=True,
    ),
    FormParsingSpec(
        corpus_key="imperfective",
        name="3rd_incompletive_habitual",
        meta_label_id="[FORM=3RD_HABITUAL]",
        person="3rd",
        allows_set_a=True,
    ),
    FormParsingSpec(
        corpus_key="perfective",
        name="3rd_completive_assertive",
        meta_label_id="[FORM=3RD_COMPLETIVE]",
        person="3rd",
        allows_set_a=False,
    ),
    FormParsingSpec(
        corpus_key="perfective",
        name="3rd_incompletive_assertive",
        meta_label_id="[FORM=3RD_INCOMPLETIVE_ASSERTIVE]",
        person="3rd",
        allows_set_a=True,
    ),
    FormParsingSpec(
        corpus_key="imperative",
        name="2nd_imperative",
        meta_label_id="[FORM=2ND_IMPERATIVE]",
        person="2nd",
        allows_set_a=True,
    ),
    FormParsingSpec(
        corpus_key="imperative",
        name="2nd_future_prog",
        meta_label_id="[FORM=2ND_FUT_PROG]",
        person="2nd",
        allows_set_a=True,
    ),
    FormParsingSpec(
        corpus_key="infinitive",
        name="3rd_infinitive",
        meta_label_id="[FORM=3RD_INFINITIVE]",
        person="3rd",
        allows_set_a=False,
    ),
]

PRIMARY_ENTRY_TYPES: List[EntryTypeSpec] = [
    EntryTypeSpec(
        name="Eventful",
        forms=[
            "3rd_present",
            "1st_present",
            "3rd_incompletive_habitual",
            "3rd_completive_assertive",
            "2nd_imperative",
            "3rd_infinitive",
        ],
    ),
    EntryTypeSpec(
        name="StativeFutProg",
        forms=[
            "3rd_present",
            "1st_present",
            "3rd_incompletive_habitual",
            "3rd_completive_assertive",
            "2nd_future_prog",
        ],
    ),
    EntryTypeSpec(
        name="StativeNoImp",
        forms=[
            "3rd_present",
            "1st_present",
            "3rd_incompletive_habitual",
            "3rd_completive_assertive",
        ],
    ),
]

SHIM_ENTRY_TYPES: List[EntryTypeSpec] = [
    EntryTypeSpec(
        name="EventfulInfinitive",
        forms=["3rd_infinitive"],
    ),
    EntryTypeSpec(
        name="EventfulImperativeInfinitive",
        forms=["2nd_imperative", "3rd_infinitive"],
    ),
]


# Pre-defined Meta Labels
META_LABELS: Dict[str, MetaLabelDefinition] = {
    "[FORM=3RD_PRES]": MetaLabelDefinition(
        id="[FORM=3RD_PRES]",
        description="3rd person present form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["present"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["present"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(person="3rd")),
        ],
    ),
    "[FORM=1ST_PRES]": MetaLabelDefinition(
        id="[FORM=1ST_PRES]",
        description="1st person present form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["present"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["present"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(person="1st")),
        ],
    ),
    "[FORM=3RD_HABITUAL]": MetaLabelDefinition(
        id="[FORM=3RD_HABITUAL]",
        description="3rd person habitual form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["habitual"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["incompletive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(person="3rd")),
        ],
    ),
    "[FORM=3RD_COMPLETIVE]": MetaLabelDefinition(
        id="[FORM=3RD_COMPLETIVE]",
        description="3rd person completive assertive form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["assertive"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["completive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["3sg.B", "3ns.B"]),
        ],
    ),
    "[FORM=3RD_INCOMPLETIVE_ASSERTIVE]": MetaLabelDefinition(
        id="[FORM=3RD_INCOMPLETIVE_ASSERTIVE]",
        description="3rd person incompletive assertive form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["assertive"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["incompletive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(person="3rd")),
        ],
    ),
    "[FORM=2ND_IMPERATIVE]": MetaLabelDefinition(
        id="[FORM=2ND_IMPERATIVE]",
        description="2nd person immediate imperative form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["immediate"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["immediate"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(person="2nd")),
        ],
    ),
    "[FORM=2ND_FUT_PROG]": MetaLabelDefinition(
        id="[FORM=2ND_FUT_PROG]",
        description="2nd person future progressive form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["future_prog"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["incompletive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(person="2nd")),
        ],
    ),
    "[FORM=3RD_INFINITIVE]": MetaLabelDefinition(
        id="[FORM=3RD_INFINITIVE]",
        description="3rd person infinitive form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["infinitive"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["infinitive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["3sg.B", "3ns.B"]),
        ],
    ),
    "[PRONOUN_SET=A]": MetaLabelDefinition(
        id="[PRONOUN_SET=A]",
        description="Pronoun Set A constraint",
        constraints=[
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(pronoun_set="A")),
        ],
    ),
    "[PLURAL=TRUE]": MetaLabelDefinition(
        id="[PLURAL=TRUE]",
        description="Plural or dual subject or object pronominal forms",
        constraints=[
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(number="ns") + filter_pronominals(number="pl") + filter_pronominals(number="dl")),
        ],
    ),
    "[PLURAL=FALSE]": MetaLabelDefinition(
        id="[PLURAL=FALSE]",
        description="Singular pronominal forms",
        constraints=[
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(number="sg")),
        ],
    ),
    "[OBJECT_ANIMACY=ANIMATE]": MetaLabelDefinition(
        id="[OBJECT_ANIMACY=ANIMATE]",
        description="Transitive animate object pronominal forms (1sg>3sg, 2sg>3sg, etc.)",
        constraints=[
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(pronoun_set="transitive")),
        ],
    ),
    "[OBJECT_ANIMACY=INANIMATE]": MetaLabelDefinition(
        id="[OBJECT_ANIMACY=INANIMATE]",
        description="Inanimate object or intransitive pronominal forms",
        constraints=[
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=filter_pronominals(exclude_transitive=True)),
        ],
    ),
}


class MetaConstraintCompiler:
    """
    Compiler that maps meta label definitions to target feature tag lattices.
    """

    def __init__(
        self,
        base_tag_acceptor: Optional[pynini.Fst] = None,
        sigma_star: Optional[pynini.Fst] = None,
        symbol_table: Optional[pynini.SymbolTable] = None,
        meta_registry: Optional[Dict[str, MetaLabelDefinition]] = None,
    ):
        self.symbol_table = symbol_table if symbol_table is not None else get_symbol_table()
        self.sigma_star = sigma_star if sigma_star is not None else get_sigma_star()
        self.meta_registry = meta_registry if meta_registry is not None else META_LABELS
        self.base_tag_acceptor = base_tag_acceptor.copy() if base_tag_acceptor is not None else None
        self._slot_mask_cache: Dict[Tuple[str, MatchMode | str, Tuple[str, ...]], pynini.Fst] = {}
        self._acceptor_cache: Dict[Tuple[Tuple[str, ...], Tuple], pynini.Fst] = {}
        self._surface_fsa_cache: Dict[str, pynini.Fst] = {}
        self._surface_parse_cache: Dict[Tuple[str, Optional[int]], List[str]] = {}
        self._query_lattice_cache: Dict[Tuple[str, Tuple[str, ...], Tuple], pynini.Fst] = {}
        self._parse_cache: Dict[Tuple[str, Tuple[str, ...], Tuple], List[str]] = {}
        self._feature_tuples_cache: Dict[Tuple[str, ...], List[Tuple[str, str]]] = {}
        from parse_chr_dict.parse import get_parse_graph
        self.parse_graph = get_parse_graph()
        # Pre-compile static single meta-label acceptors
        for meta_id in self.meta_registry:
            self.compile_restricted_tag_acceptor([meta_id])

    def parse_surface(
        self,
        surface: str,
        parse_graph: Optional[pynini.Fst] = None,
    ) -> List[str]:
        """
        Parses a bare surface form without input tag acceptors by executing
        pynini.compose(linear_surface_fsa, parse_graph).
        Memoized by (surface, id(parse_graph)).
        """
        if not surface:
            return []

        graph = parse_graph if parse_graph is not None else self.parse_graph
        graph_key = id(parse_graph) if parse_graph is not None else None
        cache_key = (surface, graph_key)

        if hasattr(self, "_surface_parse_cache") and cache_key in self._surface_parse_cache:
            return self._surface_parse_cache[cache_key]

        if not hasattr(self, "_surface_fsa_cache"):
            self._surface_fsa_cache = {}

        if surface in self._surface_fsa_cache:
            surface_fsa = self._surface_fsa_cache[surface]
        else:
            surface_fsa = word_fsa(surface)
            self._surface_fsa_cache[surface] = surface_fsa

        output_lattice = pynini.compose(surface_fsa, graph).optimize()
        output_lattice = pynini.project(output_lattice, project_type="output")
        output_lattice = pynini.rmepsilon(output_lattice).optimize()
        if output_lattice.properties(pynini.CYCLIC, True) == pynini.CYCLIC:
            output_lattice = pynini.shortestpath(output_lattice, nshortest=2000).optimize()

        results = fsm_strings(output_lattice, strip_all_tags=False)

        if not hasattr(self, "_surface_parse_cache"):
            self._surface_parse_cache = {}
        self._surface_parse_cache[cache_key] = results
        return results

    def build_slot_mask(self, constraint: FeatureConstraint) -> pynini.Fst:
        """
        Compiles an unanchored feature-slot constraint acceptor:
        F_slot = Sigma* . [slot_name=value] . Sigma*
        Memoized by (slot_name, mode, values tuple).
        """
        if not constraint.values:
            return pynini.Fst()

        mode_val = constraint.mode if isinstance(constraint.mode, str) else constraint.mode.value
        cache_key = (constraint.slot_name, mode_val, tuple(constraint.values))
        if cache_key in self._slot_mask_cache:
            return self._slot_mask_cache[cache_key]

        slot_patterns = [
            feature_tag(constraint.slot_name, val)
            for val in constraint.values
            if self.symbol_table.find(feature_tag(constraint.slot_name, val)) != -1
        ]
        if not slot_patterns:
            return pynini.Fst()

        if len(slot_patterns) == 1:
            target_fsa = pynini.accep(slot_patterns[0], token_type=self.symbol_table)
        else:
            target_fsa = pynini.union(*[pynini.accep(p, token_type=self.symbol_table) for p in slot_patterns])

        compiled_mask = pynini.optimize(pynini.concat(self.sigma_star, pynini.concat(target_fsa, self.sigma_star)))
        self._slot_mask_cache[cache_key] = compiled_mask
        return compiled_mask

    def compile_restricted_tag_acceptor(
        self,
        meta_label_ids: List[str],
        dynamic_constraints: Optional[List[FeatureConstraint]] = None,
    ) -> pynini.Fst:
        """
        Intersects parC's base morphotactic tag acceptor (or Sigma*) with active meta constraints
        and optional dynamic constraints:
        L_restricted = L_base ∩ F_1 ∩ F_2 ∩ ... ∩ F_n ∩ F_dyn1 ∩ ...
        """
        # Cache key based on sorted meta label IDs and dynamic constraint representations
        dyn_tuple = ()
        if dynamic_constraints:
            dyn_tuple = tuple(
                sorted(
                    (c.slot_name, c.mode if isinstance(c.mode, str) else c.mode.value, tuple(c.values))
                    for c in dynamic_constraints
                )
            )
        cache_key = (tuple(sorted(meta_label_ids)), dyn_tuple)
        if hasattr(self, "_acceptor_cache") and cache_key in self._acceptor_cache:
            return self._acceptor_cache[cache_key]

        from parse_chr_dict.parse import is_inplace_grammar
        restricted_fsa = (
            self.base_tag_acceptor.copy()
            if (self.base_tag_acceptor is not None and not is_inplace_grammar())
            else self.sigma_star.copy()
        )

        all_constraints: List[FeatureConstraint] = []
        for meta_id in meta_label_ids:
            if meta_id in self.meta_registry:
                all_constraints.extend(self.meta_registry[meta_id].constraints)

        if dynamic_constraints:
            all_constraints.extend(dynamic_constraints)

        for constraint in all_constraints:
            slot_mask = self.build_slot_mask(constraint)
            restricted_fsa = pynini.intersect(restricted_fsa, slot_mask)
            restricted_fsa.optimize()

        if not hasattr(self, "_acceptor_cache"):
            self._acceptor_cache = {}
        self._acceptor_cache[cache_key] = restricted_fsa
        return restricted_fsa

    def build_query_lattice(
        self,
        surface_form: str,
        meta_label_ids: List[str],
        dynamic_constraints: Optional[List[FeatureConstraint]] = None,
    ) -> pynini.Fst:
        """
        Builds query lattice Q = surface_fsa . L_restricted
        Memoized by (surface_form, sorted(meta_label_ids), dynamic_constraints).
        """
        dyn_tuple = ()
        if dynamic_constraints:
            dyn_tuple = tuple(
                sorted(
                    (c.slot_name, c.mode if isinstance(c.mode, str) else c.mode.value, tuple(c.values))
                    for c in dynamic_constraints
                )
            )
        cache_key = (surface_form, tuple(sorted(meta_label_ids)), dyn_tuple)
        if hasattr(self, "_query_lattice_cache") and cache_key in self._query_lattice_cache:
            return self._query_lattice_cache[cache_key]

        L_restricted = self.compile_restricted_tag_acceptor(
            meta_label_ids, dynamic_constraints=dynamic_constraints
        )
        if not hasattr(self, "_surface_fsa_cache"):
            self._surface_fsa_cache = {}
        if surface_form in self._surface_fsa_cache:
            surface_fsa = self._surface_fsa_cache[surface_form]
        else:
            surface_fsa = word_fsa(surface_form)
            self._surface_fsa_cache[surface_form] = surface_fsa

        Q = pynini.concat(surface_fsa, L_restricted)
        if not hasattr(self, "_query_lattice_cache"):
            self._query_lattice_cache = {}
        self._query_lattice_cache[cache_key] = Q
        return Q

    def parse_with_lattice(
        self,
        surface_form: str,
        meta_label_ids: List[str],
        dynamic_constraints: Optional[List[FeatureConstraint]] = None,
        parse_graph: Optional[pynini.Fst] = None,
    ) -> List[str]:
        """
        Executes lattice parsing.
        For in-place grammar: projects output of surface o P, then intersects with L_restricted.
        For legacy grammar: Q o P composition where Q = surface_fsa . L_restricted.
        """
        dyn_tuple = ()
        if dynamic_constraints:
            dyn_tuple = tuple(
                sorted(
                    (c.slot_name, c.mode if isinstance(c.mode, str) else c.mode.value, tuple(c.values))
                    for c in dynamic_constraints
                )
            )
        cache_key = (surface_form, tuple(sorted(meta_label_ids)), dyn_tuple)
        if (parse_graph is None or parse_graph is self.parse_graph) and hasattr(self, "_parse_cache"):
            if cache_key in self._parse_cache:
                return self._parse_cache[cache_key]

        if parse_graph is None:
            parse_graph = self.parse_graph

        from parse_chr_dict.parse import is_inplace_grammar
        if is_inplace_grammar():
            if not hasattr(self, "_surface_fsa_cache"):
                self._surface_fsa_cache = {}
            if surface_form in self._surface_fsa_cache:
                surface_fsa = self._surface_fsa_cache[surface_form]
            else:
                surface_fsa = word_fsa(surface_form)
                self._surface_fsa_cache[surface_form] = surface_fsa

            output_lattice = pynini.compose(surface_fsa, parse_graph).optimize()
            output_lattice = pynini.project(output_lattice, project_type="output")
            output_lattice = pynini.rmepsilon(output_lattice).optimize()

            L_restricted = self.compile_restricted_tag_acceptor(
                meta_label_ids, dynamic_constraints=dynamic_constraints
            )
            output_lattice = pynini.intersect(output_lattice, L_restricted).optimize()
        else:
            Q = self.build_query_lattice(
                surface_form, meta_label_ids, dynamic_constraints=dynamic_constraints
            )
            output_lattice = pynini.compose(Q, parse_graph).optimize()
            output_lattice = pynini.project(output_lattice, project_type="output")
            output_lattice = pynini.rmepsilon(output_lattice).optimize()

        if output_lattice.properties(pynini.CYCLIC, True) == pynini.CYCLIC:
            output_lattice = pynini.shortestpath(output_lattice, nshortest=2000).optimize()

        results = fsm_strings(output_lattice, strip_all_tags=False)

        if (parse_graph is self.parse_graph or parse_graph is None) and hasattr(self, "_parse_cache"):
            self._parse_cache[cache_key] = results
        return results

    def get_feature_tuples_from_meta(self, meta_label_ids: List[str]) -> List[Tuple[str, str]]:
        """
        Maps meta label strings to target feature label flag tuples (Step 1a).
        """
        key = tuple(sorted(meta_label_ids))
        if hasattr(self, "_feature_tuples_cache") and key in self._feature_tuples_cache:
            return self._feature_tuples_cache[key]

        tuples = []
        for meta_id in meta_label_ids:
            if meta_id in self.meta_registry:
                for c in self.meta_registry[meta_id].constraints:
                    if c.mode == MatchMode.EXACT and len(c.values) == 1:
                        tuples.append((c.slot_name, c.values[0]))

        if hasattr(self, "_feature_tuples_cache"):
            self._feature_tuples_cache[key] = tuples
        return tuples

    def infer_meta_labels_from_parse(self, parse_str: str) -> List[str]:
        """
        Step 2: Runs the meta label FST backwards (via intersection/inversion logic)
        to identify which meta labels match candidate derivation features in parse_str.
        """
        _, labels_dict = read_labels(parse_str)
        matched_meta = []

        for meta_id, meta_def in self.meta_registry.items():
            matches_all = True
            for constraint in meta_def.constraints:
                val = labels_dict.get(constraint.slot_name)
                if val is None:
                    matches_all = False
                    break
                if constraint.mode == MatchMode.EXACT:
                    if val != constraint.values[0]:
                        matches_all = False
                        break
                elif constraint.mode == MatchMode.ONE_OF:
                    if val not in constraint.values:
                        matches_all = False
                        break
                elif constraint.mode == MatchMode.EXCLUDE:
                    if val in constraint.values:
                        matches_all = False
                        break
            if matches_all and meta_def.constraints:
                matched_meta.append(meta_id)

        return matched_meta


def parse_string_to_parse_data(p: str) -> ParseData:
    """Converts a raw parse string (in-place morphemes or legacy trailing tags) to ParseData."""
    from parse_chr_dict.parse import read_inplace_parse, read_labels
    if "[" in p and ("PrefixClass=" in p or "AspectClass=" in p or "Pro=" in p):
        return read_inplace_parse(p)
    form, labels = read_labels(p)
    var_raw = labels.get("variant", 1)
    var = int(var_raw) if str(var_raw).isdigit() else 1
    return ParseData(
        root=form,
        prefix_class=labels.get("prefix_class", ""),
        pronominal=labels.get("pronominal", ""),
        h_alt_tag=labels.get("h_alt_tag", ""),
        aspect_class=labels.get("aspect_class", ""),
        variant=var,
        aspect=labels.get("aspect", ""),
        tense_present_class=labels.get("tense_present_class", ""),
        tense=labels.get("tense", ""),
    )


def derive_hypotheses_for_forms(
    forms: List[Tuple[str, FormParsingSpec | str]],
    compiler: MetaConstraintCompiler,
    lexical_features: Optional[Set[str]] = None,
) -> Set[LexicalVerb]:
    """
    Derives and iteratively narrows candidate LexicalVerb objects form-by-form across a row:
    1. Parse the initial form with its meta-label to generate candidate hypotheses
       as LexicalVerb instances (VerbTemplate x VerbMetadata).
    2. For each subsequent form, parse using the specific constraints of each hypothesis
       to filter/prune the candidate set, enforce present-tense variant consistency,
       fold non-shared aspect variants into VerbMetadata, and check H-alternation compatibility.
    """
    if not forms:
        return set()

    spec_by_meta = {p.meta_label_id: p for p in FORMS_TO_PARSE}

    # Normalize forms to List[Tuple[str, FormParsingSpec]]
    normalized_forms: List[Tuple[str, FormParsingSpec]] = []
    for surface, spec_or_id in forms:
        if isinstance(spec_or_id, FormParsingSpec):
            spec = spec_or_id
        else:
            spec = spec_by_meta.get(spec_or_id)
            if spec is None:
                spec = FormParsingSpec(
                    corpus_key="",
                    name=spec_or_id,
                    meta_label_id=spec_or_id,
                    person="3rd",
                    allows_set_a=True,
                )
        normalized_forms.append((surface, spec))

    # Step 1: Initial form
    init_surface, init_spec = normalized_forms[0]
    if not init_surface:
        return set()

    init_parses = compiler.parse_with_lattice(init_surface, [init_spec.meta_label_id])
    if not init_parses:
        return set()

    candidate_hypotheses: Set[LexicalVerb] = set()

    for p in init_parses:
        p_data = parse_string_to_parse_data(p)
        tmpl = VerbTemplate.from_parse(p_data)
        pref = tmpl.prefix_class
        asp = tmpl.aspect_class
        t_pres = tmpl.tense_present_class
        pro_tag = p_data.pronominal
        pres_var = tmpl.variant
        if not pref or not asp or not t_pres or not pro_tag:
            continue

        pro = Pronominal.from_tag(pro_tag)
        is_plural = pro.number in ("ns", "pl", "dl")
        is_transitive = pro.pronoun_set == "transitive"
        is_set_a = pro.pronoun_set in ("A", "transitive")
        is_glottal = is_h_alternation_trigger(pro_tag)

        # Validate trigger if mutation tag is present
        has_mutation = any(tag in p_data.root for tag in H_ALT_TAGS if tag.lower() not in ("[h_none]", "[h_alt=none]"))
        if not validate_h_alternation_trigger(pro_tag, has_h_alt=has_mutation):
            continue

        # Set A candidate values
        if init_spec.allows_set_a:
            set_a_options = [is_set_a]
        else:
            set_a_options = [True, False]

        # Plural candidate values
        plural_options = [is_plural]

        # Animate object candidate values
        if is_plural:
            animate_options = [False]
        elif is_transitive:
            animate_options = [True]
        elif init_spec.person == "3rd":
            animate_options = [False, True]
        else:
            animate_options = [False]

        glottal_root_val = p_data.root if is_glottal else None
        h_alt_val = p_data.h_alt_tag
        aspect_variants = AspectVariants(present=pres_var)

        for sa in set_a_options:
            for pl in plural_options:
                for anim in animate_options:
                    meta = VerbMetadata(
                        entry_type="Eventful",
                        is_set_a=sa,
                        is_plural=pl,
                        animate_objects=anim,
                        aspect_variants=aspect_variants,
                    )
                    candidate_hypotheses.add(
                        LexicalVerb(
                            template=tmpl,
                            metadata=meta,
                            glottal_root=glottal_root_val,
                            h_alt_tag=h_alt_val,
                        )
                    )

    if not candidate_hypotheses or len(normalized_forms) == 1:
        return candidate_hypotheses

    # Step 2: Form-by-form refinement
    def prefix_compat(p1: str, p2: str) -> bool:
        return p1 == p2 or (p1 in ("k_a_stem", "a_stem") and p2 in ("k_a_stem", "a_stem"))

    for surface, form_spec in normalized_forms[1:]:
        if not surface:
            continue
        if not candidate_hypotheses:
            break

        active_aspects = sorted(list({h.aspect_class for h in candidate_hypotheses}))
        active_prefixes = set()
        for h in candidate_hypotheses:
            if h.prefix_class in ("a_stem", "k_a_stem"):
                active_prefixes.add("a_stem")
                active_prefixes.add("k_a_stem")
            else:
                active_prefixes.add(h.prefix_class)
        active_prefixes = sorted(list(active_prefixes))
        active_t_pres = sorted(list({h.tense_present_class for h in candidate_hypotheses}))

        dyn_constraints = [
            FeatureConstraint("aspect_class", MatchMode.EXACT if len(active_aspects) == 1 else MatchMode.ONE_OF, active_aspects),
            FeatureConstraint("prefix_class", MatchMode.EXACT if len(active_prefixes) == 1 else MatchMode.ONE_OF, active_prefixes),
            FeatureConstraint("tense_present_class", MatchMode.EXACT if len(active_t_pres) == 1 else MatchMode.ONE_OF, active_t_pres),
        ]
        meta_ids = [form_spec.meta_label_id]
        if len({h.set_a for h in candidate_hypotheses}) == 1:
            if next(iter(candidate_hypotheses)).set_a and form_spec.allows_set_a:
                meta_ids.append("[PRONOUN_SET=A]")
        if len({h.plural for h in candidate_hypotheses}) == 1:
            meta_ids.append("[PLURAL=TRUE]" if next(iter(candidate_hypotheses)).plural else "[PLURAL=FALSE]")

        parses = compiler.parse_with_lattice(surface, meta_ids, dynamic_constraints=dyn_constraints)
        if not parses:
            return set()

        # Group parses by (p_asp, p_t_pres)
        parsed_by_asp_tense: Dict[Tuple[str, str], List[Tuple[ParseData, VerbTemplate, str, bool, bool, bool, bool, int]]] = {}
        for p in parses:
            p_data = parse_string_to_parse_data(p)
            p_tmpl = VerbTemplate.from_parse(p_data)
            p_pref = p_tmpl.prefix_class
            p_asp = p_tmpl.aspect_class
            p_t_pres = p_tmpl.tense_present_class
            pro_tag = p_data.pronominal
            p_var = p_tmpl.variant
            if not p_pref or not p_asp or not p_t_pres or not pro_tag:
                continue

            pro = Pronominal.from_tag(pro_tag)
            p_plural = pro.number in ("ns", "pl", "dl")
            p_set_a = pro.pronoun_set in ("A", "transitive")
            p_trans = pro.pronoun_set == "transitive"
            p_is_glottal = is_h_alternation_trigger(pro_tag)

            has_mutation = any(tag in p_data.root for tag in H_ALT_TAGS if tag.lower() not in ("[h_none]", "[h_alt=none]"))
            if not validate_h_alternation_trigger(pro_tag, has_h_alt=has_mutation):
                continue

            key = (p_asp, p_t_pres)
            if key not in parsed_by_asp_tense:
                parsed_by_asp_tense[key] = []
            parsed_by_asp_tense[key].append((p_data, p_tmpl, pro_tag, p_plural, p_set_a, p_trans, p_is_glottal, p_var))

        surviving: Set[LexicalVerb] = set()

        for hyp in candidate_hypotheses:
            matching_items = parsed_by_asp_tense.get((hyp.aspect_class, hyp.tense_present_class))
            if not matching_items:
                continue

            for p_data, p_tmpl, pro_tag, p_plural, p_set_a, p_trans, p_is_glottal, p_var in matching_items:
                if not prefix_compat(hyp.prefix_class, p_tmpl.prefix_class):
                    continue

                # Enforce present-tense variant consistency: template_3sg.variant == template_1sg.variant
                if form_spec.meta_label_id == "[FORM=1ST_PRES]" or form_spec.name == "1st_present" or form_spec.corpus_key == "present_1sg":
                    if p_var != hyp.template.variant:
                        continue

                if p_plural != hyp.plural:
                    continue

                if form_spec.allows_set_a and not p_trans:
                    if p_set_a != hyp.set_a:
                        continue

                if form_spec.person in ("1st", "2nd"):
                    if hyp.animate_objects:
                        # Allow fallback for 2nd person imperative if transitive not available
                        if not p_trans and not (form_spec.person == "2nd" and form_spec.corpus_key == "imperative"):
                            continue
                    else:
                        if p_trans:
                            continue

                # Root compatibility check
                if p_is_glottal:
                    compatible_glottal = determine_h_alt_glottal_root(hyp.h_root, p_data.root)
                    if compatible_glottal is None:
                        continue
                    if compatible_glottal != hyp.h_root:
                        if hyp.glottal_root is not None and hyp.glottal_root != compatible_glottal:
                            continue
                        new_glottal = compatible_glottal
                        new_h_alt_tag = p_data.h_alt_tag or hyp.h_alt_tag
                    else:
                        if hyp.glottal_root is not None and hyp.glottal_root != hyp.h_root:
                            continue
                        new_glottal = hyp.h_root
                        new_h_alt_tag = p_data.h_alt_tag or hyp.h_alt_tag
                else:
                    if strip_h_alt_tags(p_data.root) != hyp.h_root:
                        continue
                    new_glottal = hyp.glottal_root
                    new_h_alt_tag = hyp.h_alt_tag

                # Fold non-shared form variant into metadata.aspect_variants
                aspect_name = p_data.aspect or form_spec.corpus_key
                new_aspect_variants = hyp.metadata.aspect_variants.with_variant(aspect_name, p_var)
                new_metadata = VerbMetadata(
                    entry_type=hyp.metadata.entry_type,
                    is_set_a=hyp.metadata.is_set_a,
                    is_plural=hyp.metadata.is_plural,
                    animate_objects=hyp.metadata.animate_objects,
                    aspect_variants=new_aspect_variants,
                )

                # Determine canonical prefix class
                p_pref = p_tmpl.prefix_class
                canon_pref = hyp.prefix_class if hyp.prefix_class != "k_a_stem" else (p_pref if p_pref != "k_a_stem" else "a_stem")
                new_template = VerbTemplate(
                    root=hyp.template.root,
                    prefix_class=canon_pref,
                    aspect_class=hyp.template.aspect_class,
                    tense_present_class=hyp.template.tense_present_class,
                    variant=hyp.template.variant,
                    distributive=hyp.template.distributive,
                    translocutive=hyp.template.translocutive,
                    h_alt_tag=hyp.template.h_alt_tag,
                )

                surviving.add(
                    LexicalVerb(
                        template=new_template,
                        metadata=new_metadata,
                        glottal_root=new_glottal,
                        h_alt_tag=new_h_alt_tag,
                    )
                )

        # If any hypotheses underwent actual H-mutation on a trigger form, reject unmutated fallbacks for the same root
        mutated_h_roots = {h.h_root for h in surviving if h.glottal_root is not None and h.glottal_root != h.h_root}
        if mutated_h_roots:
            surviving = {h for h in surviving if not (h.h_root in mutated_h_roots and h.glottal_root == h.h_root)}

        candidate_hypotheses = surviving

    return candidate_hypotheses


def derive_lexical_features_4step(
    forms: List[Tuple[str, str]],
    compiler: MetaConstraintCompiler,
    lexical_features: Set[str],
) -> Set[Tuple[str, Tuple[Tuple[str, str], ...]]]:
    """
    Executes the 4-step derivation algorithm with dynamic meta-label propagation:
    Step 1 & 1a: Parse initial form with [FORM=...] flag and map meta label string to target label feature flags.
    Step 2: For each candidate derivation from the parse output graph, run the meta label FST backwards
            to get the possible metalabels.
    Step 3: Create the restricted set of possible labels for non-FORM features and derive active meta-labels
            (e.g., [PRONOUN_SET=A/B], [PLURAL=TRUE/FALSE]).
    Step 4: Parse each subsequent form using dynamic_constraints from discovered lexical features and active meta-labels
            via build_query_lattice / FST composition.
    """
    hypotheses = derive_hypotheses_for_forms(forms, compiler, lexical_features)
    return {h.lexical_tuple() for h in hypotheses}


