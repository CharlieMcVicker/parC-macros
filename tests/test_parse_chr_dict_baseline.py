import pytest
from parse_chr_dict.meta_label_compiler import (
    MetaConstraintCompiler,
    MetaLabelDefinition,
    FeatureConstraint,
    MatchMode,
    META_LABELS,
    FORMS_TO_PARSE,
    PRIMARY_ENTRY_TYPES,
    SHIM_ENTRY_TYPES,
    derive_lexical_features_4step,
)
from parse_chr_dict.parse import read_labels, str_to_lexical_hashable, get_roots_for_parses, parse
from parse_chr_dict.reconstruct import ReconstructionSpec, reconstruct_row


def test_meta_label_constants_and_definitions():
    assert len(FORMS_TO_PARSE) == 8
    assert len(PRIMARY_ENTRY_TYPES) == 3
    assert len(SHIM_ENTRY_TYPES) == 2

    # Check meta label definitions in registry
    assert "[FORM=3RD_PRES]" in META_LABELS
    assert "[FORM=1ST_PRES]" in META_LABELS
    assert "[FORM=3RD_HABITUAL]" in META_LABELS
    assert "[FORM=3RD_COMPLETIVE]" in META_LABELS
    assert "[FORM=3RD_INCOMPLETIVE_ASSERTIVE]" in META_LABELS
    assert "[FORM=2ND_IMPERATIVE]" in META_LABELS
    assert "[FORM=2ND_FUT_PROG]" in META_LABELS
    assert "[FORM=3RD_INFINITIVE]" in META_LABELS
    assert "[PRONOUN_SET=A]" in META_LABELS

    # Check EntryTypeSpec get_forms_from_parses
    entry = PRIMARY_ENTRY_TYPES[0]
    sample_parses = {
        "3rd_present": ("raw", {"parsed_present"}),
        "1st_present": ("raw", {"parsed_1st_present"}),
    }
    retrieved = entry.get_forms_from_parses(sample_parses)
    assert retrieved == [{"parsed_present"}, {"parsed_1st_present"}]


def test_meta_constraint_compiler_acceptor():
    compiler = MetaConstraintCompiler()
    
    # Test Step 1a target label extraction
    target_labels = compiler.get_feature_tuples_from_meta(["[FORM=3RD_PRES]"])
    assert ("tense", "present") in target_labels
    assert ("aspect", "present") in target_labels

    # Test Step 2 backward metalabel inference
    sample_parse = "[BOW]gawoniha[EOW][tense=present][aspect=present][pronominal=3sg.A]"
    inferred = compiler.infer_meta_labels_from_parse(sample_parse)
    assert "[FORM=3RD_PRES]" in inferred
    assert "[PRONOUN_SET=A]" in inferred


def test_derive_lexical_features_4step():
    compiler = MetaConstraintCompiler()
    lexical_features = {"aspect_class", "prefix_class", "tense_present_class"}
    
    forms = [
        ("atateka", "[FORM=3RD_PRES]"),
    ]
    derived = derive_lexical_features_4step(forms, compiler, lexical_features)
    assert isinstance(derived, set)
    assert len(derived) > 0


def test_read_labels():
    # Legacy trailing-tag format
    raw_str = "[BOW]gawoniha[EOW][tense=present][aspect=present]"
    form, labels = read_labels(raw_str)
    assert form == "gawoniha"
    assert labels == {"tense": "present", "aspect": "present"}

    # In-place slot tags format
    inplace_str = (
        "[BOW][PrefixClass=a_stem][Pro=1sg.A]atat[AspectClass=a][Aspect=present]"
        "[TenseClass=a_present][Tense=present][EOW][aspect_class=a][prefix_class=a_stem][tense_present_class=a_present]"
    )
    form_ip, labels_ip = read_labels(inplace_str)
    assert form_ip == "atat"
    assert labels_ip["prefix_class"] == "a_stem"
    assert labels_ip["pronominal"] == "1sg.A"
    assert labels_ip["aspect_class"] == "a"
    assert labels_ip["aspect"] == "present"
    assert labels_ip["tense_present_class"] == "a_present"
    assert labels_ip["tense"] == "present"

    # In-place format with root mutation tag preserved
    mutation_str = (
        "[BOW][PrefixClass=cons_stem][Pro=3sg.A]a[H_NONE]li[AspectClass=go]"
        "[Aspect=present][TenseClass=a_present][Tense=present][EOW]"
    )
    form_mut, labels_mut = read_labels(mutation_str)
    assert form_mut == "a[H_NONE]li"
    assert labels_mut["prefix_class"] == "cons_stem"
    assert labels_mut["pronominal"] == "3sg.A"
    assert labels_mut["aspect_class"] == "go"
    assert labels_mut["aspect"] == "present"
    assert labels_mut["tense_present_class"] == "a_present"
    assert labels_mut["tense"] == "present"



def test_str_to_lexical_hashable():
    raw_str = "[BOW]gawoniha[EOW][prefix_class=a_stem][tense=present][aspect_class=go]"
    lex_features = {"prefix_class", "aspect_class"}
    root, label_tuple = str_to_lexical_hashable(raw_str, lex_features)
    assert root == "gawoniha"
    assert label_tuple == (("aspect_class", "go"), ("prefix_class", "a_stem"))


def test_get_roots_for_parses():
    set1 = {("root1", (("feat", "val1"),)), ("root2", (("feat", "val2"),))}
    set2 = {("root1", (("feat", "val1"),)), ("root3", (("feat", "val3"),))}
    roots = get_roots_for_parses([set1, set2])
    assert roots == {("root1", (("feat", "val1"),))}


def test_reconstruct_row():
    spec = ReconstructionSpec(plural=False, set_a=True, animate_objects=False)
    assert spec.get_pronominal("3rd", True) == "3sg.A"
    assert spec.get_pronominal("3rd", False) == "3sg.B"


def test_parse_sample_cherokee():
    parses = parse("atateka")
    assert isinstance(parses, list)
    assert len(parses) > 0
    assert any("[BOW]" in p and "[EOW]" in p for p in parses)


def test_derivation_pipeline_hypothesis_refinement():
    from parse_chr_dict.meta_label_compiler import derive_hypotheses_for_forms, DerivationHypothesis
    from parse_chr_dict.reconstruct import validate_hypothesis
    compiler = MetaConstraintCompiler()

    # Multi-form row
    forms = [
        ("atateka", "[FORM=3RD_PRES]"),
        ("katateka", "[FORM=1ST_PRES]"),
        ("atateko'i", "[FORM=3RD_HABITUAL]"),
        ("utatinvsv'i", "[FORM=3RD_COMPLETIVE]"),
    ]
    hyps = derive_hypotheses_for_forms(forms, compiler)
    assert len(hyps) > 0
    for h in hyps:
        assert isinstance(h, DerivationHypothesis)
        assert h.set_a is True
        assert h.plural is False

    row = {
        "present": "atateka",
        "present_1sg": "katateka",
        "imperfective": "atateko'i",
        "perfective": "utatinvsv'i",
        "imperative": "hatatuka",
        "infinitive": "utatinvti",
    }
    validated = [h for h in hyps if validate_hypothesis(h, row, PRIMARY_ENTRY_TYPES[0], compiler=compiler)]
    assert len(validated) > 0
    val_hyp = validated[0]
    assert val_hyp.h_root == "[Pro]atat[Aspect][Tense]"
    assert val_hyp.aspect_class == "go-in"
    assert val_hyp.prefix_class == "a_stem"
    assert val_hyp.tense_present_class == "a_present"
    assert val_hyp.set_a is True
    assert val_hyp.plural is False
    assert val_hyp.animate_objects is False


def test_read_inplace_parse_shared_domain():
    from parse_chr_dict.parse import InPlaceParseConfig, read_inplace_parse

    s = (
        "[BOW][WI][DIST][PrefixClass=a_stem][Pro=3sg.A]a[H_NONE]li"
        "[AspectClass=become[inf2]][Aspect=completive][TenseClass=a_present][Tense=immediate][EOW][rules=+]"
    )
    cfg = read_inplace_parse(s)
    assert isinstance(cfg, InPlaceParseConfig)
    assert cfg.root == "a[H_NONE]li"
    assert cfg.prefix_class == "a_stem"
    assert cfg.pronominal == "3sg.A"
    assert cfg.aspect_class == "become[inf2]"
    assert cfg.aspect == "completive"
    assert cfg.tense_present_class == "a_present"
    assert cfg.tense == "immediate"
    assert cfg.rules == "+"
    assert "[WI]" in cfg.prepronominal_prefixes
    assert "[DIST]" in cfg.prepronominal_prefixes

    labels = cfg.to_labels_dict()
    assert labels["prefix_class"] == "a_stem"
    assert labels["pronominal"] == "3sg.A"
    assert labels["aspect_class"] == "become[inf2]"
    assert labels["aspect"] == "completive"
    assert labels["tense_present_class"] == "a_present"
    assert labels["tense"] == "immediate"
    assert labels["translocutive"] == "+"
    assert labels["distributive"] == "+"
    assert labels["rules"] == "+"

    # Verify canonical wrapped root
    assert cfg.canonical_root == "[Pro]a[H_NONE]li[Aspect][Tense]"


def test_read_inplace_parse_distributive_allomorphs():
    from parse_chr_dict.parse import InPlaceParseConfig, read_inplace_parse

    # Test [DIST=de]
    s_de = (
        "[BOW][DIST=de][PrefixClass=a_stem][Pro=3sg.A]a[H_NONE]li"
        "[AspectClass=become[inf2]][Aspect=completive][TenseClass=a_present][Tense=present][EOW][rules=+]"
    )
    cfg_de = read_inplace_parse(s_de)
    assert "[DIST=de]" in cfg_de.prepronominal_prefixes
    assert cfg_de.to_labels_dict()["distributive"] == "+"
    assert cfg_de.canonical_root == "[Pro]a[H_NONE]li[Aspect][Tense]"

    # Test [DIST=di]
    s_di = (
        "[BOW][DIST=di][PrefixClass=a_stem][Pro=2sg.A]atanhesaka"
        "[AspectClass=a][Aspect=completive][TenseClass=a_present][Tense=immediate][EOW][rules=+]"
    )
    cfg_di = read_inplace_parse(s_di)
    assert "[DIST=di]" in cfg_di.prepronominal_prefixes
    assert cfg_di.to_labels_dict()["distributive"] == "+"
    assert cfg_di.canonical_root == "[Pro]atanhesaka[Aspect][Tense]"


