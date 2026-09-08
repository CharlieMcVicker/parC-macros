from __future__ import annotations
import re
from typing import Callable, List, Optional, Set

VOWEL_SET: Set[str] = set("aeiouv")

H_ALTERNATION_TRIGGER_PRONOMINALS: Set[str] = {
    "1sg>3sg",
    "2sg>3sg",
    "1sg.A",
}


VOWEL_H_ALT_TAGS: Set[str] = {
    "[H_alt=vowel_a]",
    "[H_alt=vowel_e]",
    "[H_alt=vowel_i]",
    "[H_alt=vowel_o]",
    "[H_alt=vowel_u]",
    "[H_alt=vowel_v]",
}

H_ALT_TAGS: Set[str] = {
    "[H_alt=drop]",
    "[H_alt=glot]",
    "[H_alt=lat]",
    "[H_alt=none]",
    "[H_alt=vowel]",
} | VOWEL_H_ALT_TAGS



def is_h_alternation_trigger(pronominal: str) -> bool:
    """Returns True if the pronominal triggers H-alternation (glottal grade)."""
    return pronominal in H_ALTERNATION_TRIGGER_PRONOMINALS


def validate_h_alternation_trigger(
    pronominal: str,
    h_alt_tag: Optional[str] | bool = None,
    has_h_alt: Optional[bool] = None,
) -> bool:
    """
    Validates that fine-grained mutation tags ([H_alt=drop], [H_alt=glot], [H_alt=lat], [H_alt=vowel])
    or has_h_alt flag co-occur strictly with H-alternating trigger prefixes (1sg>3sg, 2sg>3sg, 1sg.A).
    Returns False if mutation tag / has_h_alt is present but pronominal is not a trigger.
    """
    if has_h_alt is not None:
        has_mutation = has_h_alt
    elif isinstance(h_alt_tag, bool):
        has_mutation = h_alt_tag
    elif isinstance(h_alt_tag, str):
        is_none = h_alt_tag.lower() == "[h_alt=none]"
        has_mutation = not is_none and (h_alt_tag in H_ALT_TAGS)
    else:
        has_mutation = False

    if has_mutation and not is_h_alternation_trigger(pronominal):
        return False
    return True


def strip_h_alt_tags(root: str) -> str:
    """Strips fine-grained H-alternation tags from a root."""
    for tag in H_ALT_TAGS:
        root = root.replace(tag, "")
    return root


