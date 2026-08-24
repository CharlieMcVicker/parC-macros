import pytest
from parse_chr_dict.h_alternation import (
    is_h_alternation_trigger,
    grades_are_compatible,
    possible_alternates,
    prevent_C_glottal_cluster,
    recreate_C_glottal_clusters,
    _drop_first_h,
    _first_h_to_glottal,
    _drop_h_in_deaffricated_lateral,
    _is_compatible_with_vowel_restoration,
)


def test_h_alternation_triggers():
    assert is_h_alternation_trigger("1sg>3sg") is True
    assert is_h_alternation_trigger("2sg>3sg") is True
    assert is_h_alternation_trigger("1sg.A") is True

    # Other pronominals do not trigger H-alternation
    assert is_h_alternation_trigger("3sg.A") is False
    assert is_h_alternation_trigger("2sg.A") is False
    assert is_h_alternation_trigger("3ns.A") is False
    assert is_h_alternation_trigger("1sg.B") is False
    assert is_h_alternation_trigger("2sg.B") is False
    assert is_h_alternation_trigger("3sg.B") is False
    assert is_h_alternation_trigger("3ns.B") is False
    assert is_h_alternation_trigger("Epl.A") is False
    assert is_h_alternation_trigger("Edl.A") is False


def test_drop_first_h():
    assert _drop_first_h("ahne") == "ane"
    assert _drop_first_h("noh") == "no"
    assert _drop_first_h("gawoniha") == "gawonia"
    assert _drop_first_h("atat") == "atat"


def test_first_h_to_glottal():
    assert _first_h_to_glottal("ahne") == "a'ne"
    assert _first_h_to_glottal("noh") == "no'"
    assert _first_h_to_glottal("atat") == "atat"


def test_drop_h_in_deaffricated_lateral():
    assert _drop_h_in_deaffricated_lateral("alhis") == "atlis"
    assert _drop_h_in_deaffricated_lateral("atat") == "atat"


def test_prevent_and_recreate_glottal_clusters():
    # Sequence of consonant + glottal stop turned into glottal stop + consonant
    assert prevent_C_glottal_cluster("at'") == "a't"
    assert prevent_C_glottal_cluster("ats'") == "a'ts"
    assert recreate_C_glottal_clusters("a't") == "at'"
    assert recreate_C_glottal_clusters("a'ts") == "ats'"


def test_grades_are_compatible():
    # Direct match
    assert grades_are_compatible(h="atat", glottal="atat") is True

    # Drop h
    assert grades_are_compatible(h="ahne", glottal="ane") is True

    # H to glottal
    assert grades_are_compatible(h="ahne", glottal="a'ne") is True

    # Lateral deaffrication
    assert grades_are_compatible(h="alhis", glottal="atlis") is True

    # Incompatible stems
    assert grades_are_compatible(h="atat", glottal="kanestalat") is False
    assert grades_are_compatible(h="gawoniha", glottal="tsuni") is False
