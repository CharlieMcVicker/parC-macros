from __future__ import annotations
import pytest
from dataclasses import FrozenInstanceError

from parse_chr_dict.types import (
    ParseData,
    Pronominal,
    filter_pronominals,
    VerbForm,
    VerbEntryType,
    VerbMetadata,
    LexicalVerb,
    VerbTemplate,
    ALL_VERB_FORMS,
    VERB_FORMS_BY_NAME,
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
    PRIMARY_VERB_ENTRY_TYPES,
    VERB_ENTRY_TYPES_BY_NAME,
)


def test_pronominal_parsing_and_filtering():
    """Verify Pronominal struct and functional filter predicates in types.py."""
    p_3sg_a = Pronominal.from_tag("3sg.A")
    assert p_3sg_a.tag == "3sg.A"
    assert p_3sg_a.person == "3rd"
    assert p_3sg_a.number == "sg"
    assert p_3sg_a.pronoun_set == "A"

    p_trans = Pronominal.from_tag("1sg>3sg")
    assert p_trans.person == "1st"
    assert p_trans.number == "sg"
    assert p_trans.pronoun_set == "transitive"

    p_2dl_b = Pronominal.from_tag("2dl.B")
    assert p_2dl_b.person == "2nd"
    assert p_2dl_b.number == "dl"
    assert p_2dl_b.pronoun_set == "B"

    # filter_pronominals
    a_3rd = filter_pronominals(person="3rd", pronoun_set="A")
    assert "3sg.A" in a_3rd
    assert "3ns.A" in a_3rd
    assert "3dl.A" in a_3rd
    assert "3sg.B" not in a_3rd

    transitive_1st = filter_pronominals(person="1st", pronoun_set="transitive")
    assert transitive_1st == ["1sg>3sg"]

    transitive_2nd = filter_pronominals(person="2nd", pronoun_set="transitive")
    assert transitive_2nd == ["2sg>3sg"]


def test_verb_form_definitions_and_immutability():
    """Verify standard VerbForm constants and frozen behavior."""
    assert len(ALL_VERB_FORMS) == 8
    assert set(VERB_FORMS_BY_NAME.keys()) == {
        "3rd_present",
        "1st_present",
        "3rd_incompletive_habitual",
        "3rd_completive_assertive",
        "3rd_incompletive_assertive",
        "2nd_imperative",
        "2nd_future_prog",
        "3rd_infinitive",
    }

    assert PRES_3RD.name == "3rd_present"
    assert PRES_3RD.corpus_key == "present"
    assert PRES_3RD.aspect == "present"
    assert PRES_3RD.tense == "present"
    assert PRES_3RD.person == "3rd"
    assert PRES_3RD.allows_set_a is True

    assert COMPLETIVE_3RD.name == "3rd_completive_assertive"
    assert COMPLETIVE_3RD.corpus_key == "perfective"
    assert COMPLETIVE_3RD.aspect == "completive"
    assert COMPLETIVE_3RD.tense == "assertive"
    assert COMPLETIVE_3RD.person == "3rd"
    assert COMPLETIVE_3RD.allows_set_a is False

    assert INFINITIVE_3RD.name == "3rd_infinitive"
    assert INFINITIVE_3RD.corpus_key == "infinitive"
    assert INFINITIVE_3RD.aspect == "infinitive"
    assert INFINITIVE_3RD.tense == "infinitive"
    assert INFINITIVE_3RD.person == "3rd"
    assert INFINITIVE_3RD.allows_set_a is False

    with pytest.raises(FrozenInstanceError):
        PRES_3RD.aspect = "completive"


def test_verb_form_matching():
    """Verify matches method against various ParseData instances."""
    # 3rd Present
    p_pres_3a = ParseData(root="ga", aspect="present", tense="present", pronominal="3sg.A")
    p_pres_3b = ParseData(root="ga", aspect="present", tense="present", pronominal="3sg.B")
    p_pres_1a = ParseData(root="ga", aspect="present", tense="present", pronominal="1sg.A")
    p_comp_3b = ParseData(root="ga", aspect="completive", tense="assertive", pronominal="3sg.B")
    p_comp_3a = ParseData(root="ga", aspect="completive", tense="assertive", pronominal="3sg.A")

    assert PRES_3RD.matches(p_pres_3a) is True
    assert PRES_3RD.matches(p_pres_3b) is True
    assert PRES_3RD.matches(p_pres_1a) is False  # Wrong person
    assert PRES_3RD.matches(p_comp_3b) is False  # Wrong aspect/tense

    # 1st Present
    assert PRES_1SG.matches(p_pres_1a) is True
    assert PRES_1SG.matches(p_pres_3a) is False

    # 3rd Completive (allows_set_a=False)
    assert COMPLETIVE_3RD.matches(p_comp_3b) is True
    assert COMPLETIVE_3RD.matches(p_comp_3a) is False  # Set A disallowed for completive
    p_comp_3ns_b = ParseData(root="ga", aspect="completive", tense="assertive", pronominal="3ns.B")
    assert COMPLETIVE_3RD.matches(p_comp_3ns_b) is True

    # Incompletive Assertive
    p_inc_ass = ParseData(root="ga", aspect="incompletive", tense="assertive", pronominal="3sg.A")
    assert INCOMPLETIVE_ASSERTIVE_3RD.matches(p_inc_ass) is True
    assert INCOMPLETIVE_ASSERTIVE_3RD.matches(p_comp_3b) is False

    # Habitual
    p_hab = ParseData(root="ga", aspect="incompletive", tense="habitual", pronominal="3sg.A")
    assert HABITUAL_3RD.matches(p_hab) is True
    assert HABITUAL_3RD.matches(p_inc_ass) is False

    # Imperative 2nd
    p_imp_2a = ParseData(root="ga", aspect="immediate", tense="immediate", pronominal="2sg.A")
    p_imp_2b = ParseData(root="ga", aspect="immediate", tense="immediate", pronominal="2sg.B")
    p_imp_trans = ParseData(root="ga", aspect="immediate", tense="immediate", pronominal="2sg>3sg")
    assert IMPERATIVE_2ND.matches(p_imp_2a) is True
    assert IMPERATIVE_2ND.matches(p_imp_2b) is True
    assert IMPERATIVE_2ND.matches(p_imp_trans) is True
    assert IMPERATIVE_2ND.matches(p_pres_3a) is False

    # Future Progressive 2nd
    p_fut_prog = ParseData(root="ga", aspect="incompletive", tense="future_prog", pronominal="2sg.A")
    assert FUT_PROG_2ND.matches(p_fut_prog) is True
    assert FUT_PROG_2ND.matches(p_imp_2a) is False

    # Infinitive 3rd (allows_set_a=False)
    p_inf_b = ParseData(root="ga", aspect="infinitive", tense="infinitive", pronominal="3sg.B")
    p_inf_a = ParseData(root="ga", aspect="infinitive", tense="infinitive", pronominal="3sg.A")
    assert INFINITIVE_3RD.matches(p_inf_b) is True
    assert INFINITIVE_3RD.matches(p_inf_a) is False

    # Empty pronominal
    p_empty = ParseData(root="ga", aspect="present", tense="present", pronominal="")
    assert PRES_3RD.matches(p_empty) is False


def test_verb_entry_type_definitions():
    """Verify VerbEntryType specifications and form groupings."""
    assert EVENTFUL.name == "Eventful"
    assert len(EVENTFUL.forms) == 6
    assert EVENTFUL.forms == (
        PRES_3RD,
        PRES_1SG,
        HABITUAL_3RD,
        COMPLETIVE_3RD,
        IMPERATIVE_2ND,
        INFINITIVE_3RD,
    )
    assert len(EVENTFUL) == 6
    assert list(iter(EVENTFUL)) == list(EVENTFUL.forms)
    assert EVENTFUL.get_form("3rd_present") == PRES_3RD
    assert EVENTFUL.get_form("2nd_future_prog") is None

    assert STATIVE_FUT_PROG.name == "StativeFutProg"
    assert len(STATIVE_FUT_PROG.forms) == 5
    assert STATIVE_FUT_PROG.forms == (
        PRES_3RD,
        PRES_1SG,
        HABITUAL_3RD,
        COMPLETIVE_3RD,
        FUT_PROG_2ND,
    )

    assert STATIVE_NO_IMP.name == "StativeNoImp"
    assert len(STATIVE_NO_IMP.forms) == 4
    assert STATIVE_NO_IMP.forms == (
        PRES_3RD,
        PRES_1SG,
        HABITUAL_3RD,
        COMPLETIVE_3RD,
    )

    assert PRIMARY_VERB_ENTRY_TYPES == [EVENTFUL, STATIVE_FUT_PROG, STATIVE_NO_IMP]
    assert VERB_ENTRY_TYPES_BY_NAME["Eventful"] == EVENTFUL
    assert VERB_ENTRY_TYPES_BY_NAME["StativeFutProg"] == STATIVE_FUT_PROG
    assert VERB_ENTRY_TYPES_BY_NAME["StativeNoImp"] == STATIVE_NO_IMP

    with pytest.raises(FrozenInstanceError):
        EVENTFUL.name = "Modified"


def test_verb_metadata_pronominal_candidates():
    """Verify VerbMetadata.get_pronominal_candidates and get_pronominal across paradigm variants."""
    # Set A singular
    meta_a = VerbMetadata(is_set_a=True, is_plural=False, animate_objects=False)
    assert meta_a.get_pronominal_candidates("3rd", allow_set_a=True) == ["3sg.A"]
    assert meta_a.get_pronominal_candidates("3rd", allow_set_a=False) == ["3sg.B"]
    assert meta_a.get_pronominal_candidates("1st", allow_set_a=True) == ["1sg.A"]
    assert meta_a.get_pronominal_candidates("2nd", allow_set_a=True) == ["2sg.A"]
    assert meta_a.get_pronominal("3rd", allow_set_a=True) == "3sg.A"
    assert meta_a.get_pronominal("3rd", allow_set_a=False) == "3sg.B"

    # Set B singular
    meta_b = VerbMetadata(is_set_a=False, is_plural=False, animate_objects=False)
    assert meta_b.get_pronominal_candidates("3rd", allow_set_a=True) == ["3sg.B"]
    assert meta_b.get_pronominal_candidates("3rd", allow_set_a=False) == ["3sg.B"]
    assert meta_b.get_pronominal_candidates("1st", allow_set_a=True) == ["1sg.B"]
    assert meta_b.get_pronominal_candidates("2nd", allow_set_a=True) == ["2sg.B"]
    assert meta_b.get_pronominal("3rd", allow_set_a=True) == "3sg.B"

    # Plural Set A
    meta_plural_a = VerbMetadata(is_set_a=True, is_plural=True, animate_objects=False)
    assert meta_plural_a.get_pronominal_candidates("3rd", allow_set_a=True) == ["3ns.A", "3dl.A"]
    assert meta_plural_a.get_pronominal_candidates("3rd", allow_set_a=False) == ["3ns.B", "3dl.B"]
    assert meta_plural_a.get_pronominal_candidates("1st", allow_set_a=True) == ["Epl.A", "Edl.A", "1pl.A", "1dl.A"]
    assert meta_plural_a.get_pronominal_candidates("2nd", allow_set_a=True) == ["2pl.A", "2dl.A"]
    assert meta_plural_a.get_pronominal("3rd", allow_set_a=True) == "3ns.A"

    # Plural Set B
    meta_plural_b = VerbMetadata(is_set_a=False, is_plural=True, animate_objects=False)
    assert meta_plural_b.get_pronominal_candidates("3rd", allow_set_a=True) == ["3ns.B", "3dl.B"]
    assert meta_plural_b.get_pronominal_candidates("1st", allow_set_a=True) == ["Epl.B", "Edl.B", "1pl.B", "1dl.B"]
    assert meta_plural_b.get_pronominal_candidates("2nd", allow_set_a=True) == ["2pl.B", "2dl.B"]

    # Animate transitive
    meta_anim = VerbMetadata(is_set_a=True, is_plural=False, animate_objects=True)
    assert meta_anim.get_pronominal_candidates("1st", allow_set_a=True) == ["1sg>3sg"]
    assert meta_anim.get_pronominal("1st", allow_set_a=True) == "1sg>3sg"
    assert meta_anim.get_pronominal_candidates("2nd", allow_set_a=True) == ["2sg>3sg", "2sg.A"]
    assert meta_anim.get_pronominal_candidates("2nd", allow_set_a=False) == ["2sg>3sg", "2sg.B"]
    assert meta_anim.get_pronominal_candidates("3rd", allow_set_a=True) == ["3sg.A"]
    assert meta_anim.get_pronominal_candidates("3rd", allow_set_a=False) == ["3sg.B"]


def test_verb_metadata_all_combinations():
    """Verify VerbMetadata.all_combinations generates exactly 6 combinations with correct properties."""
    combos = list(VerbMetadata.all_combinations())
    assert len(combos) == 6
    for c in combos:
        assert isinstance(c, VerbMetadata)
        assert c.set_a == c.is_set_a
        assert c.plural == c.is_plural
        if c.is_plural:
            assert c.animate_objects is False
        # Each combination generates valid pronominal candidates
        for person in ("1st", "2nd", "3rd"):
            for allow_a in (True, False):
                candidates = c.get_pronominal_candidates(person, allow_a)
                assert len(candidates) > 0
                pro = c.get_pronominal(person, allow_a)
                assert pro in candidates


def test_lexical_verb_inflect_and_validate_form():
    """Test LexicalVerb.inflect_form and validate_form against real Cherokee entry."""
    verb = LexicalVerb(
        h_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )

    # inflect_form tests
    pres_forms = verb.inflect_form(PRES_3RD)
    assert isinstance(pres_forms, list)
    assert "atateka" in pres_forms

    pres_1sg_forms = verb.inflect_form(PRES_1SG)
    assert "katateka" in pres_1sg_forms

    imp_forms = verb.inflect_form(IMPERATIVE_2ND)
    assert "hatatuka" in imp_forms

    # validate_form tests
    assert verb.validate_form(PRES_3RD, "atateka") is True
    assert verb.validate_form(PRES_1SG, "katateka") is True
    assert verb.validate_form(HABITUAL_3RD, "atateko'i") is True
    assert verb.validate_form(COMPLETIVE_3RD, "utatinvsv'i") is True
    assert verb.validate_form(IMPERATIVE_2ND, "hatatuka") is True
    assert verb.validate_form(INFINITIVE_3RD, "utatinvti") is True

    # Invalid surface forms should fail validation
    assert verb.validate_form(PRES_3RD, "wrongform") is False
    assert verb.validate_form(PRES_1SG, "atateka") is False


def test_lexical_verb_integration():
    """Verify LexicalVerb exposes pronominal resolution directly."""
    tmpl = VerbTemplate(root="ali")
    meta = VerbMetadata(is_set_a=True, is_plural=False, animate_objects=False)
    verb = LexicalVerb(template=tmpl, metadata=meta)

    assert verb.get_pronominal_candidates("3rd", allow_set_a=True) == ["3sg.A"]
    assert verb.get_pronominal_candidates("3rd", allow_set_a=False) == ["3sg.B"]
    assert verb.get_pronominal("3rd", allow_set_a=True) == "3sg.A"
