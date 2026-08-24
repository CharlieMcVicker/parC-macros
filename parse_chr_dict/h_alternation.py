from __future__ import annotations
import re
from typing import Callable, List, Optional, Set

VOWEL_SET: Set[str] = set("aeiouv")

H_ALTERNATION_TRIGGER_PRONOMINALS: Set[str] = {
    "1sg>3sg",
    "2sg>3sg",
    "1sg.A",
}


def is_h_alternation_trigger(pronominal: str) -> bool:
    """Returns True if the pronominal triggers H-alternation (glottal grade)."""
    return pronominal in H_ALTERNATION_TRIGGER_PRONOMINALS


def validate_h_alternation_trigger(pronominal: str, has_h_alt: bool) -> bool:
    """
    Validates that [H_ALT] or H-alternation rule application co-occurs strictly
    with H-alternating trigger prefixes (1sg>3sg, 2sg>3sg, 1sg.A).
    Returns False if has_h_alt is True but pronominal is not a trigger.
    """
    if has_h_alt and not is_h_alternation_trigger(pronominal):
        return False
    return True


def _drop_first_h(h_grade: str) -> str:
    idx = h_grade.find("h")
    if idx != -1:
        return h_grade[:idx] + h_grade[idx + 1 :]
    return h_grade


def _first_h_to_glottal(h_grade: str) -> str:
    idx = h_grade.find("h")
    if idx != -1:
        return h_grade[:idx] + "'" + h_grade[idx + 1 :]
    return h_grade


def prevent_C_glottal_cluster(form: str) -> str:
    # turn all sequences of (C+)' into '(C+)
    # capture consonants as [^aeiouv']
    return re.sub(r"([^aeiouv']+)'", r"'\1", form)


def recreate_C_glottal_clusters(surface: str) -> str:
    return re.sub(r"'([^aeiouv']+)", r"\1'", surface)


def _is_compatible_with_vowel_restoration(restored: str, syncopated: str) -> bool:
    if len(restored) - len(syncopated) not in [0, 1, 3]:
        return False
    i = 0
    j = 0
    quality_shift = False
    skipped = False
    skipped_idx = -1
    while i < len(restored) and j < len(syncopated):
        if restored[i] == syncopated[j]:
            i += 1
            j += 1
        elif restored[i] == "i" and syncopated[j] == "a":
            # clothing words
            quality_shift = True
            i += 1
            j += 1
        else:
            if skipped:
                if (
                    # sometimes we will have a case like
                    #               1234
                    # syncopated:   tsgo
                    #                 ___
                    # restored:     tsihsgo
                    #               1234567
                    skipped_idx == i - 1
                    and restored[skipped_idx - 1] == "s"
                    and restored[i] == "h"
                    and restored[i + 1] == "s"
                ):
                    i += 2
                else:
                    return False
            elif restored[i] in VOWEL_SET:
                skipped = True
                skipped_idx = i
                i += 1
            else:
                return False
    if quality_shift:
        # can't handle this case
        if skipped:
            print("[WARNING] didn't plan for this case")

        return not skipped

    if not skipped:
        return i == len(restored) - 1 and restored[i] in VOWEL_SET

    return True


def _drop_h_in_deaffricated_lateral(h_grade: str) -> str:
    return h_grade.replace("lh", "tl", 1)


def possible_alternates(h_form: str, fix_clusters: bool = True) -> List[str]:
    ways_to_drop: List[Callable[[str], str]] = [
        lambda x: x,
        _drop_h_in_deaffricated_lateral,
        _drop_first_h,
        _first_h_to_glottal,
    ]

    return [
        prevent_C_glottal_cluster(way(h_form)) if fix_clusters else way(h_form)
        for way in ways_to_drop
    ]


def grades_are_compatible(*, h: str, glottal: str) -> bool:
    """Checks if `h` and `glottal` could be respective grades of the same stem or root"""
    for h_dropped in possible_alternates(h):
        if h_dropped == glottal:
            return True
        if _is_compatible_with_vowel_restoration(glottal, h_dropped):
            return True

    return False


# Re-export FST-based implementations
from parse_chr_dict.h_alternation_fst import (
    build_drop_first_h_fst,
    build_first_h_to_glottal_fst,
    build_drop_h_in_deaffricated_lateral_fst,
    build_prevent_c_glottal_cluster_fst,
    build_recreate_c_glottal_clusters_fst,
    build_possible_alternates_fst,
    build_vowel_restoration_fst,
    build_grades_compatible_fst,
    fst_possible_alternates,
    fst_prevent_c_glottal_cluster,
    fst_recreate_c_glottal_clusters,
    fst_grades_are_compatible,
)

