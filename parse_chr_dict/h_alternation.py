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
    Returns:
    - h_root if p_root == h_root (non-alternating verb)
    - h_root with [H_DROP] embedded after [Pro] if h drops
    - h_root with [H_GLOT] embedded after [Pro] if h becomes glottal
    - h_root with [H_LAT] embedded after [Pro] if lh becomes tl
    - None if incompatible
    """
    import pynini
    from parse_chr_dict.h_alternation_fst import (
        build_drop_first_h_fst,
        build_first_h_to_glottal_fst,
        build_drop_h_in_deaffricated_lateral_fst,
        fst_grades_are_compatible,
    )

    clean_h = strip_h_alt_tags(h_root)
    clean_p = strip_h_alt_tags(p_root)
    if clean_h == clean_p:
        return h_root

    h_stem = re.sub(r"\[.*?\]", "", clean_h)
    p_stem = re.sub(r"\[.*?\]", "", clean_p)
    if h_stem == p_stem:
        return clean_h

    # 1. Check lateral deaffrication (lh -> tl)
    f_lat = build_drop_h_in_deaffricated_lateral_fst()
    lat_res = pynini.compose(pynini.accep(h_stem), f_lat)
    if lat_res.num_states() > 0:
        lat_outs = {item[1] for item in pynini.project(lat_res, "output").optimize().paths().items()}
        if p_stem in lat_outs and p_stem != h_stem:
            return clean_h.replace("[Pro]", "[Pro][H_LAT]", 1) if "[Pro]" in clean_h else f"[H_LAT]{clean_h}"

    # 2. Check first h to glottal (h -> ')
    f_glot = build_first_h_to_glottal_fst()
    glot_res = pynini.compose(pynini.accep(h_stem), f_glot)
    if glot_res.num_states() > 0:
        glot_outs = {item[1] for item in pynini.project(glot_res, "output").optimize().paths().items()}
        if p_stem in glot_outs and p_stem != h_stem:
            return clean_h.replace("[Pro]", "[Pro][H_GLOT]", 1) if "[Pro]" in clean_h else f"[H_GLOT]{clean_h}"

    # 3. Check drop first h (h -> "")
    f_drop = build_drop_first_h_fst()
    drop_res = pynini.compose(pynini.accep(h_stem), f_drop)
    if drop_res.num_states() > 0:
        drop_outs = {item[1] for item in pynini.project(drop_res, "output").optimize().paths().items()}
        if p_stem in drop_outs and p_stem != h_stem:
            return clean_h.replace("[Pro]", "[Pro][H_DROP]", 1) if "[Pro]" in clean_h else f"[H_DROP]{clean_h}"

    # 4. Check general FST compatibility (vowel restoration / syncopation)
    if fst_grades_are_compatible(h=h_stem, glottal=p_stem):
        if "h" in h_stem and "h" not in p_stem:
            return clean_h.replace("[Pro]", "[Pro][H_DROP]", 1) if "[Pro]" in clean_h else f"[H_DROP]{clean_h}"
        elif "'" in p_stem and "'" not in h_stem:
            return clean_h.replace("[Pro]", "[Pro][H_GLOT]", 1) if "[Pro]" in clean_h else f"[H_GLOT]{clean_h}"
        elif "tl" in p_stem and "lh" in h_stem:
            return clean_h.replace("[Pro]", "[Pro][H_LAT]", 1) if "[Pro]" in clean_h else f"[H_LAT]{clean_h}"
        return clean_h

    return None




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

