from dataclasses import dataclass


@dataclass
class FormParsing:
    """Spec for how to parse a form + a name"""

    corpus_key: str
    name: str
    lexical_features: list[tuple]

    # fields used for reconstruction
    person: str
    allows_set_a: bool


@dataclass
class EntryType:
    """A set of forms to parse from a row"""

    name: str
    """Name for the spec"""

    forms: list[str]
    """Names of FormParsings to use"""

    def get_forms_from_parses(self, form_parses):
        return [form_parses[name][1] for name in self.forms if name in form_parses]


FORMS_TO_PARSE: list[FormParsing] = [
    FormParsing(
        corpus_key="present",
        name="3rd_present",
        lexical_features=[
            ("tense", "present"),
            ("aspect", "present"),
        ],
        person="3rd",
        allows_set_a=True,
    ),
    FormParsing(
        corpus_key="present_1sg",
        name="1st_present",
        lexical_features=[
            ("tense", "present"),
            ("aspect", "present"),
        ],
        person="1st",
        allows_set_a=True,
    ),
    FormParsing(
        corpus_key="imperfective",
        name="3rd_incompletive_habitual",
        lexical_features=[
            ("tense", "habitual"),
            ("aspect", "incompletive"),
        ],
        person="3rd",
        allows_set_a=True,
    ),
    FormParsing(
        corpus_key="perfective",
        name="3rd_completive_assertive",
        lexical_features=[
            ("tense", "assertive"),
            ("aspect", "completive"),
        ],
        person="3rd",
        allows_set_a=False,
    ),
    FormParsing(
        corpus_key="perfective",
        name="3rd_incompletive_assertive",
        lexical_features=[
            ("tense", "assertive"),
            ("aspect", "incompletive"),
        ],
        person="3rd",
        allows_set_a=True,
    ),
    FormParsing(
        corpus_key="imperative",
        name="2nd_imperative",
        lexical_features=[
            ("tense", "immediate"),
            ("aspect", "immediate"),
        ],
        person="2nd",
        allows_set_a=True,
    ),
    FormParsing(
        corpus_key="imperative",
        name="2nd_future_prog",
        lexical_features=[
            ("tense", "future_prog"),
            ("aspect", "incompletive"),
        ],
        person="2nd",
        allows_set_a=True,
    ),
    FormParsing(
        corpus_key="infinitive",
        name="3rd_infinitive",
        lexical_features=[
            ("tense", "infinitive"),
            ("aspect", "infinitive"),
        ],
        person="3rd",
        allows_set_a=False,
    ),
]

PRIMARY_ENTRY_TYPES = [
    EntryType(
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
    EntryType(
        name="StativeFutProg",
        forms=[
            "3rd_present",
            "1st_present",
            "3rd_incompletive_habitual",
            "3rd_completive_assertive",
            "2nd_future_prog",
        ],
    ),
    EntryType(
        name="StativeNoImp",
        forms=[
            "3rd_present",
            "1st_present",
            "3rd_incompletive_habitual",
            "3rd_completive_assertive",
        ],
    ),
]

SHIM_ENTRY_TYPES = [
    EntryType(
        name="EventfulInfinitive",
        forms=["3rd_infinitive"],
    ),
    EntryType(
        name="EventfulImperativeInfinitive",
        forms=["2nd_imperative", "3rd_infinitive"],
    ),
]
