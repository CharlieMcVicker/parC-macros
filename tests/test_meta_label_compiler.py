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

