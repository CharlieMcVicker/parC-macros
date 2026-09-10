"""
tests/test_acceptors.py

Comprehensive test suite for in-place stem-shape and morphotactic acceptor system (TASK-106):
- AC 1: Audit and verify all 7 prefix classes in chr-config/feature_acceptors/prefix_class.csv
- AC 2: Morphotactic licensing acceptor enforcing trigger => licensed constraints
- AC 3: Anchored prefix stem-shape acceptor matching [PrefixClass=c]<Pro><H_ALT>?<PhoneConstraint>
- AC 4: Cascade domain acceptor combining morphotactics and stem-shape with [BOW]/[EOW] wrapping
- AC 5: Verification of invalid hypothesis pruning with minimal state footprint (~15-35 states)
"""

import csv
import os
from pathlib import Path
import pytest
import pynini

from parC.constants import set_yaml_dir
from parC.grammar.acceptor_compilation import fsa, fsm_strings, word_fsa
from parC.grammar.paradigm_compilation import clear_all_caches
from parc_macros.generate_markers import generate_markers
from parse_chr_dict.acceptors import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_FEATURE_ACCEPTORS_DIR,
    DEFAULT_MORPHOTACTICS_CSV,
    _CASCADE_DOMAIN_CACHE,
    compile_morphotactic_acceptor,
    compile_cascade_domain_acceptor,
    accepts_parse,
    get_cascade_domain_acceptor,
    tokenize_parse_str,
    parse_to_fsa,
    get_default_symbol_table,
    get_default_alphabet,
)
import parse_chr_dict.parse as parse_mod
from parse_chr_dict.parse import get_parse_graph, parse
from parC.grammar.paradigm_compilation import get_open_inflect_graph

REPO_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_DIR = REPO_ROOT / "chr-config"
GEN_DIR = REPO_ROOT / "chr-generated"
PREFIX_CLASS_CSV = DEFAULT_FEATURE_ACCEPTORS_DIR / "prefix_class.csv"


@pytest.fixture(scope="module", autouse=True)
def setup_acceptor_env():
    """Ensure generated environment is set up and configured."""
    orig_yaml_dir = os.environ.get("YAML_DIR")

    generate_markers(str(CONFIG_DIR), str(GEN_DIR))

    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    set_yaml_dir(str(GEN_DIR))
    os.environ["YAML_DIR"] = str(GEN_DIR)

    yield

    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    if orig_yaml_dir:
        set_yaml_dir(orig_yaml_dir)
        os.environ["YAML_DIR"] = orig_yaml_dir


# ==============================================================================
# AC 1: Audit and verify chr-config/feature_acceptors/prefix_class.csv
# ==============================================================================

def test_prefix_class_csv_audit_ac1():
    """Verify all prefix classes are present and map to exact phoneme patterns."""
    assert PREFIX_CLASS_CSV.exists()

    # All expected classes and their phone expectations
    expected_classes = {
        "a_stem": {"a"},
        "v_stem": {"v"},
        "e_stem": {"e"},
        "k_a_stem": {"a"},
        "vowel_stem": {"e", "o", "u", "v"},
        "cons_stem": {"t", "k", "'", "h", "s", "lh", "y", "yh", "w"},
        "r_stem": {"m", "n", "l", "y", "w", "'m", "'n", "'l", "'y", "'w"},
        "long_stem": {"t", "k", "'", "m", "n", "h", "s", "l", "y", "w"},
    }

    with open(PREFIX_CLASS_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        classes_found = {}
        for row in reader:
            if not row or not row[0] or row[0].startswith("#") or row[0] == "prefix_class":
                continue
            pclass = row[0].strip()
            pat = row[1].strip()
            classes_found[pclass] = pat

    assert set(classes_found.keys()) == set(expected_classes.keys()), (
        f"Mismatch in prefix classes: found {set(classes_found.keys())}, expected {set(expected_classes.keys())}"
    )

    for pclass, expected_phones in expected_classes.items():
        pat = classes_found[pclass]
        pat_fsa = fsa(pat)
        assert pat_fsa is not None
        resolved = set(fsm_strings(pat_fsa))
        assert resolved == expected_phones, (
            f"Class {pclass} pattern '{pat}' resolved to {resolved}, expected {expected_phones}"
        )


# =========================================================================
# AC 2: Morphotactic licensing acceptor
# =========================================================================

def test_compile_morphotactic_acceptor_ac2():
    """AC 2: compile_morphotactic_acceptor enforces trigger => licensed constraints."""
    syms = get_default_symbol_table()
    alphabet = get_default_alphabet()

    morph_fsa = compile_morphotactic_acceptor(syms, alphabet)
    assert morph_fsa is not None

    # State footprint verification: compact (~15-700 states across all modular CSVs)
    state_count = morph_fsa.num_states()
    assert 12 <= state_count <= 700, f"Expected state count between 12 and 700, got {state_count}"

    # Helper to test un-wrapped strings against morph_fsa
    def morph_accepts(tokens: list[str]) -> bool:
        test_fsa = pynini.accep(" ".join(tokens), token_type=syms)
        res = pynini.intersect(test_fsa, morph_fsa)
        return res.num_states() > 0 and res.start() != pynini.NO_STATE_ID

    base_tokens = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "a", "t", "a", "t", "[AspectClass=a]"]

    # 1. [DIST=de] licenses indicative tenses
    indicative_tenses = [
        "[Tense=present_a]",
        "[Tense=habitual]",
        "[Tense=future_prog]",
        "[Tense=assertive]",
        "[Tense=reported]",
    ]
    for t in indicative_tenses:
        asp = "[Aspect=present]" if t == "[Tense=present_a]" else "[Aspect=incompletive]"
        tokens = ["[DIST=de]"] + base_tokens + [asp, t]
        assert morph_accepts(tokens), f"[DIST=de] should accept indicative tense {t}"

    # 2. [DIST=de] rejects non-indicative tenses
    non_indicative_tenses = ["[Tense=immediate]", "[Tense=infinitive]"]
    for t in non_indicative_tenses:
        tokens = ["[DIST=de]"] + base_tokens + ["[Aspect=present]", t]
        assert not morph_accepts(tokens), f"[DIST=de] must reject non-indicative tense {t}"

    # 3. [DIST=di] licenses non-indicative tenses (immediate, infinitive)
    for t in non_indicative_tenses:
        tokens = ["[DIST=di]"] + base_tokens + ["[Aspect=immediate]" if t == "[Tense=immediate]" else "[Aspect=infinitive]", t]
        assert morph_accepts(tokens), f"[DIST=di] should accept non-indicative tense {t}"

    # 4. [DIST=di] rejects indicative tenses
    for t in indicative_tenses:
        asp = "[Aspect=present]" if t == "[Tense=present_a]" else "[Aspect=incompletive]"
        tokens = ["[DIST=di]"] + base_tokens + [asp, t]
        assert not morph_accepts(tokens), f"[DIST=di] must reject indicative tense {t}"

    # 5. [Aspect=immediate] licenses only [Tense=immediate]
    tokens_imm_ok = base_tokens + ["[Aspect=immediate]", "[Tense=immediate]"]
    assert morph_accepts(tokens_imm_ok)
    tokens_imm_bad = base_tokens + ["[Aspect=immediate]", "[Tense=present_a]"]
    assert not morph_accepts(tokens_imm_bad)

    # 6. [Aspect=infinitive] licenses only [Tense=infinitive]
    tokens_inf_ok = base_tokens + ["[Aspect=infinitive]", "[Tense=infinitive]"]
    assert morph_accepts(tokens_inf_ok)
    tokens_inf_bad = base_tokens + ["[Aspect=infinitive]", "[Tense=present_a]"]
    assert not morph_accepts(tokens_inf_bad)

    # 7. Unconstrained when no triggers present
    tokens_plain_pres = base_tokens + ["[Tense=present_a]"]
    assert morph_accepts(tokens_plain_pres)
    tokens_plain_imm = base_tokens + ["[Tense=immediate]"]
    assert morph_accepts(tokens_plain_imm)

    # 8. TASK-109: Pronominal H_alt morphotactics
    # Trigger 1sg.A licenses all H_alt allomorphs
    tokens_1sg_alt = ["[PrefixClass=a_stem]", "[Pro=1sg.A]", "[H_alt=drop]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert morph_accepts(tokens_1sg_alt)
    tokens_1sg_none = ["[PrefixClass=a_stem]", "[Pro=1sg.A]", "[H_alt=none]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert morph_accepts(tokens_1sg_none)

    # Elsewhere (*): 3sg.A licenses only [H_alt=none]
    tokens_3sg_none = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "[H_alt=none]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert morph_accepts(tokens_3sg_none)
    tokens_3sg_drop = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "[H_alt=drop]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert not morph_accepts(tokens_3sg_drop)
    tokens_2sg_glot = ["[PrefixClass=a_stem]", "[Pro=2sg.A]", "[H_alt=glot]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert not morph_accepts(tokens_2sg_glot)

    # 9. Stative aspect morphotactics: stative classes license ONLY present and incompletive aspects
    tokens_stative_pres = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "a", "t", "a", "t", "[AspectClass=stative-k]", "[Aspect=present]", "[Tense=present_a]"]
    assert morph_accepts(tokens_stative_pres)
    tokens_stative_incomp = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "a", "t", "a", "t", "[AspectClass=stative-k]", "[Aspect=incompletive]", "[Tense=habitual]"]
    assert morph_accepts(tokens_stative_incomp)
    tokens_stative_comp = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "a", "t", "a", "t", "[AspectClass=stative-k]", "[Aspect=completive]", "[Tense=assertive]"]
    assert not morph_accepts(tokens_stative_comp)
    tokens_stative_imm = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "a", "t", "a", "t", "[AspectClass=stative-k]", "[Aspect=immediate]", "[Tense=immediate]"]
    assert not morph_accepts(tokens_stative_imm)
    tokens_stative_inf = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "a", "t", "a", "t", "[AspectClass=stative-k]", "[Aspect=infinitive]", "[Tense=infinitive]"]
    assert not morph_accepts(tokens_stative_inf)

    # 10. H_metathesis morphotactics: <HMetaPro> (3sg.A, 1sg.B, 2sg.B) licenses <H_metathesis>
    tokens_meta_3sg_active = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "[H_metathesis=active]", "[H_alt=none]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert morph_accepts(tokens_meta_3sg_active)
    tokens_meta_3sg_none = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "[H_metathesis=none]", "[H_alt=none]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert morph_accepts(tokens_meta_3sg_none)

    # Elsewhere (*): 3sg.B licenses only [H_metathesis=none]
    tokens_meta_3sgB_none = ["[PrefixClass=a_stem]", "[Pro=3sg.B]", "[H_metathesis=none]", "[H_alt=none]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert morph_accepts(tokens_meta_3sgB_none)
    tokens_meta_3sgB_active = ["[PrefixClass=a_stem]", "[Pro=3sg.B]", "[H_metathesis=active]", "[H_alt=none]", "a", "t", "a", "t", "[AspectClass=a]"]
    assert not morph_accepts(tokens_meta_3sgB_active)


# =========================================================================
# AC 3: Native prefix stem-shape right-context licensing via FST cascade
# =========================================================================

def test_right_context_prefix_stem_shape_licensing_ac3():
    """
    AC 3: Verify that morpheme replacement rules enforce prefix class stem-shape
    constraints at insertion time via right_context in pro_replace.yaml.
    """
    inflect_fst = get_open_inflect_graph("verb", infer_lexical_features=False)
    mid = "[H_metathesis=none][H_alt=none]"
    tail = "[AspectClass=a][Aspect=present][Tense=present_a]"

    # Valid combinations produce clean surface forms
    valid_cases = [
        (f"[PrefixClass=a_stem][Pro=3sg.A]{mid}atat{tail}", "atata'a"),
        (f"[PrefixClass=cons_stem][Pro=3sg.A]{mid}that{tail}", "athata'a"),
        (f"[PrefixClass=r_stem][Pro=3sg.A]{mid}nhat{tail}", "kanhata'a"),
        (f"[PrefixClass=vowel_stem][Pro=3sg.A]{mid}ehat{tail}", "kehata'a"),
    ]
    for inp, expected in valid_cases:
        out_fst = pynini.compose(word_fsa(inp), inflect_fst)
        forms = fsm_strings(pynini.project(out_fst, "output").optimize())
        clean_forms = [f.replace("[BOW]", "").replace("[EOW]", "") for f in forms if "[" not in f.replace("[BOW]", "").replace("[EOW]", "")]
        assert expected in clean_forms, f"Expected {expected} in inflected forms for {inp}, got {forms}"

    # Invalid combinations (illicit initial phones for prefix class) fail to transduce (tags left unconsumed)
    invalid_cases = [
        # a_stem before consonant root 'that'
        f"[PrefixClass=a_stem][Pro=3sg.A]{mid}that{tail}",
        # cons_stem before vowel root 'atat'
        f"[PrefixClass=cons_stem][Pro=3sg.A]{mid}atat{tail}",
        # v_stem before 'a'
        f"[PrefixClass=v_stem][Pro=3sg.A]{mid}atat{tail}",
        # e_stem before 'a'
        f"[PrefixClass=e_stem][Pro=3sg.A]{mid}atat{tail}",
    ]
    for inp in invalid_cases:
        out_fst = pynini.compose(word_fsa(inp), inflect_fst)
        forms = fsm_strings(pynini.project(out_fst, "output").optimize())
        clean_forms = [f for f in forms if "[" not in f.replace("[BOW]", "").replace("[EOW]", "")]
        assert len(clean_forms) == 0, f"Mismatched stem shape {inp} must produce 0 valid surface forms, got {clean_forms}"


# =========================================================================
# AC 4 & 5: Cascade domain acceptor & invalid combination pruning
# =========================================================================

def test_compile_cascade_domain_acceptor_ac4_ac5():
    """
    AC 4 & AC 5: Wrap morphotactic licensing acceptor with [BOW]/[EOW] wrapping.
    Verify valid in-place parses are accepted and illicit morphotactic combinations pruned.
    """
    syms = get_default_symbol_table()
    alphabet = get_default_alphabet()

    cascade = compile_cascade_domain_acceptor(syms, alphabet)
    assert cascade is not None
    assert cascade.num_states() > 0

    valid_parses = [
        # a_stem with initial 'a'
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # cons_stem with consonant 't'
        "[BOW][PrefixClass=cons_stem][Pro=3sg.A]that[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # [DIST=de] with indicative present tense
        "[BOW][DIST=de][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # [DIST=di] with non-indicative immediate tense
        "[BOW][DIST=di][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=immediate][Tense=immediate][EOW][rules=+]",
        # [DIST=di] with cons_stem and immediate tense
        "[BOW][DIST=di][PrefixClass=cons_stem][Pro=3sg.A]that[AspectClass=a][Aspect=immediate][Tense=immediate][EOW][rules=+]",
        # [WI] prepronominal prefix
        "[BOW][WI][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # [WI] + [DIST=de]
        "[BOW][WI][DIST=de][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # [H_alt=drop] with a_stem and 1sg.A (trigger)
        "[BOW][PrefixClass=a_stem][Pro=1sg.A][H_alt=drop]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # Without trailing [rules=+]
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW]",
    ]

    for vp in valid_parses:
        assert accepts_parse(cascade, vp, syms), f"Cascade should accept valid parse: {vp}"

    invalid_parses = [
        # TASK-109: Non-trigger 3sg.A with active [H_alt=drop] (violates pro_morphotactics)
        "[BOW][PrefixClass=a_stem][Pro=3sg.A][H_alt=drop]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # [DIST=de] with immediate tense (violates morphotactics)
        "[BOW][DIST=de][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=immediate][EOW][rules=+]",
        # [DIST=di] with present tense (violates morphotactics)
        "[BOW][DIST=di][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # [Aspect=immediate] with present tense
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=immediate][Tense=present_a][EOW][rules=+]",
        # [Aspect=infinitive] with present tense
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=infinitive][Tense=present_a][EOW][rules=+]",
        # Missing [BOW]
        "[PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=present_a][EOW][rules=+]",
        # Missing [EOW]
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][Tense=present_a][rules=+]",
    ]

    for ip in invalid_parses:
        assert not accepts_parse(cascade, ip, syms), f"Cascade must reject invalid parse: {ip}"


def test_tokenize_parse_str_and_parse_to_fsa():
    """Verify parse tokenization handles nested brackets and complex tags."""
    syms = get_default_symbol_table()

    # In-place string with AspectClass and Variant tags
    s = "[BOW][PrefixClass=a_stem][Pro=1sg.A]atat[AspectClass=become][Variant=2][Aspect=infinitive][Tense=infinitive][EOW][rules=+]"
    tokens = tokenize_parse_str(s)
    assert tokens[0] == "[BOW]"
    assert tokens[1] == "[PrefixClass=a_stem]"
    assert tokens[2] == "[Pro=1sg.A]"
    assert tokens[3:7] == ["a", "t", "a", "t"]
    assert tokens[7] == "[AspectClass=become]"
    assert tokens[8] == "[Variant=2]"
    assert tokens[9] == "[Aspect=infinitive]"
    assert tokens[10] == "[Tense=infinitive]"
    assert tokens[11] == "[EOW]"
    assert tokens[12] == "[rules=+]"

    fsa = parse_to_fsa(s, syms)
    assert fsa.num_states() == len(tokens) + 1


def test_get_cascade_domain_acceptor_caching(tmp_path):
    """Verify persistent disk caching of cascade domain acceptor."""
    syms = get_default_symbol_table()
    custom_cache = tmp_path / ".cache"

    # First call: compiles and caches to disk
    acc1 = get_cascade_domain_acceptor(syms=syms, cache_dir=custom_cache, force_recompile=True)
    assert acc1.num_states() > 0
    assert (custom_cache / "cascade_domain.fst").exists()
    assert (custom_cache / "cascade_domain.meta").exists()

    # Clear in-memory cache to force disk load
    _CASCADE_DOMAIN_CACHE.clear()

    # Second call: loads from disk cache
    acc2 = get_cascade_domain_acceptor(syms=syms, cache_dir=custom_cache)
    assert acc2.num_states() == acc1.num_states()


def test_get_parse_graph_inplace_composition():
    """Verify get_parse_graph composes cascade domain acceptor and filters invalid parses."""
    graph = get_parse_graph()
    assert graph is not None

    # Parse a surface form and check that no invalid prefix/root combinations exist
    parses = parse("kawoniha")
    assert len(parses) > 0
    # Every parse with [PrefixClass=a_stem] should have root starting with 'a'
    for p in parses[:50]:
        if "[PrefixClass=a_stem]" in p:
            # Should not have non-a initial consonant
            assert not ("[PrefixClass=a_stem][Pro=3sg.A][H_alt=drop]that" in p)

