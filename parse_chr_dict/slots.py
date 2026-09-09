"""
Slot manifest loader and dynamic slot/tag mapping utilities.
Reads slot structure and root boundary metadata from compiled slots.json.
"""

import copy
import functools
import json
import os
import re
from pathlib import Path
from typing import Any

FALLBACK_MANIFEST: dict[str, Any] = {
    "slots": [
        {
            "name": "pronominal",
            "role": "prefix",
            "rule": "pro_replace",
            "tags": ["PrefixClass", "Pro"],
        },
        {
            "name": "aspect",
            "role": "suffix",
            "rule": "aspect_replace",
            "tags": ["AspectClass", "Variant", "Aspect"],
        },
        {
            "name": "tense",
            "role": "suffix",
            "rule": "tense_replace",
            "tags": ["Tense"],
        },
    ],
    "template": [
        "<PrepronominalPrefixes>",
        "<PrefixClass>",
        "<Pro>",
        "<H_metathesis>",
        "<H_alt>",
        "<Root>",
        "<AspectClass>",
        "<Variant>",
        "<Aspect>",
        "<Tense>",
    ],
    "tag_to_slot": {
        "PrefixClass": "pronominal",
        "Pro": "pronominal",
        "AspectClass": "aspect",
        "Variant": "aspect",
        "Aspect": "aspect",
        "Tense": "tense",
    },
    "root_boundaries": {
        "left": "<H_alt>",
        "right": "<AspectClass>",
    },
}

DEFAULT_SLOT_TAG_MAP: dict[str, str] = {
    "PrefixClass": "prefix_class",
    "Pro": "pronominal",
    "H_metathesis": "h_metathesis_tag",
    "H_METATHESIS": "h_metathesis_tag",
    "H_alt": "h_alt_tag",
    "H_ALT": "h_alt_tag",
    "AspectClass": "aspect_class",
    "Variant": "variant",
    "Aspect": "aspect",
    "Tense": "tense",
}

SPECIAL_TAG_MAP: dict[str, str] = {
    "Pro": "pronominal",
    "H_metathesis": "h_metathesis_tag",
    "H_METATHESIS": "h_metathesis_tag",
    "H_alt": "h_alt_tag",
    "H_ALT": "h_alt_tag",
}


def _pascal_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _resolve_manifest_path(manifest_path: str | Path | None = None) -> Path:
    if manifest_path is not None:
        return Path(manifest_path)
    yaml_dir = os.environ.get("YAML_DIR")
    if yaml_dir:
        return Path(yaml_dir) / "slots.json"
    repo_root = Path(__file__).parent.parent.resolve()
    return repo_root / "chr-generated" / "slots.json"


@functools.lru_cache(maxsize=32)
def _load_slot_manifest(path_str: str) -> dict[str, Any]:
    p = Path(path_str)
    if not p.exists() or not p.is_file():
        return copy.deepcopy(FALLBACK_MANIFEST)
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return copy.deepcopy(FALLBACK_MANIFEST)


def get_slot_manifest(manifest_path: str | Path | None = None) -> dict[str, Any]:
    """
    Loads slots.json from YAML_DIR or chr-generated/slots.json (or specified manifest_path).
    Memoized using an internal LRU cache. If the manifest file does not exist, returns fallback dict.
    """
    p = _resolve_manifest_path(manifest_path)
    return copy.deepcopy(_load_slot_manifest(str(p.resolve())))


get_slot_manifest.cache_clear = _load_slot_manifest.cache_clear  # type: ignore[attr-defined]


def get_root_boundary_tag_prefixes(manifest: dict[str, Any] | None = None) -> tuple[str, str]:
    """
    Reads manifest["root_boundaries"] ('left' and 'right').
    Strips '<' and '>' and returns tuple (f"[{left}=", f"[{right}="),
    e.g. ("[H_alt=", "[AspectClass=").
    """
    if manifest is None:
        manifest = get_slot_manifest()

    rb = manifest.get("root_boundaries", {})
    left_raw = rb.get("left") or "<H_alt>"
    right_raw = rb.get("right") or "<AspectClass>"

    left = str(left_raw).strip("<>")
    right = str(right_raw).strip("<>")

    return f"[{left}=", f"[{right}="


def get_slot_tag_map(manifest: dict[str, Any] | None = None) -> dict[str, str]:
    """
    Returns mapping from tag name (e.g. 'PrefixClass', 'Pro') to internal field name
    (e.g. 'prefix_class', 'pronominal') derived from slot tags with case conversion
    and fallback defaults.
    """
    if manifest is None:
        manifest = get_slot_manifest()

    tag_map = dict(DEFAULT_SLOT_TAG_MAP)
    for slot in manifest.get("slots", []):
        for tag in slot.get("tags", []):
            if tag in SPECIAL_TAG_MAP:
                tag_map[tag] = SPECIAL_TAG_MAP[tag]
            elif tag.lower() == "pro":
                tag_map[tag] = "pronominal"
            else:
                tag_map[tag] = _pascal_to_snake(tag)

    return tag_map


def get_slot_name_to_tag_map(manifest: dict[str, Any] | None = None) -> dict[str, str]:
    """
    Returns reverse mapping from internal field name to tag name
    (e.g. 'prefix_class' -> 'PrefixClass').
    """
    tag_map = get_slot_tag_map(manifest)
    res: dict[str, str] = {}
    for k, v in tag_map.items():
        if v not in res or k != "H_ALT":
            res[v] = k
    return res
