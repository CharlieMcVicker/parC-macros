import pytest
from dataclasses import FrozenInstanceError
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


def test_parse_data_immutability_and_fields():
    p = ParseData(
        root="atat",
        prefix_class="a_stem",
        pronominal="3sg.A",
        h_alt_tag="[H_alt=none]",
        aspect_class="go-in",
        variant=2,
        aspect="present",
        tense_present_class="a_present",
        tense="present",
        prepronominal_prefixes=["[WI]", "[DIST]"],
        raw_tokens=["[WI]", "[DIST]"],
    )
    assert p.root == "atat"
    assert p.prefix_class == "a_stem"
    assert p.variant == 2
    assert p.has_distributive is True
    assert p.has_translocutive is True
    assert p.rules == "+"
    assert isinstance(p.prepronominal_prefixes, tuple)
    assert isinstance(p.raw_tokens, tuple)

    # Immutability
    with pytest.raises(FrozenInstanceError):
        p.root = "new_root"

    # to_labels_dict
    labels = p.to_labels_dict()
    assert labels["prefix_class"] == "a_stem"
    assert labels["pronominal"] == "3sg.A"
    assert labels["variant"] == "2"
    assert labels["distributive"] == "+"
    assert labels["translocutive"] == "+"
    assert labels["rules"] == "+"

    # to_inplace_string
    s = p.to_inplace_string()
    assert "[PrefixClass=a_stem]" in s
    assert "[Pro=3sg.A]" in s
    assert "[H_alt=none]atat" in s
    assert "[Variant=2]" in s
    assert "[Aspect=present]" in s


def test_parse_data_alias_and_string_variant():
    # InPlaceParseConfig is ParseData
    assert InPlaceParseConfig is ParseData
    p = InPlaceParseConfig(root="ali", variant="3", prepronominal_prefixes=["[DIST=de]"])
    assert p.variant == 3
    assert p.has_distributive is True
    assert p.canonical_root == "[Pro]ali[Aspect][Tense]"


def test_verb_template_projection():
    p = ParseData(
        root="a[H_NONE]li",
        prefix_class="cons_stem",
        pronominal="3sg.A",
        h_alt_tag="[H_NONE]",
        aspect_class="go",
        variant=1,
        aspect="present",
        tense_present_class="a_present",
        tense="present",
        prepronominal_prefixes=["[DIST]"],
    )
    tmpl = VerbTemplate.from_parse(p)
    assert tmpl.root == "a[H_NONE]li"
    assert tmpl.prefix_class == "cons_stem"
    assert tmpl.aspect_class == "go"
    assert tmpl.tense_present_class == "a_present"
    assert tmpl.variant == 1
    assert tmpl.distributive is True
    assert tmpl.translocutive is False
    assert tmpl.h_alt_tag == "[H_NONE]"

    # Immutability
    with pytest.raises(FrozenInstanceError):
        tmpl.root = "other"

    labels = tmpl.lexical_labels()
    assert labels["aspect_class"] == "go"
    assert labels["prefix_class"] == "cons_stem"
    assert labels["tense_present_class"] == "a_present"
    assert labels["distributive"] == "+"
    assert "variant" not in labels  # Default variant 1 omitted


def test_aspect_variants_pure_functional():
    v0 = AspectVariants()
    assert v0.present == 1
    assert v0.incompletive == 1
    assert v0.completive == 1
    assert v0.immediate == 1
    assert v0.infinitive == 1

    # Copy-on-write
    v1 = v0.with_variant("infinitive", 2)
    assert v0.infinitive == 1  # Original unmodified
    assert v1.infinitive == 2

    # Aspect name alias mapping
    v2 = v1.with_variant("imperfective", 3)
    assert v2.incompletive == 3
    assert v2.get_variant("imperfective") == 3

    v3 = v2.with_variant("imperative", 4)
    assert v3.immediate == 4
    assert v3.get_variant("immediate") == 4

    d = v3.to_dict()
    assert d == {
        "variant_present": 1,
        "variant_incompletive": 3,
        "variant_completive": 1,
        "variant_immediate": 4,
        "variant_infinitive": 2,
    }


def test_verb_metadata_pure_functional():
    m0 = VerbMetadata(entry_type="Eventful", is_set_a=True, is_plural=False, animate_objects=False)
    assert m0.aspect_variants.present == 1

    m1 = m0.with_variant("completive", 2)
    assert m0.aspect_variants.completive == 1
    assert m1.aspect_variants.completive == 2
    assert m1.is_set_a is True

    d = m1.to_dict()
    assert d["entry_type"] == "Eventful"
    assert d["set_a"] is True
    assert d["plural"] is False
    assert d["animate_objects"] is False
    assert d["variant_completive"] == 2


def test_lexical_verb_product_and_serialization():
    tmpl = VerbTemplate(
        root="a[H_NONE]li",
        prefix_class="a_stem",
        aspect_class="become",
        tense_present_class="a_present",
        variant=1,
    )
    meta = VerbMetadata(
        entry_type="Eventful",
        is_set_a=True,
        is_plural=False,
        animate_objects=False,
        aspect_variants=AspectVariants(infinitive=2),
    )
    verb = LexicalVerb(
        template=tmpl,
        metadata=meta,
        h_alt_tag="[H_alt=none]",
    )

    # Properties
    assert verb.h_root == "ali"
    assert verb.h_alt_tag == "[H_alt=none]"
    assert verb.prefix_class == "a_stem"
    assert verb.aspect_class == "become"
    assert verb.tense_present_class == "a_present"
    assert verb.set_a is True
    assert verb.plural is False
    assert verb.animate_objects is False
    assert verb.entry_type == "Eventful"

    # Immutability
    with pytest.raises(FrozenInstanceError):
        verb.h_alt_tag = "other"

    # Serialization to roots.csv schema
    base_row = {
        "corpus_id": "1",
        "entry_no": "10",
        "definition": "to become",
        "present": "aka",
        "present_1sg": "kaka",
        "imperfective": "akeko'i",
        "perfective": "ukelv'i",
        "imperative": "haka",
        "infinitive": "u'isti",
    }
    row_dict = verb.to_row_dict(base_row)
    expected_keys = [
        "corpus_id", "entry_no", "definition", "present", "present_1sg",
        "imperfective", "perfective", "imperative", "infinitive",
        "entry_type", "h_root", "h_alt_tag", "aspect_class", "prefix_class",
        "tense_present_class", "set_a", "plural", "animate_objects",
        "variant_present", "variant_incompletive", "variant_completive",
        "variant_immediate", "variant_infinitive",
    ]
    assert list(row_dict.keys()) == expected_keys
    assert row_dict["variant_infinitive"] == 2
    assert row_dict["h_root"] == "ali"
    assert row_dict["h_alt_tag"] == "[H_alt=none]"
    assert row_dict["entry_type"] == "Eventful"


def test_lexical_verb_legacy_init_and_aliases():
    assert DerivationHypothesis is LexicalVerb
    assert LexicalVerbHypothesis is LexicalVerb
    assert LexicalVerbEntry is LexicalVerb

    hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        glottal_root=None,
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
        present_variant="2",
    )
    assert hyp.h_root == "[Pro]atat[Aspect][Tense]"
    assert hyp.prefix_class == "a_stem"
    assert hyp.aspect_class == "go-in"
    assert hyp.template.variant == 2
    assert hyp.present_variant == "2"
    assert hyp.metadata.aspect_variants.present == 2


def test_lexical_verb_inflect_form_and_validate_form():
    from parse_chr_dict.types import (
        PRES_3RD,
        PRES_1SG,
        HABITUAL_3RD,
        COMPLETIVE_3RD,
        IMPERATIVE_2ND,
        INFINITIVE_3RD,
    )
    verb = LexicalVerb(
        h_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )

    # inflect_form returns sorted, deduplicated list
    forms_3rd = verb.inflect_form(PRES_3RD)
    assert isinstance(forms_3rd, list)
    assert forms_3rd == sorted(list(set(forms_3rd)))
    assert "atateka" in forms_3rd

    # validate_form with respell_consonants handling
    assert verb.validate_form(PRES_3RD, "atateka") is True
    assert verb.validate_form(PRES_1SG, "katateka") is True
    assert verb.validate_form(HABITUAL_3RD, "atateko'i") is True
    assert verb.validate_form(COMPLETIVE_3RD, "utatinvsv'i") is True
    assert verb.validate_form(IMPERATIVE_2ND, "hatatuka") is True
    assert verb.validate_form(INFINITIVE_3RD, "utatinvti") is True

    # Failed validations
    assert verb.validate_form(PRES_3RD, "invalid") is False
    assert verb.validate_form(PRES_1SG, "atateka") is False


def test_lexical_verb_validate_hypothesis_direct():
    from parse_chr_dict.reconstruct import validate_hypothesis
    from parse_chr_dict.types import EVENTFUL

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
    valid_verb = LexicalVerb(
        h_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )

    # Valid with VerbEntryType, str name, or without compiler
    assert validate_hypothesis(valid_verb, row, EVENTFUL) is True
    assert validate_hypothesis(valid_verb, row, "Eventful") is True
    assert valid_verb.validate(row, EVENTFUL) is True

    # Mismatched hypothesis fails
    bad_verb = LexicalVerb(
        h_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="wrong",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert validate_hypothesis(bad_verb, row, EVENTFUL) is False
    assert bad_verb.validate(row, EVENTFUL) is False
