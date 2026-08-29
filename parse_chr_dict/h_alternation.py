from __future__ import annotations
import re
from typing import Callable, List, Optional, Set

VOWEL_SET: Set[str] = set("aeiouv")

H_ALTERNATION_TRIGGER_PRONOMINALS: Set[str] = {
    "1sg>3sg",
    "2sg>3sg",
    "1sg.A",
}


H_ALT_TAGS: Set[str] = {
    "[H_DROP]",
    "[H_GLOT]",
    "[H_LAT]",
    "[H_NONE]",
}


def is_h_alternation_trigger(pronominal: str) -> bool:
    """Returns True if the pronominal triggers H-alternation (glottal grade)."""
    return pronominal in H_ALTERNATION_TRIGGER_PRONOMINALS


def validate_h_alternation_trigger(
    pronominal: str,
    h_alt_tag: Optional[str] | bool = None,
    has_h_alt: Optional[bool] = None,
) -> bool:
    """
    Validates that fine-grained mutation tags ([H_DROP], [H_GLOT], [H_LAT]) or has_h_alt flag
    co-occur strictly with H-alternating trigger prefixes (1sg>3sg, 2sg>3sg, 1sg.A).
    Returns False if mutation tag / has_h_alt is present but pronominal is not a trigger.
    """
    if has_h_alt is not None:
        has_mutation = has_h_alt
    elif isinstance(h_alt_tag, bool):
        has_mutation = h_alt_tag
    elif isinstance(h_alt_tag, str):
        has_mutation = h_alt_tag in {"[H_DROP]", "[H_GLOT]", "[H_LAT]"}
    else:
        has_mutation = False

    if has_mutation and not is_h_alternation_trigger(pronominal):
        return False
    return True


def strip_h_alt_tags(root: str) -> str:
    """Strips fine-grained H-alternation tags ([H_DROP], [H_GLOT], [H_LAT], [H_NONE], [H_ALT]) from a root."""
    for tag in ("[H_DROP]", "[H_GLOT]", "[H_LAT]", "[H_NONE]", "[H_ALT]"):
        root = root.replace(tag, "")
    return root


def determine_h_alt_glottal_root(h_root: str, p_root: str) -> Optional[str]:
    """
    Determines the glottal_root carrying the appropriate [H_ALT] morphotactic tag
    by checking whether p_root (from a trigger form) is compatible with h_root.
    Relying purely on parC's built-in H-alternation resolution, this checks that
    glottal root p_root differs from h_root only by an optional [H_ALT] tag.
    Returns:
    - p_root if p_root carries an active mutation tag ([H_DROP], [H_GLOT], [H_LAT])
    - clean_h if non-alternating ([H_NONE] or tagless)
    - None if incompatible
    """
    clean_h = strip_h_alt_tags(h_root)
    clean_p = strip_h_alt_tags(p_root)
    if clean_h != clean_p:
        return None
    if any(tag in p_root for tag in ("[H_DROP]", "[H_GLOT]", "[H_LAT]")):
        return p_root
    return clean_h




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

