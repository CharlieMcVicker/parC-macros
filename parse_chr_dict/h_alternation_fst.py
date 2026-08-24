from __future__ import annotations
from functools import lru_cache
from typing import Set
import pynini

# Phoneme inventory for Cherokee
CHEROKEE_VOWELS = list("aeiouv")
CHEROKEE_CONSONANTS = list("tkmnshlywdg")  # Non-glottal, non-vowel consonants
CHEROKEE_ALL_CHARS = CHEROKEE_VOWELS + CHEROKEE_CONSONANTS + ["'"]


@lru_cache(maxsize=1)
def get_sigma() -> pynini.Fst:
    """Returns the alphabet union acceptor."""
    return pynini.union(*CHEROKEE_ALL_CHARS).optimize()


@lru_cache(maxsize=1)
def get_sigma_star() -> pynini.Fst:
    """Returns the universal Kleene-star acceptor over the Cherokee alphabet."""
    return get_sigma().star.optimize()


@lru_cache(maxsize=1)
def get_vowels_fsa() -> pynini.Fst:
    """Returns union acceptor over all vowels."""
    return pynini.union(*CHEROKEE_VOWELS).optimize()


@lru_cache(maxsize=1)
def get_consonants_fsa() -> pynini.Fst:
    """Returns union acceptor over all non-glottal consonants."""
    return pynini.union(*CHEROKEE_CONSONANTS).optimize()


@lru_cache(maxsize=1)
def build_drop_first_h_fst() -> pynini.Fst:
    """FST that drops the first 'h' in a string, or acts as identity if no 'h' exists."""
    sigma = get_sigma()
    sigma_star = get_sigma_star()
    not_h = pynini.difference(sigma, pynini.accep("h")).star
    return pynini.union(not_h, not_h + pynini.cross("h", "") + sigma_star).optimize()


@lru_cache(maxsize=1)
def build_first_h_to_glottal_fst() -> pynini.Fst:
    """FST that converts the first 'h' to a glottal stop "'", or identity if no 'h'."""
    sigma = get_sigma()
    sigma_star = get_sigma_star()
    not_h = pynini.difference(sigma, pynini.accep("h")).star
    return pynini.union(not_h, not_h + pynini.cross("h", "'") + sigma_star).optimize()


@lru_cache(maxsize=1)
def build_drop_h_in_deaffricated_lateral_fst() -> pynini.Fst:
    """FST that converts the first lateral 'lh' into 'tl', or identity if no 'lh'."""
    sigma = get_sigma()
    sigma_star = get_sigma_star()
    no_lh = (
        pynini.difference(sigma, pynini.accep("l"))
        | (pynini.accep("l") + pynini.difference(sigma, pynini.accep("h")))
    ).star + pynini.accep("l").ques
    return pynini.union(no_lh, no_lh + pynini.cross("lh", "tl") + sigma_star).optimize()


@lru_cache(maxsize=1)
def build_prevent_c_glottal_cluster_fst() -> pynini.Fst:
    """FST that metathesizes consonant-glottal clusters (C+)' into '(C+)."""
    sigma_star = get_sigma_star()
    c_plus = get_consonants_fsa().plus
    t_insert = pynini.cdrewrite(pynini.cross("", "'"), "", c_plus + "'", sigma_star)
    t_delete = pynini.cdrewrite(pynini.cross("'", ""), c_plus, "", sigma_star)
    return pynini.compose(t_insert, t_delete).optimize()


@lru_cache(maxsize=1)
def build_recreate_c_glottal_clusters_fst() -> pynini.Fst:
    """FST that metathesizes '(C+) back to (C+)'. Reverse of prevent_c_glottal_cluster."""
    sigma_star = get_sigma_star()
    c_plus = get_consonants_fsa().plus
    t_insert = pynini.cdrewrite(pynini.cross("", "'"), "'" + c_plus, "", sigma_star)
    t_delete = pynini.cdrewrite(pynini.cross("'", ""), "", c_plus + "'", sigma_star)
    return pynini.compose(t_insert, t_delete).optimize()


@lru_cache(maxsize=1)
def build_possible_alternates_fst() -> pynini.Fst:
    """FST that maps an h-grade input into all possible alternate forms (with cluster prevention)."""
    sigma_star = get_sigma_star()
    raw_alternates = pynini.union(
        sigma_star,
        build_drop_first_h_fst(),
        build_first_h_to_glottal_fst(),
        build_drop_h_in_deaffricated_lateral_fst(),
    ).optimize()
    return pynini.compose(raw_alternates, build_prevent_c_glottal_cluster_fst()).optimize()


@lru_cache(maxsize=1)
def build_vowel_restoration_fst() -> pynini.Fst:
    """FST mapping syncopated / h-dropped stem to restored glottal stem.
    
    Includes:
    - Identity mapping
    - Single vowel restoration anywhere in the string
    - 's' + V + 'hs' restoration after 's'
    - 'a' -> 'i' clothing word quality shift
    """
    sigma = get_sigma()
    sigma_star = get_sigma_star()
    v = get_vowels_fsa()

    f_id = sigma_star
    f_single_v = (sigma_star + pynini.cross("", v) + sigma_star).optimize()
    f_vhs = (sigma_star + pynini.accep("s") + pynini.cross("", v + "hs") + sigma_star).optimize()
    f_quality = pynini.closure(pynini.union(sigma, pynini.cross("a", "i"))).optimize()

    return pynini.union(f_id, f_single_v, f_vhs, f_quality).optimize()


@lru_cache(maxsize=1)
def build_grades_compatible_fst() -> pynini.Fst:
    """Full transducer mapping h-grade to compatible glottal-grade strings."""
    return pynini.compose(
        build_possible_alternates_fst(),
        build_vowel_restoration_fst(),
    ).optimize()


def fst_possible_alternates(h_form: str, fix_clusters: bool = True) -> Set[str]:
    """Computes possible alternates for an h-grade stem using FST composition."""
    fst = (
        build_possible_alternates_fst()
        if fix_clusters
        else pynini.union(
            get_sigma_star(),
            build_drop_first_h_fst(),
            build_first_h_to_glottal_fst(),
            build_drop_h_in_deaffricated_lateral_fst(),
        ).optimize()
    )
    res = pynini.compose(pynini.accep(h_form), fst)
    if res.num_states() == 0:
        return set()
    out = pynini.project(res, "output").optimize()
    return {item[1] for item in out.paths().items()}


def fst_prevent_c_glottal_cluster(form: str) -> str:
    """Metathesizes (C+)' into '(C+) using FST."""
    res = pynini.compose(pynini.accep(form), build_prevent_c_glottal_cluster_fst())
    if res.num_states() == 0:
        return form
    out = pynini.project(res, "output").optimize()
    for item in out.paths().items():
        return item[1]
    return form


def fst_recreate_c_glottal_clusters(surface: str) -> str:
    """Metathesizes '(C+) into (C+)' using FST."""
    res = pynini.compose(pynini.accep(surface), build_recreate_c_glottal_clusters_fst())
    if res.num_states() == 0:
        return surface
    out = pynini.project(res, "output").optimize()
    for item in out.paths().items():
        return item[1]
    return surface


def fst_grades_are_compatible(*, h: str, glottal: str) -> bool:
    """Checks if `h` and `glottal` grades are compatible via direct FST composition."""
    res = pynini.compose(
        pynini.compose(pynini.accep(h), build_grades_compatible_fst()),
        pynini.accep(glottal),
    )
    return res.num_states() > 0
