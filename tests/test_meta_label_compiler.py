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
