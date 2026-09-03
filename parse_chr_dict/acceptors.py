"""
parse_chr_dict/acceptors.py

Deterministic FST compiler functions for in-place morphotactic licensing,
anchored prefix stem-shape constraints, and cascade domain acceptors.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Iterable, Set

import pynini

REPO_ROOT = Path(__file__).parent.parent.resolve()
DEFAULT_CONFIG_DIR = REPO_ROOT / "chr-inplace-config"
DEFAULT_MORPHOTACTICS_CSV = DEFAULT_CONFIG_DIR / "feature_acceptors" / "morphotactics.csv"
DEFAULT_PREFIX_CLASS_CSV = DEFAULT_CONFIG_DIR / "feature_acceptors" / "prefix_class.csv"


def get_default_symbol_table() -> pynini.SymbolTable:
    """Returns the default symbol table for the active in-place grammar."""
    from parC.grammar.acceptor_compilation import get_symbol_table
    return get_symbol_table()


def get_default_alphabet():
    """Returns the default AlphabetBlueprint for the active in-place grammar."""
    from parC.grammar.blueprints.alphabet import AlphabetBlueprint
    return AlphabetBlueprint.from_config()


def tokenize_parse_str(s: str) -> list[str]:
    """
    Tokenizes an in-place morpheme parse string into discrete symbol tokens.
    Handles bracket-delimited tags (such as [PrefixClass=a_stem], [AspectClass=become[inf2]])
    and individual phonemic characters outside brackets.
    """
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "[":
            depth = 1
            start = i
            i += 1
            while i < n and depth > 0:
                if s[i] == "[":
                    depth += 1
                elif s[i] == "]":
                    depth -= 1
                i += 1
            tokens.append(s[start:i])
        else:
            tokens.append(s[i])
            i += 1
    return tokens


def parse_to_fsa(parse_str: str, syms: pynini.SymbolTable) -> pynini.Fst:
    """
    Converts a tokenized parse string into a deterministic linear FSA over syms.
    """
    tokens = tokenize_parse_str(parse_str)
    try:
        return pynini.accep(" ".join(tokens), token_type=syms)
    except Exception:
        empty = pynini.Fst()
        empty.set_input_symbols(syms)
        empty.set_output_symbols(syms)
        return empty


def accepts_parse(acceptor: pynini.Fst, parse_str: str, syms: pynini.SymbolTable | None = None) -> bool:
    """
    Tests whether an acceptor FST accepts a given parse string.
    """
    if syms is None:
        syms = get_default_symbol_table()
    test_fsa = parse_to_fsa(parse_str, syms)
    if test_fsa.num_states() == 0 or test_fsa.start() == pynini.NO_STATE_ID:
        return False
    res = pynini.intersect(test_fsa, acceptor)
    return res.num_states() > 0 and res.start() != pynini.NO_STATE_ID


def get_template_sigma(syms: pynini.SymbolTable) -> tuple[pynini.Fst, pynini.Fst, list[str]]:
    """
    Builds the inner template alphabet union FSA (Sigma) and universal Kleene-star (Sigma*)
    over all valid morpheme tags and phonemes in syms, excluding [BOW], [EOW], and [rules=+].
    """
    excluded = {"[BOW]", "[EOW]", "[rules=+]"}
    sym_strings = [
        syms.find(i)
        for i in range(1, syms.num_symbols())
        if syms.find(i) not in excluded
    ]
    sigma = pynini.union(*[pynini.accep(s, token_type=syms) for s in sym_strings]).optimize()
    sigma_star = sigma.star.optimize()
    return sigma, sigma_star, sym_strings


def resolve_phones_for_pattern(pattern: str, alphabet=None) -> set[str]:
    """
    Resolves a phonemic pattern or class reference into a set of Cherokee phone symbols.
    Supports:
      - Raw characters, e.g. 'a', 'v', 'e'
      - Class references, e.g. '<V>', '<C>', '<Son>', '<N>', '<Stops>', '<Frc>'
      - Alternations, e.g. '<Son>|<N>' or '(<Son>|<N>)'
      - Legacy wrapped patterns, e.g. '<Morpheme>*a<Phone>*<Morpheme>*'
    """
    if alphabet is None:
        alphabet = get_default_alphabet()

    pat = pattern.strip()
    # Strip legacy morpheme wrappers if present
    pat = re.sub(r"^<Morpheme>\*", "", pat)
    pat = re.sub(r"<Phone>\*<Morpheme>\*$", "", pat)
    pat = pat.strip()

    if pat.startswith("(") and pat.endswith(")"):
        pat = pat[1:-1].strip()

    parts = pat.split("|")
    phones = set()
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part == "<C>":
            for group in ("<Stops>", "<Frc>", "<Son>", "<N>"):
                if group in alphabet.inventory.item_map:
                    phones.update(alphabet.inventory.item_map[group].phones)
        elif part in alphabet.inventory.item_map:
            phones.update(alphabet.inventory.item_map[part].phones)
        elif part in alphabet.inventory.phones:
            phones.add(part)
        else:
            raise ValueError(f"Cannot resolve phone or group '{part}' in pattern '{pattern}'")
    return phones


def compile_morphotactic_acceptor(
    syms: pynini.SymbolTable | None = None,
    alphabet=None,
    rules_csv: str | Path | None = None,
) -> pynini.Fst:
    """
    Constructs a deterministic finite-state acceptor (DFA) over the linear template alphabet
    enforcing that if trigger T is present, the target slot must contain one of the licensed values.
    If T is absent, the target slot is unconstrained.

    Rules are read from rules_csv (defaults to chr-inplace-config/feature_acceptors/morphotactics.csv).
    """
    if alphabet is None:
        alphabet = get_default_alphabet()
    if syms is None:
        syms = alphabet.get_symbol_table() if hasattr(alphabet, "get_symbol_table") else get_default_symbol_table()

    if rules_csv is None:
        rules_csv = DEFAULT_MORPHOTACTICS_CSV
    rules_path = Path(rules_csv)
    if not rules_path.is_absolute():
        rules_path = REPO_ROOT / rules_path

    _, sigma_star, all_syms = get_template_sigma(syms)

    # Read morphotactic licensing rules
    rules: list[tuple[str, str, list[str]]] = []
    with open(rules_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = None
        for row in reader:
            if not row or not row[0] or row[0].startswith("#"):
                continue
            if header is None:
                header = [c.strip() for c in row]
                continue
            row_dict = dict(zip(header, [c.strip() for c in row]))
            trigger = row_dict.get("trigger", "")
            target_slot = row_dict.get("target_slot", "")
            licensed_str = row_dict.get("licensed", "")
            if trigger and target_slot and licensed_str:
                licensed_vals = [v.strip() for v in licensed_str.split("|") if v.strip()]
                rules.append((trigger, target_slot, licensed_vals))

    combined_acceptor = sigma_star
    for trigger, target_slot, licensed in rules:
        # Determine all possible values for target_slot in syms
        slot_prefix = f"[{target_slot}=" if not target_slot.startswith("[") else target_slot.rstrip("]") + "="
        all_slot_vals = [s for s in all_syms if s.startswith(slot_prefix) and s.endswith("]")]
        unlicensed = [v for v in all_slot_vals if v not in licensed]
        if not unlicensed:
            continue

        trigger_fsa = pynini.accep(trigger, token_type=syms)
        unlicensed_fsa = pynini.union(*[pynini.accep(u, token_type=syms) for u in unlicensed]).optimize()

        # Disallow sequences where trigger co-occurs with any unlicensed value in either order
        bad_forward = pynini.concat(
            sigma_star,
            pynini.concat(trigger_fsa, pynini.concat(sigma_star, pynini.concat(unlicensed_fsa, sigma_star))),
        )
        bad_reverse = pynini.concat(
            sigma_star,
            pynini.concat(unlicensed_fsa, pynini.concat(sigma_star, pynini.concat(trigger_fsa, sigma_star))),
        )
        bad = pynini.union(bad_forward, bad_reverse).optimize()

        rule_dfa = pynini.difference(sigma_star, bad).optimize()
        combined_acceptor = pynini.intersect(combined_acceptor, rule_dfa).optimize()

    return combined_acceptor


def compile_prefix_stem_shape_acceptor(
    syms: pynini.SymbolTable | None = None,
    alphabet=None,
    rules_csv: str | Path | None = None,
) -> pynini.Fst:
    """
    Enforces anchored sequence in the template:
    <PrefixClass> <Pro> <H_ALT>? <InitialPhoneme>

    For every prefix class c in rules, [PrefixClass=c] must be followed by <Pro>,
    optional <H_ALT>, and a root whose initial phoneme satisfies PhonemeConstraint_c.

    Rules are read from rules_csv (defaults to chr-inplace-config/feature_acceptors/prefix_class.csv).
    """
    if alphabet is None:
        alphabet = get_default_alphabet()
    if syms is None:
        syms = alphabet.get_symbol_table() if hasattr(alphabet, "get_symbol_table") else get_default_symbol_table()

    if rules_csv is None:
        rules_csv = DEFAULT_PREFIX_CLASS_CSV
    rules_path = Path(rules_csv)
    if not rules_path.is_absolute():
        rules_path = REPO_ROOT / rules_path

    _, sigma_star, all_syms = get_template_sigma(syms)

    # Pro tags in syms
    pro_tags = [s for s in all_syms if s.startswith("[Pro=") and s.endswith("]")]
    if not pro_tags:
        raise ValueError("No [Pro=...] tags found in symbol table.")
    pro_fsa = pynini.union(*[pynini.accep(p, token_type=syms) for p in pro_tags]).optimize()

    # Optional H_ALT tags in syms
    h_alt_tags = [s for s in all_syms if s.startswith("[H_") and s.endswith("]")]
    empty_fsa = pynini.accep("", token_type=syms)
    if h_alt_tags:
        h_alt_opt = pynini.union(empty_fsa, *[pynini.accep(h, token_type=syms) for h in h_alt_tags]).optimize()
    else:
        h_alt_opt = empty_fsa

    all_phones = sorted(list(alphabet.inventory.phones))

    # Read prefix class rules
    class_rules: list[tuple[str, set[str]]] = []
    with open(rules_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = None
        for row in reader:
            if not row or not row[0] or row[0].startswith("#"):
                continue
            if header is None:
                header = [c.strip() for c in row]
                continue
            pclass = row[0].strip()
            pattern = row[1].strip() if len(row) > 1 else ""
            if pclass and pattern:
                allowed_phones = resolve_phones_for_pattern(pattern, alphabet)
                class_rules.append((pclass, allowed_phones))

    bad_seqs: list[pynini.Fst] = []
    prefix_class_fsas: list[pynini.Fst] = []

    for pclass, allowed_phones in class_rules:
        tag_str = f"[PrefixClass={pclass}]"
        c_fsa = pynini.accep(tag_str, token_type=syms)
        prefix_class_fsas.append(c_fsa)

        disallowed_phones = [p for p in all_phones if p not in allowed_phones]
        if disallowed_phones:
            dis_fsa = pynini.union(*[pynini.accep(p, token_type=syms) for p in disallowed_phones]).optimize()
            bad_phone_seq = pynini.concat(
                sigma_star,
                pynini.concat(c_fsa, pynini.concat(pro_fsa, pynini.concat(h_alt_opt, pynini.concat(dis_fsa, sigma_star)))),
            )
            bad_seqs.append(bad_phone_seq)

    all_pclasses_fsa = pynini.union(*prefix_class_fsas).optimize()

    # Disallow [PrefixClass=c] followed by non-Pro
    non_pro_syms = [s for s in all_syms if not s.startswith("[Pro=")]
    if non_pro_syms:
        non_pro_fsa = pynini.union(*[pynini.accep(s, token_type=syms) for s in non_pro_syms]).optimize()
        bad_no_pro = pynini.concat(
            sigma_star,
            pynini.concat(all_pclasses_fsa, pynini.concat(non_pro_fsa, sigma_star)),
        )
        bad_seqs.append(bad_no_pro)

    # Disallow [PrefixClass=c] Pro (H_ALT)? followed by non-phone (e.g. adjacent morpheme tag)
    non_phone_syms = [s for s in all_syms if s not in all_phones and not s.startswith("[H_")]
    if non_phone_syms:
        non_phone_fsa = pynini.union(*[pynini.accep(s, token_type=syms) for s in non_phone_syms]).optimize()
        bad_no_phone = pynini.concat(
            sigma_star,
            pynini.concat(
                all_pclasses_fsa,
                pynini.concat(pro_fsa, pynini.concat(h_alt_opt, pynini.concat(non_phone_fsa, sigma_star))),
            ),
        )
        bad_seqs.append(bad_no_phone)

    total_bad = pynini.union(*bad_seqs).optimize()
    stem_shape_dfa = pynini.difference(sigma_star, total_bad).optimize()
    return stem_shape_dfa


def compile_cascade_domain_acceptor(
    syms: pynini.SymbolTable | None = None,
    alphabet=None,
    morph_rules_csv: str | Path | None = None,
    prefix_rules_csv: str | Path | None = None,
) -> pynini.Fst:
    """
    Compiles the full cascade domain acceptor by intersecting the morphotactic licensing
    and anchored prefix stem-shape acceptors, wrapped with [BOW] on the left and [EOW]
    (with optional trailing [rules=+]) on the right.
    """
    if alphabet is None:
        alphabet = get_default_alphabet()
    if syms is None:
        syms = alphabet.get_symbol_table() if hasattr(alphabet, "get_symbol_table") else get_default_symbol_table()

    morph_acceptor = compile_morphotactic_acceptor(syms, alphabet, rules_csv=morph_rules_csv)
    stem_acceptor = compile_prefix_stem_shape_acceptor(syms, alphabet, rules_csv=prefix_rules_csv)

    inner_acceptor = pynini.intersect(morph_acceptor, stem_acceptor).optimize()

    bow_fsa = pynini.accep("[BOW]", token_type=syms)
    eow_fsa = pynini.accep("[EOW]", token_type=syms)
    rules_opt = pynini.union(
        pynini.accep("", token_type=syms),
        pynini.accep("[rules=+]", token_type=syms),
    ).optimize()

    cascade_acceptor = pynini.concat(
        bow_fsa,
        pynini.concat(inner_acceptor, pynini.concat(eow_fsa, rules_opt)),
    ).optimize()

    return cascade_acceptor


_CASCADE_DOMAIN_CACHE: dict[str, pynini.Fst] = {}


def compute_domain_acceptor_cache_key(
    syms: pynini.SymbolTable,
    morph_rules_path: Path,
    prefix_rules_path: Path,
) -> str:
    """Computes a SHA-256 cache key over morphotactics rules, prefix class rules, and symbol table."""
    h = hashlib.sha256()
    if morph_rules_path.exists():
        h.update(morph_rules_path.read_bytes())
    if prefix_rules_path.exists():
        h.update(prefix_rules_path.read_bytes())
    h.update(str(syms.num_symbols()).encode("utf-8"))
    for i in range(min(100, syms.num_symbols())):
        h.update(syms.find(i).encode("utf-8"))
    return h.hexdigest()


def get_cascade_domain_acceptor(
    syms: pynini.SymbolTable | None = None,
    alphabet=None,
    morph_rules_csv: str | Path | None = None,
    prefix_rules_csv: str | Path | None = None,
    cache_dir: Path | str | None = None,
    force_recompile: bool = False,
) -> pynini.Fst:
    """
    Retrieves the cascade domain acceptor, loading from persistent disk cache
    keyed by rule file and symbol table checksums if valid, or compiling and caching it.
    Ensures instantaneous parse graph startup.
    """
    if alphabet is None:
        alphabet = get_default_alphabet()
    if syms is None:
        syms = (
            alphabet.get_symbol_table()
            if hasattr(alphabet, "get_symbol_table")
            else get_default_symbol_table()
        )

    if morph_rules_csv is None:
        morph_rules_csv = DEFAULT_MORPHOTACTICS_CSV
    morph_rules_path = Path(morph_rules_csv)
    if not morph_rules_path.is_absolute():
        morph_rules_path = REPO_ROOT / morph_rules_path

    if prefix_rules_csv is None:
        prefix_rules_csv = DEFAULT_PREFIX_CLASS_CSV
    prefix_rules_path = Path(prefix_rules_csv)
    if not prefix_rules_path.is_absolute():
        prefix_rules_path = REPO_ROOT / prefix_rules_path

    cache_key = compute_domain_acceptor_cache_key(syms, morph_rules_path, prefix_rules_path)

    # Check in-memory cache
    if not force_recompile and cache_key in _CASCADE_DOMAIN_CACHE:
        return _CASCADE_DOMAIN_CACHE[cache_key].copy()

    # Determine primary cache directory
    if cache_dir is not None:
        c_dir = Path(cache_dir)
    else:
        from parC.constants import get_yaml_dir
        yd = Path(get_yaml_dir())
        if not yd.is_absolute():
            yd = REPO_ROOT / yd
        c_dir = yd / ".cache"

    c_dir.mkdir(parents=True, exist_ok=True)
    cache_file = c_dir / "cascade_domain.fst"
    meta_file = c_dir / "cascade_domain.meta"

    # Also keep repo root .cache in sync for backwards compatibility / local checks
    repo_cache_dir = REPO_ROOT / ".cache"
    repo_cache_file = repo_cache_dir / "cascade_domain.fst"
    repo_meta_file = repo_cache_dir / "cascade_domain.meta"

    if not force_recompile:
        for f_path, m_path in [(cache_file, meta_file), (repo_cache_file, repo_meta_file)]:
            if f_path.exists() and m_path.exists():
                try:
                    meta = json.loads(m_path.read_text(encoding="utf-8"))
                    if meta.get("cache_key") == cache_key:
                        fst = pynini.Fst.read(str(f_path))
                        fst.set_input_symbols(syms)
                        fst.set_output_symbols(syms)
                        _CASCADE_DOMAIN_CACHE[cache_key] = fst
                        return fst.copy()
                except Exception:
                    pass

    # Compile cascade domain acceptor
    fst = compile_cascade_domain_acceptor(
        syms=syms,
        alphabet=alphabet,
        morph_rules_csv=morph_rules_path,
        prefix_rules_csv=prefix_rules_path,
    )

    meta_content = json.dumps({
        "cache_key": cache_key,
        "morph_rules": str(morph_rules_path),
        "prefix_rules": str(prefix_rules_path),
    })

    # Save to primary cache
    try:
        fst.write(str(cache_file))
        meta_file.write_text(meta_content, encoding="utf-8")
        fst.write(str(c_dir / "cascade_domain_acceptor.fst"))
    except Exception:
        pass

    # Save to repo root cache
    try:
        repo_cache_dir.mkdir(parents=True, exist_ok=True)
        fst.write(str(repo_cache_file))
        repo_meta_file.write_text(meta_content, encoding="utf-8")
        fst.write(str(repo_cache_dir / "cascade_domain_acceptor.fst"))
    except Exception:
        pass

    _CASCADE_DOMAIN_CACHE[cache_key] = fst
    return fst.copy()

