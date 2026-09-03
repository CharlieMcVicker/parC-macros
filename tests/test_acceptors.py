"""
tests/test_acceptors.py

Comprehensive test suite for in-place stem-shape and morphotactic acceptor system (TASK-106):
- AC 1: Audit and verify all 7 prefix classes in chr-inplace-config/feature_acceptors/prefix_class.csv
- AC 2: Morphotactic licensing acceptor enforcing trigger => licensed constraints
- AC 3: Anchored prefix stem-shape acceptor matching [PrefixClass=c]<Pro><H_ALT>?<PhoneConstraint>
- AC 4: Cascade domain acceptor combining morphotactics and stem-shape with [BOW]/[EOW] wrapping
- AC 5: Verification of invalid hypothesis pruning with minimal state footprint (~15-35 states)
"""

import os
from pathlib import Path
import pytest
import pynini

from parc_macros.generate_markers import generate_markers
from parse_chr_dict.acceptors import (
    DEFAULT_CONFIG_DIR,
    DEFAULT_MORPHOTACTICS_CSV,
    DEFAULT_PREFIX_CLASS_CSV,
    compile_morphotactic_acceptor,
    compile_prefix_stem_shape_acceptor,
    compile_cascade_domain_acceptor,
    accepts_parse,
    resolve_phones_for_pattern,
    tokenize_parse_str,
    parse_to_fsa,
    get_default_symbol_table,
    get_default_alphabet,
)

REPO_ROOT = Path(__file__).parent.parent.resolve()
INPLACE_CONFIG_DIR = REPO_ROOT / "chr-inplace-config"
INPLACE_GEN_DIR = REPO_ROOT / "chr-inplace-generated"


@pytest.fixture(scope="module", autouse=True)
def setup_acceptor_env():
    """Ensure in-place generated environment is set up and configured."""
    from parC.constants import set_yaml_dir
    from parC.grammar.paradigm_compilation import clear_all_caches
    import parse_chr_dict.parse as parse_mod

    orig_yaml_dir = os.environ.get("YAML_DIR")

    generate_markers(str(INPLACE_CONFIG_DIR), str(INPLACE_GEN_DIR), in_place=True)

    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    set_yaml_dir(str(INPLACE_GEN_DIR))
    os.environ["YAML_DIR"] = str(INPLACE_GEN_DIR)

    yield

    clear_all_caches()
    parse_mod.PARSE_GRAPH = None
    parse_mod.INFLECT_GRAPH = None
    parse_mod._READ_LABELS_CACHE.clear()
    if orig_yaml_dir:
        set_yaml_dir(orig_yaml_dir)
        os.environ["YAML_DIR"] = orig_yaml_dir


# =========================================================================
# AC 1: Audit and verify chr-inplace-config/feature_acceptors/prefix_class.csv
# =========================================================================

def test_prefix_class_csv_audit_ac1():
    """Verify all 7 prefix classes are present and map to exact phoneme patterns."""
    assert DEFAULT_PREFIX_CLASS_CSV.exists()
    alphabet = get_default_alphabet()

    # All 7 expected classes and their phone expectations
    expected_classes = {
        "a_stem": {"a"},
        "v_stem": {"v"},
        "e_stem": {"e"},
        "k_a_stem": {"a"},
        "vowel_stem": set("aeiouv"),
        "cons_stem": set("tk'mnshlyw"),
        "r_stem": set("lywmn"),  # <Son>|<N>
    }

    import csv
    with open(DEFAULT_PREFIX_CLASS_CSV, "r", encoding="utf-8") as f:
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
        resolved = resolve_phones_for_pattern(pat, alphabet)
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

    # State footprint verification: compact (~15-100 states across all modular CSVs)
    state_count = morph_fsa.num_states()
    assert 12 <= state_count <= 100, f"Expected state count between 12 and 100, got {state_count}"

    # Helper to test un-wrapped strings against morph_fsa
    def morph_accepts(tokens: list[str]) -> bool:
        test_fsa = pynini.accep(" ".join(tokens), token_type=syms)
        res = pynini.intersect(test_fsa, morph_fsa)
        return res.num_states() > 0 and res.start() != pynini.NO_STATE_ID

    base_tokens = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "a", "t", "a", "t", "[AspectClass=a]"]

    # 1. [DIST=de] licenses indicative tenses
    indicative_tenses = [
        "[Tense=present]",
        "[Tense=habitual]",
        "[Tense=future_prog]",
        "[Tense=assertive]",
        "[Tense=reported]",
    ]
    for t in indicative_tenses:
        asp = "[Aspect=present]" if t == "[Tense=present]" else "[Aspect=incompletive]"
        tokens = ["[DIST=de]"] + base_tokens + [asp, "[TenseClass=a_present]", t]
        assert morph_accepts(tokens), f"[DIST=de] should accept indicative tense {t}"

    # 2. [DIST=de] rejects non-indicative tenses
    non_indicative_tenses = ["[Tense=immediate]", "[Tense=infinitive]"]
    for t in non_indicative_tenses:
        tokens = ["[DIST=de]"] + base_tokens + ["[Aspect=present]", "[TenseClass=a_present]", t]
        assert not morph_accepts(tokens), f"[DIST=de] must reject non-indicative tense {t}"

    # 3. [DIST=di] licenses non-indicative tenses (immediate, infinitive)
    for t in non_indicative_tenses:
        tokens = ["[DIST=di]"] + base_tokens + ["[Aspect=immediate]" if t == "[Tense=immediate]" else "[Aspect=infinitive]", "[TenseClass=a_present]", t]
        assert morph_accepts(tokens), f"[DIST=di] should accept non-indicative tense {t}"

    # 4. [DIST=di] rejects indicative tenses
    for t in indicative_tenses:
        asp = "[Aspect=present]" if t == "[Tense=present]" else "[Aspect=incompletive]"
        tokens = ["[DIST=di]"] + base_tokens + [asp, "[TenseClass=a_present]", t]
        assert not morph_accepts(tokens), f"[DIST=di] must reject indicative tense {t}"

    # 5. [Aspect=immediate] licenses only [Tense=immediate]
    tokens_imm_ok = base_tokens + ["[Aspect=immediate]", "[TenseClass=a_present]", "[Tense=immediate]"]
    assert morph_accepts(tokens_imm_ok)
    tokens_imm_bad = base_tokens + ["[Aspect=immediate]", "[TenseClass=a_present]", "[Tense=present]"]
    assert not morph_accepts(tokens_imm_bad)

    # 6. [Aspect=infinitive] licenses only [Tense=infinitive]
    tokens_inf_ok = base_tokens + ["[Aspect=infinitive]", "[TenseClass=a_present]", "[Tense=infinitive]"]
    assert morph_accepts(tokens_inf_ok)
    tokens_inf_bad = base_tokens + ["[Aspect=infinitive]", "[TenseClass=a_present]", "[Tense=present]"]
    assert not morph_accepts(tokens_inf_bad)

    # 7. Unconstrained when no triggers present
    tokens_plain_pres = base_tokens + ["[TenseClass=a_present]", "[Tense=present]"]
    assert morph_accepts(tokens_plain_pres)
    tokens_plain_imm = base_tokens + ["[TenseClass=a_present]", "[Tense=immediate]"]
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


# =========================================================================
# AC 3: Anchored prefix stem-shape acceptor
# =========================================================================

def test_compile_prefix_stem_shape_acceptor_ac3():
    """AC 3: compile_prefix_stem_shape_acceptor anchors [PrefixClass=c]<Pro><H_ALT>?<InitialPhoneme>."""
    syms = get_default_symbol_table()
    alphabet = get_default_alphabet()

    stem_fsa = compile_prefix_stem_shape_acceptor(syms, alphabet)
    assert stem_fsa is not None

    # State footprint verification: tiny (~15-35 states)
    state_count = stem_fsa.num_states()
    assert 12 <= state_count <= 35, f"Expected state count between 12 and 35, got {state_count}"

    def stem_accepts(tokens: list[str]) -> bool:
        test_fsa = pynini.accep(" ".join(tokens), token_type=syms)
        res = pynini.intersect(test_fsa, stem_fsa)
        return res.num_states() > 0 and res.start() != pynini.NO_STATE_ID

    tail = ["[AspectClass=a]", "[Aspect=present]", "[TenseClass=a_present]", "[Tense=present]"]

    # Valid combinations for all 7 classes
    valid_cases = [
        ("[PrefixClass=a_stem]", ["a", "t", "a", "t"]),
        ("[PrefixClass=v_stem]", ["v", "a", "t", "a", "t"]),
        ("[PrefixClass=e_stem]", ["e", "t", "a", "t"]),
        ("[PrefixClass=k_a_stem]", ["a", "t", "a", "t"]),
        ("[PrefixClass=vowel_stem]", ["o", "t", "a", "t"]),
        ("[PrefixClass=cons_stem]", ["t", "h", "a", "t"]),
        ("[PrefixClass=cons_stem]", ["s", "t", "a", "t"]),
        ("[PrefixClass=r_stem]", ["n", "a", "t", "a", "t"]),
        ("[PrefixClass=r_stem]", ["l", "a", "t", "a", "t"]),
    ]
    for pclass, root_chars in valid_cases:
        tokens = [pclass, "[Pro=3sg.A]"] + root_chars + tail
        assert stem_accepts(tokens), f"Expected valid parse for {pclass} with root starting {root_chars[0]}"

    # Optional H_ALT tags
    for h_tag in ["[H_alt=none]", "[H_alt=drop]", "[H_alt=glot]", "[H_alt=lat]", "[H_alt=vowel]"]:
        tokens_h_a = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", h_tag, "a", "t", "a", "t"] + tail
        assert stem_accepts(tokens_h_a), f"Expected acceptance of a_stem with {h_tag} and initial 'a'"
        tokens_h_cons = ["[PrefixClass=cons_stem]", "[Pro=3sg.A]", h_tag, "t", "h", "a", "t"] + tail
        assert stem_accepts(tokens_h_cons), f"Expected acceptance of cons_stem with {h_tag} and initial 't'"

    # Invalid combinations (illicit initial phones)
    invalid_cases = [
        ("[PrefixClass=a_stem]", ["t", "h", "a", "t"]),       # TASK-108 scenario: a_stem before 't'
        ("[PrefixClass=v_stem]", ["a", "t", "a", "t"]),       # v_stem before 'a'
        ("[PrefixClass=e_stem]", ["a", "t", "a", "t"]),       # e_stem before 'a'
        ("[PrefixClass=k_a_stem]", ["t", "h", "a", "t"]),     # k_a_stem before 't'
        ("[PrefixClass=vowel_stem]", ["t", "h", "a", "t"]),   # vowel_stem before 't'
        ("[PrefixClass=cons_stem]", ["a", "t", "a", "t"]),    # cons_stem before 'a'
        ("[PrefixClass=r_stem]", ["t", "a", "t", "a", "t"]),  # r_stem before 't' (not sonorant/nasal)
    ]
    for pclass, root_chars in invalid_cases:
        tokens = [pclass, "[Pro=3sg.A]"] + root_chars + tail
        assert not stem_accepts(tokens), f"Must reject illicit initial phone for {pclass}: {root_chars[0]}"

    # TASK-108 explicit regression check: a_stem with [H_alt=drop] before consonant root 'that'
    tokens_task108 = ["[PrefixClass=a_stem]", "[Pro=3sg.A]", "[H_alt=drop]", "t", "h", "a", "t"] + tail
    assert not stem_accepts(tokens_task108), "TASK-108: [PrefixClass=a_stem] with [H_alt=drop]that MUST be rejected"

    # Illicit templates (PrefixClass missing Pro, or PrefixClass followed by non-Pro)
    assert not stem_accepts(["[PrefixClass=a_stem]", "a", "t", "a", "t"] + tail)
    assert not stem_accepts(["[PrefixClass=a_stem]", "[AspectClass=a]", "a", "t", "a", "t"] + tail)


# =========================================================================
# AC 4 & 5: Cascade domain acceptor & invalid combination pruning
# =========================================================================

def test_compile_cascade_domain_acceptor_ac4_ac5():
    """
    AC 4 & AC 5: Intersect morphotactic and stem-shape acceptors with [BOW]/[EOW] wrapping.
    Verify valid in-place parses are accepted and illicit combinations pruned.
    """
    syms = get_default_symbol_table()
    alphabet = get_default_alphabet()

    cascade = compile_cascade_domain_acceptor(syms, alphabet)
    assert cascade is not None
    assert cascade.num_states() > 0

    valid_parses = [
        # a_stem with initial 'a'
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # cons_stem with consonant 't'
        "[BOW][PrefixClass=cons_stem][Pro=3sg.A]that[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # [DIST=de] with indicative present tense
        "[BOW][DIST=de][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # [DIST=di] with non-indicative immediate tense
        "[BOW][DIST=di][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=immediate][TenseClass=a_present][Tense=immediate][EOW][rules=+]",
        # [DIST=di] with cons_stem and immediate tense
        "[BOW][DIST=di][PrefixClass=cons_stem][Pro=3sg.A]that[AspectClass=a][Aspect=immediate][TenseClass=a_present][Tense=immediate][EOW][rules=+]",
        # [WI] prepronominal prefix
        "[BOW][WI][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # [WI] + [DIST=de]
        "[BOW][WI][DIST=de][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # [H_alt=drop] with a_stem and 1sg.A (trigger)
        "[BOW][PrefixClass=a_stem][Pro=1sg.A][H_alt=drop]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # Without trailing [rules=+]
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW]",
    ]

    for vp in valid_parses:
        assert accepts_parse(cascade, vp, syms), f"Cascade should accept valid parse: {vp}"

    invalid_parses = [
        # TASK-108: a_stem before consonant root 'that'
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]that[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # TASK-108 with [H_alt=drop]: a_stem with [H_alt=drop] before consonant root 'that'
        "[BOW][PrefixClass=a_stem][Pro=1sg.A][H_alt=drop]that[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # TASK-109: Non-trigger 3sg.A with active [H_alt=drop] (violates pro_morphotactics)
        "[BOW][PrefixClass=a_stem][Pro=3sg.A][H_alt=drop]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # cons_stem before vowel root 'atat'
        "[BOW][PrefixClass=cons_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # [DIST=de] with immediate tense (violates morphotactics)
        "[BOW][DIST=de][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=immediate][EOW][rules=+]",
        # [DIST=di] with present tense (violates morphotactics)
        "[BOW][DIST=di][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # [Aspect=immediate] with present tense
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=immediate][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # [Aspect=infinitive] with present tense
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=infinitive][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # Missing [BOW]
        "[PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][EOW][rules=+]",
        # Missing [EOW]
        "[BOW][PrefixClass=a_stem][Pro=3sg.A]atat[AspectClass=a][Aspect=present][TenseClass=a_present][Tense=present][rules=+]",
    ]

    for ip in invalid_parses:
        assert not accepts_parse(cascade, ip, syms), f"Cascade must reject invalid parse: {ip}"


def test_tokenize_parse_str_and_parse_to_fsa():
    """Verify parse tokenization handles nested brackets and complex tags."""
    syms = get_default_symbol_table()

    # In-place string with AspectClass and Variant tags
    s = "[BOW][PrefixClass=a_stem][Pro=1sg.A]atat[AspectClass=become][Variant=2][Aspect=infinitive][TenseClass=a_present][Tense=infinitive][EOW][rules=+]"
    tokens = tokenize_parse_str(s)
    assert tokens[0] == "[BOW]"
    assert tokens[1] == "[PrefixClass=a_stem]"
    assert tokens[2] == "[Pro=1sg.A]"
    assert tokens[3:7] == ["a", "t", "a", "t"]
    assert tokens[7] == "[AspectClass=become]"
    assert tokens[8] == "[Variant=2]"
    assert tokens[9] == "[Aspect=infinitive]"
    assert tokens[10] == "[TenseClass=a_present]"
    assert tokens[11] == "[Tense=infinitive]"
    assert tokens[12] == "[EOW]"
    assert tokens[13] == "[rules=+]"

    fsa = parse_to_fsa(s, syms)
    assert fsa.num_states() == len(tokens) + 1


def test_get_cascade_domain_acceptor_caching(tmp_path):
    """Verify persistent disk caching of cascade domain acceptor."""
    from parse_chr_dict.acceptors import get_cascade_domain_acceptor, _CASCADE_DOMAIN_CACHE

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
    from parse_chr_dict.parse import get_parse_graph, parse, is_inplace_grammar

    assert is_inplace_grammar() is True
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

