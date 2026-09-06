import os
from pathlib import Path
import pytest
import yaml

CONFIG_DIR = Path(__file__).parent.parent / "chr-config"
GEN_DIR = Path(__file__).parent.parent / "chr-generated"
import parC.constants as c
from parC.grammar.paradigm_compilation import clear_all_caches

from parC.yaml_utils.yaml_server import get_inventory_items, get_patterns, get_rules
from parC.grammar.acceptor_compilation import (
    build_symbol_table,
    _build_special_fsas,
    _build_token_map,
    _build_class_fsts,
    compile_all_patterns,
    _parse_pattern,
)
from parC.yaml_utils.models import SimpleRule, StringMapRule, RuleSequence
import pynini


@pytest.fixture(autouse=True)
def setup_inplace_config():
    old_dir = c.get_yaml_dir()
    c.set_yaml_dir(str(GEN_DIR))
    clear_all_caches()
    try:
        yield
    finally:
        c.set_yaml_dir(old_dir)
        clear_all_caches()


def test_inplace_patterns_and_inventory():
    inv = get_inventory_items()
    patterns = get_patterns()

    assert len(inv.phones) == 16
    assert len(inv.tags) == 138

    # Check required patterns
    assert "<PrepronominalPrefixes>" in patterns
    assert "<Root>" in patterns
    assert "<PrefixClass>" in patterns
    assert "<Pro>" in patterns
    assert "<AspectClass>" in patterns
    assert "<Variant>" in patterns
    assert "<Aspect>" in patterns
    assert "<TenseClass>" not in patterns
    assert "<Tense>" in patterns
    assert "<Morpheme>" in patterns

    # Build symbols and compile pattern FSAs
    syms = build_symbol_table(inv, ())
    special_fsas = _build_special_fsas(syms, inv, ())
    token_map = _build_token_map(syms, inv, (), patterns)
    class_fsts = _build_class_fsts(syms, inv)
    phone_starts = {p[0] for p in inv.phones}
    compiled_patterns = compile_all_patterns(
        patterns, token_map, phone_starts, syms, special_fsas["sigma"], special_fsas, class_fsts
    )

    assert len(compiled_patterns) >= 20
    assert compiled_patterns["<Root>"].num_states() == 2
    assert compiled_patterns["<PrepronominalPrefixes>"].num_states() == 3


def test_inplace_rules_compilation():
    inv = get_inventory_items()
    patterns = get_patterns()
    rules = get_rules()

    syms = build_symbol_table(inv, ())
    special_fsas = _build_special_fsas(syms, inv, ())
    token_map = _build_token_map(syms, inv, (), patterns)
    class_fsts = _build_class_fsts(syms, inv)
    phone_starts = {p[0] for p in inv.phones}
    compiled_patterns = compile_all_patterns(
        patterns, token_map, phone_starts, syms, special_fsas["sigma"], special_fsas, class_fsts
    )

    def fsa_test(p_str):
        return _parse_pattern(
            p_str, token_map, phone_starts, compiled_patterns, syms, special_fsas["sigma"], special_fsas
        )

    sigma_star = special_fsas["sigma_star"]

    # Test that all rules compile without error
    for name, rule in rules.items():
        if isinstance(rule, SimpleRule):
            tau = pynini.cross(fsa_test(rule.input_pattern), fsa_test(rule.output_pattern)).optimize()
            l = fsa_test(rule.left_context) if rule.left_context else ""
            r = fsa_test(rule.right_context) if rule.right_context else ""
            fst = pynini.cdrewrite(tau, l, r, sigma_star)
            assert fst.num_states() > 0
        elif isinstance(rule, StringMapRule):
            tau = pynini.union(*[pynini.cross(fsa_test(i), fsa_test(o)) for i, o in rule.string_map]).optimize()
            l = fsa_test(rule.left_context) if rule.left_context else ""
            r = fsa_test(rule.right_context) if rule.right_context else ""
            fst = pynini.cdrewrite(tau, l, r, sigma_star)
            assert fst.num_states() > 0
        elif isinstance(rule, RuleSequence):
            assert len(rule.rule_sequence) > 0


def test_open_root_template_compiles():
    inv = get_inventory_items()
    patterns = get_patterns()

    syms = build_symbol_table(inv, ())
    special_fsas = _build_special_fsas(syms, inv, ())
    token_map = _build_token_map(syms, inv, (), patterns)
    class_fsts = _build_class_fsts(syms, inv)
    phone_starts = {p[0] for p in inv.phones}
    compiled_patterns = compile_all_patterns(
        patterns, token_map, phone_starts, syms, special_fsas["sigma"], special_fsas, class_fsts
    )

    with open(CONFIG_DIR / "verb.yaml", "r", encoding="utf-8") as f:
        verb_data = yaml.safe_load(f)

    template = verb_data["paradigm"]["open_root_template"]
    tpl_fst = _parse_pattern(
        template, token_map, phone_starts, compiled_patterns, syms, special_fsas["sigma"], special_fsas
    )
    assert tpl_fst.num_states() > 0
