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


def test_meta_label_definitions():
    compiler = MetaConstraintCompiler()
    assert compiler is not None
    assert "[FORM=3RD_PRES]" in compiler.meta_registry
    assert "[FORM=1ST_PRES]" in compiler.meta_registry
    assert "[PRONOUN_SET=A]" in compiler.meta_registry
    assert "[PLURAL=TRUE]" in compiler.meta_registry
    assert "[PLURAL=FALSE]" in compiler.meta_registry


def test_pronominal_struct_and_filters():
    from parse_chr_dict.meta_label_compiler import Pronominal, filter_pronominals
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
    compiler = MetaConstraintCompiler()
    target_labels = compiler.get_feature_tuples_from_meta(["[FORM=3RD_PRES]"])
    assert ("tense", "present") in target_labels
    assert ("aspect", "present") in target_labels


def test_step2_infer_meta_labels():
    compiler = MetaConstraintCompiler()
    parse_str = "[BOW]gawoniha[EOW][tense=present][aspect=present][pronominal=3sg.A]"
    inferred = compiler.infer_meta_labels_from_parse(parse_str)
    assert "[FORM=3RD_PRES]" in inferred
    assert "[PRONOUN_SET=A]" in inferred


def test_4step_derivation_flow():
    compiler = MetaConstraintCompiler()
    lexical_features = {"aspect_class", "prefix_class", "tense_present_class"}
    forms = [
        ("atateka", "[FORM=3RD_PRES]"),
    ]
    res = derive_lexical_features_4step(forms, compiler, lexical_features)
    assert isinstance(res, set)
    assert len(res) > 0


def test_dynamic_constraints_compilation():
    compiler = MetaConstraintCompiler()
    dyn_constraints = [
        FeatureConstraint(slot_name="aspect_class", mode=MatchMode.ONE_OF, values=["go", "d_stem"]),
        FeatureConstraint(slot_name="prefix_class", mode=MatchMode.EXACT, values=["a_stem"]),
    ]
    fsa = compiler.compile_restricted_tag_acceptor(["[FORM=3RD_PRES]"], dynamic_constraints=dyn_constraints)
    assert fsa is not None
    assert fsa.num_states() > 0


def test_build_query_lattice_and_parse_with_lattice():
    compiler = MetaConstraintCompiler()
    surface = "atateka"
    meta_ids = ["[FORM=3RD_PRES]"]
    
    Q = compiler.build_query_lattice(surface, meta_ids)
    assert Q is not None
    assert Q.num_states() > 0

    parses = compiler.parse_with_lattice(surface, meta_ids)
    assert isinstance(parses, list)
    assert len(parses) > 0


def test_4step_derivation_flow_multi_form():
    compiler = MetaConstraintCompiler()
    lexical_features = {"aspect_class", "prefix_class", "tense_present_class"}
    forms = [
        ("atateka", "[FORM=3RD_PRES]"),
        ("atatekaha", "[FORM=3RD_HABITUAL]"),
    ]
    res = derive_lexical_features_4step(forms, compiler, lexical_features)
    assert isinstance(res, set)


def test_4step_meta_label_propagation():
    compiler = MetaConstraintCompiler()
    lexical_features = {"aspect_class", "prefix_class", "tense_present_class"}
    # Multi-form derivation with valid surface form spellings
    forms = [
        ("atateka", "[FORM=3RD_PRES]"),
        ("atatekaha", "[FORM=3RD_HABITUAL]"),
        ("atatekea", "[FORM=3RD_COMPLETIVE]"), # allows_set_a = False, overrides to Set B
    ]
    res = derive_lexical_features_4step(forms, compiler, lexical_features)
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

    compiler = MetaConstraintCompiler()
    lexical_features = {"aspect_class", "prefix_class", "tense_present_class"}

    # Entry 355 forms: present='anatalhisiha', present_1sg='otsatalhisiha'
    forms = [
        (row["present"], "[FORM=3RD_PRES]"),
        (row["present_1sg"], "[FORM=1ST_PRES]"),
        (row["imperfective"], "[FORM=3RD_HABITUAL]"),
    ]
    derived = derive_lexical_features_4step(forms, compiler, lexical_features)
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

    compiler = MetaConstraintCompiler()
    lexical_features = {"aspect_class", "prefix_class", "tense_present_class"}

    # Entry 598 forms: present='tanakaleniha', present_1sg='tostakaleniha', imperative='tistakalena'
    forms = [
        (row["present"], "[FORM=3RD_PRES]"),
        (row["present_1sg"], "[FORM=1ST_PRES]"),
        (row["imperative"], "[FORM=2ND_IMPERATIVE]"),
    ]
    derived = derive_lexical_features_4step(forms, compiler, lexical_features)
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

    compiler = MetaConstraintCompiler()
    lexical_features = {"aspect_class", "prefix_class", "tense_present_class"}

    # Entry 776 forms: present="katonhtiha", present_1sg="tsiyatonhtiha", imperative="hiyatonhta"
    forms = [
        (row["present"], "[FORM=3RD_PRES]"),
        (row["present_1sg"], "[FORM=1ST_PRES]"),
        (row["imperative"], "[FORM=2ND_IMPERATIVE]"),
    ]
    derived = derive_lexical_features_4step(forms, compiler, lexical_features)
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

    compiler = MetaConstraintCompiler()
    lexical_features = {"aspect_class", "prefix_class", "tense_present_class"}

    # Entry 788 forms: present="katv'vska", present_1sg="tsiyatv'vska"
    forms = [
        (row["present"], "[FORM=3RD_PRES]"),
        (row["present_1sg"], "[FORM=1ST_PRES]"),
    ]
    derived = derive_lexical_features_4step(forms, compiler, lexical_features)
    assert len(derived) > 0, f"Animate verb entry 788 ('{row['present']}') failed multi-form derivation"


def test_derivation_hypothesis_dataclass_and_aliases():
    from parse_chr_dict.meta_label_compiler import (
        DerivationHypothesis,
        LexicalVerbHypothesis,
        LexicalVerbEntry,
    )
    assert LexicalVerbHypothesis is DerivationHypothesis
    assert LexicalVerbEntry is DerivationHypothesis

    hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        glottal_root=None,
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert hyp.h_root == "[Pro]atat[Aspect][Tense]"
    assert hyp.glottal_root is None
    assert hyp.prefix_class == "a_stem"
    assert hyp.aspect_class == "go-in"
    assert hyp.tense_present_class == "a_present"
    assert hyp.set_a is True
    assert hyp.plural is False
    assert hyp.animate_objects is False

    d = hyp.to_dict()
    assert d["h_root"] == "[Pro]atat[Aspect][Tense]"
    assert d["glottal_root"] == ""
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
    assert lex_tup[1] is None
    assert ("aspect_class", "go-in") in lex_tup[2]
    assert ("prefix_class", "a_stem") in lex_tup[2]
    assert ("tense_present_class", "a_present") in lex_tup[2]

    meta_comb = hyp.to_meta_combination()
    assert meta_comb.set_a is True
    assert meta_comb.plural is False
    assert meta_comb.animate_objects is False


def test_derive_hypotheses_for_forms_direct():
    from parse_chr_dict.meta_label_compiler import derive_hypotheses_for_forms, DerivationHypothesis
    from parse_chr_dict.create_aspect_class_csv import respell_consonants

    compiler = MetaConstraintCompiler()
    forms = [
        (respell_consonants("atateka"), "[FORM=3RD_PRES]"),
        (respell_consonants("katateka"), "[FORM=1ST_PRES]"),
        (respell_consonants("atateko'i"), "[FORM=3RD_HABITUAL]"),
        (respell_consonants("utatinvsv'i"), "[FORM=3RD_COMPLETIVE]"),
    ]
    hyps = derive_hypotheses_for_forms(forms, compiler)
    assert isinstance(hyps, set)
    assert len(hyps) > 0
    assert all(isinstance(h, DerivationHypothesis) for h in hyps)
    assert any(h.h_root == "[Pro]atat[Aspect][Tense]" and h.glottal_root == "[Pro]atat[Aspect][Tense]" and h.aspect_class == "go-in" for h in hyps)


def test_validate_hypothesis_and_row_reconstruction():
    from parse_chr_dict.meta_label_compiler import DerivationHypothesis
    from parse_chr_dict.reconstruct import validate_hypothesis
    compiler = MetaConstraintCompiler()

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
        glottal_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="go-in",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert validate_hypothesis(valid_hyp, row, PRIMARY_ENTRY_TYPES[0], compiler=compiler) is True
    assert valid_hyp.validate(row, PRIMARY_ENTRY_TYPES[0], compiler=compiler) is True

    # Invalid hypothesis (unknown aspect_class) should fail validation safely
    invalid_hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        glottal_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="wrong_aspect",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert validate_hypothesis(invalid_hyp, row, PRIMARY_ENTRY_TYPES[0], compiler=compiler) is False

    # Mismatched valid aspect_class should fail validation
    mismatched_hyp = DerivationHypothesis(
        h_root="[Pro]atat[Aspect][Tense]",
        glottal_root="[Pro]atat[Aspect][Tense]",
        prefix_class="a_stem",
        aspect_class="become",
        tense_present_class="a_present",
        set_a=True,
        plural=False,
        animate_objects=False,
    )
    assert validate_hypothesis(mismatched_hyp, row, PRIMARY_ENTRY_TYPES[0], compiler=compiler) is False


def test_parse_with_lattice_caching():
    compiler = MetaConstraintCompiler()
    surface = "atateka"
    meta_ids = ["[FORM=3RD_PRES]"]

    # Initial parse
    parses_1 = compiler.parse_with_lattice(surface, meta_ids)
    assert len(parses_1) > 0

    # Cache hit check
    cache_key = (surface, tuple(sorted(meta_ids)), ())
    assert cache_key in compiler._parse_cache
    assert compiler._parse_cache[cache_key] is parses_1

    # Second call returns cached list
    parses_2 = compiler.parse_with_lattice(surface, meta_ids)
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
    from parse_chr_dict.meta_label_compiler import derive_hypotheses_for_forms, DerivationHypothesis

    compiler = MetaConstraintCompiler()
    # Provide 4 consistent forms
    forms = [
        ("atateka", "[FORM=3RD_PRES]"),
        ("katateka", "[FORM=1ST_PRES]"),
        ("atateko'i", "[FORM=3RD_HABITUAL]"),
        ("utatinvsv'i", "[FORM=3RD_COMPLETIVE]"),
    ]
    hyps = derive_hypotheses_for_forms(forms, compiler)
    assert len(hyps) > 0
    # Provide an incompatible form sequence (atateka + kanestalatisko'i from a different root)
    bad_forms = [
        ("atateka", "[FORM=3RD_PRES]"),
        ("kanestalatisko'i", "[FORM=3RD_HABITUAL]"),
    ]
    bad_hyps = derive_hypotheses_for_forms(bad_forms, compiler)
    assert len(bad_hyps) == 0


def test_entry_1759_derivation_and_validation():
    from parse_chr_dict.meta_label_compiler import derive_hypotheses_for_forms, DerivationHypothesis

    compiler = MetaConstraintCompiler()
    row = {
        "present": "uthvtasti",
        "present_1sg": "tsiyathvtasti",
        "imperfective": "uthvtasto'i",
        "perfective": "uthvtastv'i",
        "imperative": "hiyathvtastesti",
        "infinitive": "uthvtastohti",
    }
    spec_by_name = {p.name: p for p in FORMS_TO_PARSE}
    entry_type = PRIMARY_ENTRY_TYPES[1]  # StativeFutProg
    forms = [(row[spec_by_name[fn].corpus_key], spec_by_name[fn]) for fn in entry_type.forms]

    hyps = derive_hypotheses_for_forms(forms, compiler)
    assert len(hyps) == 1
    hyp = next(iter(hyps))
    assert hyp.h_root == "[Pro]athvtast[Aspect][Tense]"
    assert hyp.prefix_class == "a_stem"
    assert hyp.aspect_class == "stative"
    assert hyp.tense_present_class == "i_present"
    assert hyp.set_a is False
    assert hyp.plural is False
    assert hyp.animate_objects is True

    # Validate against full row under StativeFutProg
    assert hyp.validate(row, entry_type, compiler=compiler)


def test_h_alternation_verb_derivation():
    from parse_chr_dict.meta_label_compiler import derive_hypotheses_for_forms, DerivationHypothesis
    from parse_chr_dict.create_aspect_class_csv import respell_consonants

    compiler = MetaConstraintCompiler()
    # Test with a pair of forms where 3rd person has H-grade and 1st person triggers H-alternation
    forms = [
        (respell_consonants("atateka"), "[FORM=3RD_PRES]"),
        (respell_consonants("katateka"), "[FORM=1ST_PRES]"),
    ]
    hyps = derive_hypotheses_for_forms(forms, compiler)
    assert len(hyps) > 0
    assert any(h.h_root == "[Pro]atat[Aspect][Tense]" and h.glottal_root is not None for h in hyps)
