from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
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


class MatchMode(str, Enum):
    """Specifies how feature values should be matched in the slot."""
    EXACT = "exact"
    ONE_OF = "one_of"
    ANY = "any"
    EXCLUDE = "exclude"


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
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["3sg.A", "3sg.B"]),
        ],
    ),
    "[FORM=1ST_PRES]": MetaLabelDefinition(
        id="[FORM=1ST_PRES]",
        description="1st person present form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["present"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["present"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["1sg.A", "1sg.B", "1sg>3sg"]),
        ],
    ),
    "[FORM=3RD_HABITUAL]": MetaLabelDefinition(
        id="[FORM=3RD_HABITUAL]",
        description="3rd person habitual form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["habitual"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["incompletive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["3sg.A", "3sg.B"]),
        ],
    ),
    "[FORM=3RD_COMPLETIVE]": MetaLabelDefinition(
        id="[FORM=3RD_COMPLETIVE]",
        description="3rd person completive assertive form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["assertive"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["completive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.EXACT, values=["3sg.B"]),
        ],
    ),
    "[FORM=3RD_INCOMPLETIVE_ASSERTIVE]": MetaLabelDefinition(
        id="[FORM=3RD_INCOMPLETIVE_ASSERTIVE]",
        description="3rd person incompletive assertive form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["assertive"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["incompletive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["3sg.A", "3sg.B"]),
        ],
    ),
    "[FORM=2ND_IMPERATIVE]": MetaLabelDefinition(
        id="[FORM=2ND_IMPERATIVE]",
        description="2nd person immediate imperative form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["immediate"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["immediate"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["2sg.A", "2sg.B", "2sg>3sg"]),
        ],
    ),
    "[FORM=2ND_FUT_PROG]": MetaLabelDefinition(
        id="[FORM=2ND_FUT_PROG]",
        description="2nd person future progressive form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["future_prog"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["incompletive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["2sg.A", "2sg.B", "2sg>3sg"]),
        ],
    ),
    "[FORM=3RD_INFINITIVE]": MetaLabelDefinition(
        id="[FORM=3RD_INFINITIVE]",
        description="3rd person infinitive form",
        constraints=[
            FeatureConstraint(slot_name="tense", mode=MatchMode.EXACT, values=["infinitive"]),
            FeatureConstraint(slot_name="aspect", mode=MatchMode.EXACT, values=["infinitive"]),
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.EXACT, values=["3sg.B"]),
        ],
    ),
    "[PRONOUN_SET=A]": MetaLabelDefinition(
        id="[PRONOUN_SET=A]",
        description="Pronoun Set A constraint",
        constraints=[
            FeatureConstraint(slot_name="pronominal", mode=MatchMode.ONE_OF, values=["3sg.A", "1sg.A", "2sg.A"]),
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

    def build_slot_mask(self, constraint: FeatureConstraint) -> pynini.Fst:
        """
        Compiles an unanchored feature-slot constraint acceptor:
        F_slot = Sigma* . [slot_name=value] . Sigma*
        """
        if constraint.mode == MatchMode.ONE_OF:
            slot_patterns = [feature_tag(constraint.slot_name, val) for val in constraint.values]
            target_fsa = pynini.union(*[pynini.accep(p, token_type=self.symbol_table) for p in slot_patterns])
        elif constraint.mode == MatchMode.EXACT:
            target_fsa = pynini.accep(
                feature_tag(constraint.slot_name, constraint.values[0]),
                token_type=self.symbol_table,
            )
        else:
            raise NotImplementedError(f"Constraint mode {constraint.mode} not supported yet.")

        return pynini.optimize(pynini.concat(self.sigma_star, pynini.concat(target_fsa, self.sigma_star)))

    def compile_restricted_tag_acceptor(self, meta_label_ids: List[str]) -> pynini.Fst:
        """
        Intersects parC's base morphotactic tag acceptor (or Sigma*) with active meta constraints:
        L_restricted = L_base ∩ F_1 ∩ F_2 ∩ ... ∩ F_n
        """
        restricted_fsa = (
            self.base_tag_acceptor.copy()
            if self.base_tag_acceptor is not None
            else self.sigma_star.copy()
        )

        all_constraints: List[FeatureConstraint] = []
        for meta_id in meta_label_ids:
            if meta_id in self.meta_registry:
                all_constraints.extend(self.meta_registry[meta_id].constraints)

        for constraint in all_constraints:
            slot_mask = self.build_slot_mask(constraint)
            restricted_fsa = pynini.intersect(restricted_fsa, slot_mask)
            restricted_fsa.optimize()

        return restricted_fsa

    def get_feature_tuples_from_meta(self, meta_label_ids: List[str]) -> List[Tuple[str, str]]:
        """
        Maps meta label strings to target feature label flag tuples (Step 1a).
        """
        tuples = []
        for meta_id in meta_label_ids:
            if meta_id in self.meta_registry:
                for c in self.meta_registry[meta_id].constraints:
                    if c.mode == MatchMode.EXACT and len(c.values) == 1:
                        tuples.append((c.slot_name, c.values[0]))
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


def derive_lexical_features_4step(
    forms: List[Tuple[str, str]],
    compiler: MetaConstraintCompiler,
    lexical_features: Set[str],
) -> Set[Tuple[str, Tuple[Tuple[str, str], ...]]]:
    """
    Executes the 4-step derivation algorithm:
    Step 1 & 1a: Parse initial form with [FORM=...] flag and map meta label string to target label feature flags.
    Step 2: For each candidate derivation from the parse output graph, run the meta label FST backwards
            to get the possible metalabels.
    Step 3: Create the restricted set of possible labels for non-FORM features (e.g. aspect_class, prefix_class, etc.).
    Step 4: Parse each subsequent form using the restricted metalabels.
    """
    if not forms:
        return set()

    # Step 1 & 1a: Initial form
    init_surface, init_meta_id = forms[0]
    init_target_labels = compiler.get_feature_tuples_from_meta([init_meta_id])
    
    # Parse initial form with target label feature flags
    from parse_chr_dict.parse import parse
    init_parses = parse(init_surface, labels=init_target_labels)

    # Step 2 & 3: For each candidate derivation, obtain possible metalabels and create restricted non-FORM feature set
    init_lexicals: Set[Tuple[str, Tuple[Tuple[str, str], ...]]] = set()
    for p in init_parses:
        # Step 2: Metalabel backwards check
        metalabels = compiler.infer_meta_labels_from_parse(p)
        if init_meta_id in metalabels or not compiler.meta_registry.get(init_meta_id):
            # Step 3: Extract non-FORM lexical features
            lex_item = str_to_lexical_hashable(p, lexical_features=lexical_features)
            init_lexicals.add(lex_item)

    if len(forms) == 1:
        return init_lexicals

    # Step 4: Parse each subsequent form using the restricted metalabels
    candidate_lexicals = init_lexicals
    for surface, meta_id in forms[1:]:
        if not surface:
            continue
        subseq_target_labels = compiler.get_feature_tuples_from_meta([meta_id])
        subseq_parses = parse(surface, labels=subseq_target_labels)
        
        subseq_lexicals = set()
        for p in subseq_parses:
            metalabels = compiler.infer_meta_labels_from_parse(p)
            if meta_id in metalabels or not compiler.meta_registry.get(meta_id):
                lex_item = str_to_lexical_hashable(p, lexical_features=lexical_features)
                subseq_lexicals.add(lex_item)

        candidate_lexicals = candidate_lexicals.intersection(subseq_lexicals)

    return candidate_lexicals
