import pytest
from parse_chr_dict.derive import (
    derive_lexical_features_4step,
    derive_hypotheses_for_forms,
)
from parse_chr_dict.types import (
    Pronominal,
    filter_pronominals,
    DerivationHypothesis,
    VerbForm,
    VerbEntryType,
    ALL_VERB_FORMS,
    PRIMARY_VERB_ENTRY_TYPES,
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
)
from parse_chr_dict.parse import parse_surface, parse_string_to_parse_data


def test_meta_label_definitions():
    # Pure VerbForm domain models
    assert PRES_3RD.name == "3rd_present"
    assert PRES_1SG.name == "1st_present"
    assert len(ALL_VERB_FORMS) == 8
    assert len(PRIMARY_VERB_ENTRY_TYPES) == 3


def test_pronominal_struct_and_filters():
    p = Pronominal.from_tag("3sg.A")
    assert p.person == "3rd"
    assert p.number == "sg"
    assert p.pronoun_set == "A"

    p_trans = Pronominal.from_tag("1sg>3sg")
    assert p_trans.pronoun_set == "transitive"

    sg_a = filter_pronominals(person="3rd", number="sg", pronoun_set="A")
    assert sg_a == ["3sg.A"]

    all_set_a = filter_pronominals(pronoun_set="A")
    assert "3sg.A" in all_set_a
    assert "1sg.A" in all_set_a
    assert "3ns.A" in all_set_a


def test_step1a_feature_tuples():
    # Direct VerbForm features
    assert PRES_3RD.tense == "present"
    assert PRES_3RD.aspect == "present"


def test_step2_infer_meta_labels():
    # Pure VerbForm matching
    parse_str = "[BOW]gawoniha[EOW][tense=present][aspect=present][pronominal=3sg.A]"
    p_data = parse_string_to_parse_data(parse_str)
    assert PRES_3RD.matches(p_data) is True
    assert PRES_1SG.matches(p_data) is False


def test_4step_derivation_flow():
    forms = [
        ("atateka", PRES_3RD),
    ]
    res = derive_hypotheses_for_forms(forms)
    assert isinstance(res, set)
    assert len(res) > 0


def test_verb_form_filtering_and_template_extraction():
    from parse_chr_dict.types import VerbTemplate
    parses = parse_surface("atateka")
    assert len(parses) > 0
    matched = []
    for p in parses:
        p_data = parse_string_to_parse_data(p)
        if PRES_3RD.matches(p_data):
            tmpl = VerbTemplate.from_parse(p_data)
            matched.append((p_data, tmpl))
    assert len(matched) > 0
    assert any(tmpl.aspect_class == "go-in" for _, tmpl in matched)


def test_parse_surface_bare():
    surface = "atateka"
    parses = parse_surface(surface)
    assert isinstance(parses, list)
    assert len(parses) > 0


def test_4step_derivation_flow_multi_form():
    forms = [
        ("atateka", PRES_3RD),
        ("atatekaha", HABITUAL_3RD),
    ]
    res = derive_lexical_features_4step(forms)
    assert isinstance(res, set)


def test_4step_meta_label_propagation():
    forms = [
        ("atateka", PRES_3RD),
        ("atatekaha", HABITUAL_3RD),
        ("atatekea", COMPLETIVE_3RD),  # allows_set_a = False, overrides to Set B
    ]
    res = derive_lexical_features_4step(forms)
    assert isinstance(res, set)


def test_real_plural_verb_entry_355():
    import csv
    with open("chr-corpus/corpus.csv") as f:
        reader = csv.DictReader(
            f,
            fieldnames=[
                "corpus_id",
                "entry_no",
                "definition",
                "present",
                "present_1sg",
                "imperfective",
                "perfective",
                "imperative",
                "infinitive",
            ],
        )
        next(reader)
        row = next(r for r in reader if r["corpus_id"] == "355")

    # Entry 355 forms: present='anatalhisiha', present_1sg='otsatalhisiha'
    forms = [
        (row["present"], PRES_3RD),
        (row["present_1sg"], PRES_1SG),
        (row["imperfective"], HABITUAL_3RD),
    ]
    derived = derive_hypotheses_for_forms(forms)
    assert len(derived) > 0, f"Plural verb entry 355 ('{row['present']}') failed multi-form derivation"


def test_real_plural_verb_entry_598():
    import csv
    with open("chr-corpus/corpus.csv") as f:
        reader = csv.DictReader(
            f,
            fieldnames=[
                "corpus_id",
                "entry_no",
                "definition",
                "present",
                "present_1sg",
                "imperfective",
                "perfective",
                "imperative",
                "infinitive",
            ],
        )
        next(reader)
        row = next(r for r in reader if r["corpus_id"] == "598")

    # Entry 598 forms: present='tanakaleniha', present_1sg='tostakaleniha', imperative='tistakalena'
    forms = [
        (row["present"], PRES_3RD),
        (row["present_1sg"], PRES_1SG),
        (row["imperative"], IMPERATIVE_2ND),
    ]
    derived = derive_hypotheses_for_forms(forms)
    assert len(derived) > 0, f"Plural verb entry 598 ('{row['present']}') failed multi-form derivation"


def test_real_animate_verb_entry_776():
    import csv
    with open("chr-corpus/corpus.csv") as f:
        reader = csv.DictReader(
            f,
            fieldnames=[
                "corpus_id",
                "entry_no",
                "definition",
                "present",
                "present_1sg",
                "imperfective",
                "perfective",
                "imperative",
                "infinitive",
            ],
        )
        next(reader)
        row = next(r for r in reader if r["corpus_id"] == "776")

    # Entry 776 forms: present="katonhtiha", present_1sg="tsiyatonhtiha", imperative="hiyatonhta"
    forms = [
        (row["present"], PRES_3RD),
        (row["present_1sg"], PRES_1SG),
        (row["imperative"], IMPERATIVE_2ND),
    ]
    derived = derive_hypotheses_for_forms(forms)
    assert len(derived) > 0, f"Animate verb entry 776 ('{row['present']}') failed multi-form derivation"


def test_real_animate_verb_entry_788():
    import csv
    with open("chr-corpus/corpus.csv") as f:
        reader = csv.DictReader(
            f,
            fieldnames=[
                "corpus_id",
                "entry_no",
                "definition",
                "present",
                "present_1sg",
                "imperfective",
                "perfective",
                "imperative",
                "infinitive",
            ],
        )
        next(reader)
        row = next(r for r in reader if r["corpus_id"] == "788")

    # Entry 788 forms: present="katv'vska", present_1sg="tsiyatv'vska"
    forms = [
        (row["present"], PRES_3RD),
        (row["present_1sg"], PRES_1SG),
    ]
    derived = derive_hypotheses_for_forms(forms)
    assert len(derived) > 0, f"Animate verb entry 788 ('{row['present']}') failed multi-form derivation"


def test_derivation_hypothesis_dataclass_and_aliases():
    from parse_chr_dict.types import (
        DerivationHypothesis,
        LexicalVerbHypothesis,
        LexicalVerbEntry,
    )
    assert LexicalVerbHypothesis is DerivationHypothesis
    assert LexicalVerbEntry is DerivationHypothesis

    hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        h_alt_tag="[H_alt=none]",
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert hyp.h_root == "[Pro]atat[Aspect][Tense]"
    assert hyp.h_alt_tag == "[H_alt=none]"
    assert hyp.prefix_class == "a_stem"
    assert hyp.aspect_class == "go-in"
    assert hyp.tense_present_class == "a_present"

    assert hyp.set_a is True
    assert hyp.plural is False
    assert hyp.animate_objects is False

    d = hyp.to_dict()
    assert d["h_root"] == "[Pro]atat[Aspect][Tense]"
    assert d["h_alt_tag"] == "[H_alt=none]"
    assert d["prefix_class"] == "a_stem"

    assert d["aspect_class"] == "go-in"
    assert d["tense_present_class"] == "a_present"
    assert d["set_a"] is True
    assert d["plural"] is False
    assert d["animate_objects"] is False

    lex_labels = hyp.lexical_labels()
    assert lex_labels == {
        "aspect_class": "go-in",
        "prefix_class": "a_stem",
        "tense_present_class": "a_present",
    }

    lex_tup = hyp.lexical_tuple()
    assert lex_tup[0] == "[Pro]atat[Aspect][Tense]"
    assert lex_tup[1] == "[H_alt=none]"
    assert ("aspect_class", "go-in") in lex_tup[2]
    assert ("prefix_class", "a_stem") in lex_tup[2]
    assert ("tense_present_class", "a_present") in lex_tup[2]

    assert hyp.set_a is True
    assert hyp.plural is False
    assert hyp.animate_objects is False
    assert hyp.metadata.set_a is True
    assert hyp.metadata.plural is False
    assert hyp.metadata.animate_objects is False


def test_derive_hypotheses_for_forms_direct():
    from parse_chr_dict.derive import derive_hypotheses_for_forms
    from parse_chr_dict.create_aspect_class_csv import respell_consonants

    forms = [
        (respell_consonants("atateka"), PRES_3RD),
        (respell_consonants("katateka"), PRES_1SG),
        (respell_consonants("atateko'i"), HABITUAL_3RD),
        (respell_consonants("utatinvsv'i"), COMPLETIVE_3RD),
    ]
    hyps = derive_hypotheses_for_forms(forms)
    assert isinstance(hyps, set)
    assert len(hyps) > 0
    assert all(isinstance(h, DerivationHypothesis) for h in hyps)
    assert any(h.h_root in ("atat", "[Pro]atat[Aspect][Tense]") and h.aspect_class == "go-in" for h in hyps)


def test_validate_hypothesis_and_row_reconstruction():
    from parse_chr_dict.reconstruct import validate_hypothesis

    row = {
        "corpus_id": "4",
        "entry_no": "8",
        "definition": "it’s bouncing",
        "present": "atateka",
        "present_1sg": "katateka",
        "imperfective": "atateko'i",
        "perfective": "utatinvsv'i",
        "imperative": "hatatuka",
        "infinitive": "utatinvti",
    }
    valid_hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert validate_hypothesis(valid_hyp, row, EVENTFUL) is True
    assert valid_hyp.validate(row, EVENTFUL) is True

    # Invalid hypothesis (unknown aspect_class) should fail validation safely
    invalid_hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="wrong_aspect",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert validate_hypothesis(invalid_hyp, row, EVENTFUL) is False

    # Mismatched valid aspect_class should fail validation
    mismatched_hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="become",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert validate_hypothesis(mismatched_hyp, row, EVENTFUL) is False


def test_parse_surface_caching():
    from parse_chr_dict.parse import parse_surface
    surface = "atateka"

    # Initial parse
    parses_1 = parse_surface(surface)
    assert len(parses_1) > 0

    # Second call returns cached list
    parses_2 = parse_surface(surface)
    assert parses_2 is parses_1


def test_memoized_inflect_caching():
    from parse_chr_dict.reconstruct import memoized_inflect, _INFLECT_CACHE

    root = "[Pro]atat[Aspect][Tense]"
    features = {
        "aspect": "present",
        "tense": "present",
        "pronominal": "3sg.A",
        "aspect_class": "go-in",
        "prefix_class": "a_stem",
        "tense_present_class": "a_present",
        "rules": "+",
    }

    # Initial call
    res_1 = memoized_inflect(root, features)
    assert "atateka" in res_1

    # Verify cache key exists
    feat_key = frozenset(features.items())
    cache_key = (root, feat_key, "verb", True, True)
    assert cache_key in _INFLECT_CACHE

    # Second call hits cache
    res_2 = memoized_inflect(root, features)
    assert res_2 is res_1


def test_hypothesis_pruning_efficiency():
    from parse_chr_dict.derive import derive_hypotheses_for_forms

    # Provide 4 consistent forms
    forms = [
        ("atateka", PRES_3RD),
        ("katateka", PRES_1SG),
        ("atateko'i", HABITUAL_3RD),
        ("utatinvsv'i", COMPLETIVE_3RD),
    ]
    hyps = derive_hypotheses_for_forms(forms)
    assert len(hyps) > 0
    # Provide an incompatible form sequence (atateka + kanestalatisko'i from a different root)
    bad_forms = [
        ("atateka", PRES_3RD),
        ("kanestalatisko'i", HABITUAL_3RD),
    ]
    bad_hyps = derive_hypotheses_for_forms(bad_forms)
    assert len(bad_hyps) == 0


def test_entry_1759_derivation_and_validation():
    from parse_chr_dict.derive import derive_hypotheses_for_forms

    row = {
        "present": "uthvtasti",
        "present_1sg": "tsiyathvtasti",
        "imperfective": "uthvtasto'i",
        "perfective": "uthvtastv'i",
        "imperative": "hiyathvtastesti",
        "infinitive": "uthvtastohti",
    }
    entry_type = STATIVE_FUT_PROG
    forms = [(row[form.corpus_key], form) for form in entry_type.forms]

    hyps = derive_hypotheses_for_forms(forms)
    assert len(hyps) >= 1
    hyp = next(h for h in hyps if h.h_root in ("athvtast", "[Pro]athvtast[Aspect][Tense]") and h.animate_objects is True)
    assert hyp.h_root in ("athvtast", "[Pro]athvtast[Aspect][Tense]")
    assert hyp.prefix_class == "a_stem"
    assert hyp.aspect_class == "stative"
    assert hyp.tense_present_class == "i_present"
    assert hyp.set_a is False
    assert hyp.plural is False
    assert hyp.animate_objects is True

    # Validate against full row under StativeFutProg
    assert hyp.validate(row, entry_type)


def test_h_alternation_verb_derivation():
    from parse_chr_dict.derive import derive_hypotheses_for_forms
    from parse_chr_dict.create_aspect_class_csv import respell_consonants

    # Test with a pair of forms where 3rd person has H-grade and 1st person triggers H-alternation
    forms = [
        (respell_consonants("atateka"), PRES_3RD),
        (respell_consonants("katateka"), PRES_1SG),
    ]
    hyps = derive_hypotheses_for_forms(forms)
    assert len(hyps) > 0
    assert any(h.h_root in ("atat", "[Pro]atat[Aspect][Tense]") for h in hyps)


def test_h_alternation_trigger_external_validation():
    from parse_chr_dict.h_alternation import validate_h_alternation_trigger
    from parse_chr_dict.reconstruct import validate_hypothesis, reconstruct_row

    # Test standalone trigger validation logic
    assert validate_h_alternation_trigger("1sg>3sg", has_h_alt=True) is True
    assert validate_h_alternation_trigger("2sg>3sg", has_h_alt=True) is True
    assert validate_h_alternation_trigger("1sg.A", has_h_alt=True) is True
    assert validate_h_alternation_trigger("3sg.A", has_h_alt=True) is False
    assert validate_h_alternation_trigger("3sg.B", has_h_alt=True) is False
    assert validate_h_alternation_trigger("1sg.B", has_h_alt=True) is False
    assert validate_h_alternation_trigger("3sg.A", has_h_alt=False) is True

    # Test integration with validate_hypothesis and reconstruct_row
    entry_type = EVENTFUL
    row = {
        "present": "atateka",
        "present_1sg": "katateka",
        "imperfective": "atateko'i",
        "perfective": "utatinvsv'i",
        "imperative": "hatatuka",
        "infinitive": "utatinvti",
    }
    hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        h_alt_tag="[H_alt=none]",
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert validate_hypothesis(hyp, row, entry_type) is True

    # Row reconstruction with H-alternation fields
    row_with_roots = {
        **row,
        "h_root": "[Pro]atat[Aspect][Tense]",
        "h_alt_tag": "[H_alt=none]",
        "prefix_class": "a_stem",
        "aspect_class": "go-in",
        "tense_present_class": "a_present",
    }
    specs = reconstruct_row(
        row_with_roots,
        entry_type,
        ["prefix_class", "aspect_class", "tense_present_class"],
    )
    assert len(specs) > 0


def test_fine_grained_h_alternation_tag_helpers_and_validation():
    from parse_chr_dict.h_alternation import H_ALT_TAGS, NEW_H_ALT_TAGS, validate_h_alternation_trigger, strip_h_alt_tags

    # 1. H_ALT_TAGS constant
    assert NEW_H_ALT_TAGS == {"[H_alt=drop]", "[H_alt=glot]", "[H_alt=lat]", "[H_alt=none]", "[H_alt=vowel]"}
    assert {"[H_DROP]", "[H_GLOT]", "[H_LAT]", "[H_NONE]", "[H_VOWEL]"}.issubset(H_ALT_TAGS)

    # 2. strip_h_alt_tags
    cleaned = strip_h_alt_tags("[Pro][H_DROP]atanhoy[Aspect][Tense]")
    assert cleaned == "[Pro]atanhoy[Aspect][Tense]"

    cleaned_vowel = strip_h_alt_tags("[Pro][H_VOWEL]atanhth[Aspect][Tense]")
    assert cleaned_vowel == "[Pro]atanhth[Aspect][Tense]"

    cleaned_none = strip_h_alt_tags("[Pro][H_NONE]atanhoy[Aspect][Tense]")
    assert cleaned_none == "[Pro]atanhoy[Aspect][Tense]"

    cleaned_raw = strip_h_alt_tags("[Pro]atanhoy[Aspect][Tense]")
    assert cleaned_raw == "[Pro]atanhoy[Aspect][Tense]"

    # 3. validate_h_alternation_trigger with fine-grained tags
    assert validate_h_alternation_trigger("1sg>3sg", "[H_DROP]") is True
    assert validate_h_alternation_trigger("2sg>3sg", "[H_GLOT]") is True
    assert validate_h_alternation_trigger("1sg.A", "[H_LAT]") is True
    assert validate_h_alternation_trigger("1sg.A", "[H_VOWEL]") is True
    assert validate_h_alternation_trigger("3sg.A", "[H_DROP]") is False
    assert validate_h_alternation_trigger("3sg.B", "[H_GLOT]") is False
    assert validate_h_alternation_trigger("1sg.B", "[H_LAT]") is False
    assert validate_h_alternation_trigger("3sg.A", "[H_VOWEL]") is False
    assert validate_h_alternation_trigger("3sg.A", "[H_NONE]") is True
    assert validate_h_alternation_trigger("3sg.A", None) is True


def test_strict_h_alternation_trigger_rejection():
    """Verify that when a trigger form shows H-mutation, unmutated [H_NONE] fallbacks for that root are pruned."""
    from parse_chr_dict.derive import derive_hypotheses_for_forms
    from parse_chr_dict.create_aspect_class_csv import respell_consonants

    # atanhoyeha (3sg) + katanoyeha (1sg trigger with H_DROP mutation)
    forms_mutating = [
        (respell_consonants("atanhoyeha"), PRES_3RD),
        (respell_consonants("katanoyeha"), PRES_1SG),
    ]
    hyps_mut = derive_hypotheses_for_forms(forms_mutating)
    assert len(hyps_mut) > 0
    for h in hyps_mut:
        assert h.h_alt_tag in ("[H_alt=drop]", "[H_alt=glot]", "[H_alt=lat]", "[H_DROP]", "[H_GLOT]", "[H_LAT]")

    # atateka (3sg) + katateka (1sg trigger without H-mutation)
    forms_non_mutating = [
        (respell_consonants("atateka"), PRES_3RD),
        (respell_consonants("katateka"), PRES_1SG),
    ]
    hyps_non_mut = derive_hypotheses_for_forms(forms_non_mutating)
    assert len(hyps_non_mut) > 0
    for h in hyps_non_mut:
        assert h.h_alt_tag in ("[H_alt=none]", "[H_NONE]", "")


def test_h_vowel_row_39_43_thinking_derivation():
    """Verify that row 39,43 ('he/she is thinking') matches and derives hypotheses containing [H_VOWEL]."""
    from parse_chr_dict.derive import derive_hypotheses_for_forms
    from parse_chr_dict.create_aspect_class_csv import respell_consonants

    forms = [
        (respell_consonants("atanhtheha"), PRES_3RD),
        (respell_consonants("katanvtheha"), PRES_1SG),
    ]
    hyps = derive_hypotheses_for_forms(forms)
    assert len(hyps) > 0
    h_vowel_hyps = [h for h in hyps if h.h_alt_tag in ("[H_VOWEL]", "[H_alt=vowel]")]
    assert len(h_vowel_hyps) > 0, "Expected at least one hypothesis with [H_VOWEL]"
    for h in h_vowel_hyps:
        assert h.h_alt_tag in ("[H_VOWEL]", "[H_alt=vowel]")
        assert "atanh" in h.h_root
