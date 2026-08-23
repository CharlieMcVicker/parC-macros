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


@dataclass(frozen=True)
class Pronominal:
    """Structured representation of a pronominal tag (e.g. 3sg.A, 1sg>3sg, 3ns.B)."""
    tag: str
    person: str        # "1st", "2nd", "3rd"
    number: str        # "sg", "ns", "pl"
    pronoun_set: str   # "A", "B", "transitive"

    @classmethod
    def from_tag(cls, tag: str) -> Pronominal:
        if ">" in tag:
            subj = tag.split(">")[0]
            person = "1st" if subj.startswith("1") else "2nd" if subj.startswith("2") else "3rd"
            return cls(tag=tag, person=person, number="sg", pronoun_set="transitive")

        # Standard tags: 3sg.A, 1sg.B, 3ns.A, E.A, Epl.A, etc.
        parts = tag.split(".")
        prefix = parts[0]
        pronoun_set = parts[1] if len(parts) > 1 else "A"

        if prefix.startswith("1") or prefix.startswith("E"):
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
        "E.A", "E.B", "Epl.A", "Epl.B", "Edl.A", "Edl.B",
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

    def build_slot_mask(self, constraint: FeatureConstraint) -> pynini.Fst:
        """
        Compiles an unanchored feature-slot constraint acceptor:
        F_slot = Sigma* . [slot_name=value] . Sigma*
        """
        if not constraint.values:
            return pynini.Fst()

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

        return pynini.optimize(pynini.concat(self.sigma_star, pynini.concat(target_fsa, self.sigma_star)))

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
        restricted_fsa = (
            self.base_tag_acceptor.copy()
            if self.base_tag_acceptor is not None
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

        return restricted_fsa

    def build_query_lattice(
        self,
        surface_form: str,
        meta_label_ids: List[str],
        dynamic_constraints: Optional[List[FeatureConstraint]] = None,
    ) -> pynini.Fst:
        """
        Builds query lattice Q = surface_fsa . L_restricted
        """
        L_restricted = self.compile_restricted_tag_acceptor(
            meta_label_ids, dynamic_constraints=dynamic_constraints
        )
        surface_fsa = word_fsa(surface_form)
        return pynini.optimize(pynini.concat(surface_fsa, L_restricted))

    def parse_with_lattice(
        self,
        surface_form: str,
        meta_label_ids: List[str],
        dynamic_constraints: Optional[List[FeatureConstraint]] = None,
        parse_graph: Optional[pynini.Fst] = None,
    ) -> List[str]:
        """
        Executes Q o P composition directly via Pynini.
        Q = surface_fsa . L_restricted
        P = parse_graph (open parse graph)
        """
        if parse_graph is None:
            from parse_chr_dict.parse import get_parse_graph
            parse_graph = get_parse_graph()

        Q = self.build_query_lattice(
            surface_form, meta_label_ids, dynamic_constraints=dynamic_constraints
        )
        output_lattice = pynini.compose(Q, parse_graph).optimize()
        output_lattice = pynini.project(output_lattice, project_type="output")
        return fsm_strings(output_lattice, strip_all_tags=False)

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
    Executes the 4-step derivation algorithm with dynamic meta-label propagation:
    Step 1 & 1a: Parse initial form with [FORM=...] flag and map meta label string to target label feature flags.
    Step 2: For each candidate derivation from the parse output graph, run the meta label FST backwards
            to get the possible metalabels.
    Step 3: Create the restricted set of possible labels for non-FORM features and derive active meta-labels
            (e.g., [PRONOUN_SET=A/B], [PLURAL=TRUE/FALSE]).
    Step 4: Parse each subsequent form using dynamic_constraints from discovered lexical features and active meta-labels
            via build_query_lattice / FST composition.
    """
    if not forms:
        return set()

    # Helper mapping from meta_id -> FormParsingSpec
    spec_by_meta = {p.meta_label_id: p for p in FORMS_TO_PARSE}

    # Step 1 & 1a: Initial form
    init_surface, init_meta_id = forms[0]
    init_parses = compiler.parse_with_lattice(init_surface, [init_meta_id])

    # Step 2 & 3: Obtain possible metalabels and create restricted feature set + meta label candidates
    init_lexicals: Set[Tuple[str, Tuple[Tuple[str, str], ...]]] = set()
    parse_meta_list: List[Set[str]] = []

    init_spec = spec_by_meta.get(init_meta_id)
    for p in init_parses:
        metalabels = set(compiler.infer_meta_labels_from_parse(p))
        if init_meta_id in metalabels or not compiler.meta_registry.get(init_meta_id):
            lex_item = str_to_lexical_hashable(p, lexical_features=lexical_features)
            init_lexicals.add(lex_item)
            parse_meta_list.append(metalabels)

    if len(forms) == 1:
        return init_lexicals

    # Step 4: Parse each subsequent form using dynamic constraints + meta-label propagation + lattice composition
    candidate_lexicals = init_lexicals

    for surface, meta_id in forms[1:]:
        if not surface:
            continue

        form_spec = spec_by_meta.get(meta_id)

        # Infer unambiguous meta-labels from current parse candidates (labels common to all parses)
        unambiguous_meta: Set[str] = set.intersection(*parse_meta_list) if parse_meta_list else set()

        # Assemble meta label IDs for this form
        meta_ids_for_form = [meta_id]
        for m in sorted(unambiguous_meta):
            if m.startswith("[PRONOUN_SET="):
                if form_spec and form_spec.allows_set_a:
                    meta_ids_for_form.append(m)
            elif m.startswith("[PLURAL="):
                meta_ids_for_form.append(m)

        # Construct dynamic constraints from currently discovered lexical features
        dynamic_constraints = []
        for feat in sorted(lexical_features):
            vals = set(v for _, label_tuple in candidate_lexicals for s, v in label_tuple if s == feat)
            if feat == "prefix_class":
                if "k_a_stem" in vals or "a_stem" in vals:
                    vals.add("k_a_stem")
                    vals.add("a_stem")
            sorted_vals = sorted(list(vals))
            if sorted_vals:
                mode = MatchMode.EXACT if len(sorted_vals) == 1 else MatchMode.ONE_OF
                dynamic_constraints.append(FeatureConstraint(slot_name=feat, mode=mode, values=sorted_vals))

        subseq_parses = compiler.parse_with_lattice(
            surface, meta_ids_for_form, dynamic_constraints=dynamic_constraints
        )

        subseq_lexicals = set()
        subseq_meta_list = []
        for p in subseq_parses:
            metalabels = set(compiler.infer_meta_labels_from_parse(p))
            if meta_id in metalabels or not compiler.meta_registry.get(meta_id):
                lex_item = str_to_lexical_hashable(p, lexical_features=lexical_features)
                subseq_lexicals.add(lex_item)
                subseq_meta_list.append(metalabels)

        candidate_lexicals = candidate_lexicals.intersection(subseq_lexicals)
        if subseq_meta_list:
            parse_meta_list = subseq_meta_list

    return candidate_lexicals

