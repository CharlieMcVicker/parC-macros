"""
parse_chr_dict/meta_label_compiler.py

DEPRECATION NOTICE:
This module and the MetaConstraintCompiler / META_LABELS system are deprecated in favor of:
- Pure VerbForm and VerbEntryType domain models (parse_chr_dict.types)
- Pure surface parsing and iterative candidate pruning (parse_chr_dict.derive)
- Pure LexicalVerb forward inflection and validation (parse_chr_dict.types / reconstruct.py)

This module provides backwards-compatible shims and re-exports.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
import warnings

# Re-export pure derivation pipeline from derive.py
from parse_chr_dict.derive import (
    derive_hypotheses_for_forms,
    derive_lexical_features_4step,
    VERB_FORMS_BY_META_ID,
)

# Re-export pure types from types.py
from parse_chr_dict.types import (
    ParseData,
    VerbTemplate,
    AspectVariants,
    VerbMetadata,
    LexicalVerb,
    Pronominal,
    ALL_PRONOMINALS,
    filter_pronominals,
    VerbForm,
    ALL_VERB_FORMS,
    VERB_FORMS_BY_NAME,
    VerbEntryType,
    PRIMARY_VERB_ENTRY_TYPES,
    VERB_ENTRY_TYPES_BY_NAME,
    DerivationHypothesis,
    LexicalVerbHypothesis,
    LexicalVerbEntry,
    PRES_3RD,
    PRES_1SG,
    HABITUAL_3RD,
    COMPLETIVE_3RD,
    INCOMPLETIVE_ASSERTIVE_3RD,
    IMPERATIVE_2ND,
    FUT_PROG_2ND,
    INFINITIVE_3RD,
    EVENTFUL,
    STATIVE_FUT_PROG,
    STATIVE_NO_IMP,
)


class MatchMode(str, Enum):
    """Deprecated: Specifies how feature values should be matched in the slot."""
    EXACT = "exact"
    ONE_OF = "one_of"
    ANY = "any"
    EXCLUDE = "exclude"


@dataclass
class FeatureConstraint:
    """Deprecated: Constraint on a single morphosyntactic or lexical slot."""
    slot_name: str
    mode: MatchMode = MatchMode.EXACT
    values: List[str] = field(default_factory=list)

    def __post_init__(self):
        warnings.warn(
            "FeatureConstraint is deprecated and will be removed. Use VerbForm instead.",
            DeprecationWarning,
            stacklevel=2,
        )


@dataclass
class MetaLabelDefinition:
    """Deprecated: Definition of an abstract meta-label and its associated feature constraints."""
    id: str
    description: Optional[str] = None
    constraints: List[FeatureConstraint] = field(default_factory=list)
    priority: int = 0

    def __post_init__(self):
        warnings.warn(
            "MetaLabelDefinition is deprecated and will be removed. Use VerbForm instead.",
            DeprecationWarning,
            stacklevel=2,
        )


@dataclass
class FormParsingSpec:
    """Deprecated: Specification of a form parsing layout. Use VerbForm instead."""
    corpus_key: str
    name: str
    meta_label_id: str
    person: str
    allows_set_a: bool

    def to_verb_form(self) -> VerbForm:
        if self.name in VERB_FORMS_BY_NAME:
            return VERB_FORMS_BY_NAME[self.name]
        return VERB_FORMS_BY_META_ID.get(
            self.meta_label_id,
            VerbForm(
                name=self.name,
                corpus_key=self.corpus_key,
                aspect="present",
                tense="present",
                person=self.person,
                allows_set_a=self.allows_set_a,
            ),
        )

    def matches(self, p: ParseData) -> bool:
        return self.to_verb_form().matches(p)


@dataclass
class EntryTypeSpec:
    """Deprecated: Specifies entry type and associated forms. Use VerbEntryType instead."""
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

ENTRY_TYPES_BY_NAME: Dict[str, EntryTypeSpec] = {e.name: e for e in PRIMARY_ENTRY_TYPES + SHIM_ENTRY_TYPES}


# Deprecated pre-defined Meta Labels
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
    DEPRECATED: Legacy FST tag acceptor compiler.
    Retire in favor of pure VerbForm matching and derive_hypotheses_for_forms.
    """

    def __init__(
        self,
        base_tag_acceptor: Optional[Any] = None,
        sigma_star: Optional[Any] = None,
        symbol_table: Optional[Any] = None,
        meta_registry: Optional[Dict[str, MetaLabelDefinition]] = None,
    ):
        warnings.warn(
            "MetaConstraintCompiler is deprecated and will be removed. "
            "Use VerbForm, VerbEntryType, and derive_hypotheses_for_forms instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.meta_registry = meta_registry if meta_registry is not None else META_LABELS
        self._parse_cache: Dict[Any, List[str]] = {}

    def parse_surface(
        self,
        surface: str,
        parse_graph: Optional[Any] = None,
    ) -> List[str]:
        from parse_chr_dict.parse import parse_surface
        return parse_surface(surface, parse_graph=parse_graph)

    def get_feature_tuples_from_meta(self, meta_label_ids: List[str]) -> List[Tuple[str, str]]:
        tuples = []
        for meta_id in meta_label_ids:
            if meta_id in self.meta_registry:
                for c in self.meta_registry[meta_id].constraints:
                    if c.mode == MatchMode.EXACT and len(c.values) == 1:
                        tuples.append((c.slot_name, c.values[0]))
        return tuples

    def infer_meta_labels_from_parse(self, parse_str: str) -> List[str]:
        from parse_chr_dict.parse import read_labels
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
