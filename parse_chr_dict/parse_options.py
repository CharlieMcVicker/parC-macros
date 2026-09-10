"""
Structured parse variation and option extraction for Cherokee verb morphotactics.

Extracts root equivalence classes, factored prefix and suffix bundles, and individual slot
variation options directly from parse graph lattices without Cartesian flat string explosion.
"""

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sys
from typing import Any

# Ensure YAML_DIR defaults to chr-generated
if "YAML_DIR" not in os.environ:
    repo_root = Path(__file__).parent.parent.resolve()
    gen_dir = repo_root / "chr-generated"
    if gen_dir.exists():
        os.environ["YAML_DIR"] = str(gen_dir)

try:
    import readline  # noqa: F401
except ImportError:
    pass

import pynini
from parC.constants import set_yaml_dir
from parC.grammar.paradigm_compilation import word_fsa
from parse_chr_dict.acceptors import get_default_symbol_table
from parse_chr_dict.parse import get_parse_graph

from parse_chr_dict.slots import (
    _pascal_to_snake,
    get_prepronominal_tags,
    get_root_boundary_tag_prefixes,
    get_slot_manifest,
    get_slot_name_to_tag_map,
    get_slot_tag_map,
)

if "YAML_DIR" in os.environ:
    try:
        set_yaml_dir(os.environ["YAML_DIR"])
    except Exception:
        pass


def _get_manifest_partition(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Computes prefix tag names, suffix tag names, and root boundary markers from the slot manifest.
    """
    if manifest is None:
        manifest = get_slot_manifest()

    template = manifest.get("template", [])
    root_idx = template.index("<Root>") if "<Root>" in template else -1

    prefix_slots = set()
    suffix_slots = set()

    for idx, slot_elem in enumerate(template):
        slot_clean = slot_elem.strip("<>")
        if idx < root_idx:
            prefix_slots.add(slot_clean)
        elif idx > root_idx:
            suffix_slots.add(slot_clean)

    # In addition, check slots array role definitions
    for slot in manifest.get("slots", []):
        name = slot.get("name")
        role = slot.get("role")
        tags = slot.get("tags", [])
        if role == "prefix":
            for t in tags:
                prefix_slots.add(t)
        elif role == "suffix":
            for t in tags:
                suffix_slots.add(t)

    rb = manifest.get("root_boundaries", {})
    left_boundary = rb.get("left", "<H_alt>").strip("<>")
    right_boundary = rb.get("right", "<AspectClass>").strip("<>")

    tag_to_slot = manifest.get("tag_to_slot", {})
    slot_tag_map = get_slot_tag_map(manifest)

    return {
        "prefix_slots": prefix_slots,
        "suffix_slots": suffix_slots,
        "left_boundary": left_boundary,
        "right_boundary": right_boundary,
        "tag_to_slot": tag_to_slot,
        "slot_tag_map": slot_tag_map,
        "template": template,
    }


@dataclass(frozen=True)
class PrefixBundle:
    """Represents a unique combination of prefix features associated with a parse."""

    prepronominal_prefixes: tuple[str, ...] = ()
    prefix_class: str = ""
    pronominal: str = ""
    h_metathesis_tag: str = ""
    h_alt_tag: str = ""
    slot_values: tuple[tuple[str, str], ...] = ()

    @property
    def slots(self) -> dict[str, Any]:
        """Dictionary of all slot values in this bundle including standard and dynamic slots."""
        d: dict[str, Any] = {
            "prepronominal_prefixes": self.prepronominal_prefixes,
            "prefix_class": self.prefix_class,
            "pronominal": self.pronominal,
            "h_metathesis_tag": self.h_metathesis_tag,
            "h_alt_tag": self.h_alt_tag,
        }
        for k, v in self.slot_values:
            d[k] = v
        return d

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a slot value by tag name or field name."""
        if hasattr(self, key):
            return getattr(self, key)
        for k, v in self.slot_values:
            if k == key or _pascal_to_snake(k) == key:
                return v
        return default

    def to_tag_string(self) -> str:
        """Returns the linear tag string representation of this prefix bundle."""
        parts = list(self.prepronominal_prefixes)
        if self.prefix_class:
            parts.append(f"[PrefixClass={self.prefix_class}]")
        if self.pronominal:
            parts.append(f"[Pro={self.pronominal}]")
        if self.h_metathesis_tag:
            parts.append(self.h_metathesis_tag)
        if self.h_alt_tag:
            parts.append(self.h_alt_tag)
        for tag_name, val in self.slot_values:
            if tag_name not in ("PrefixClass", "Pro", "H_metathesis", "H_METATHESIS", "H_alt", "H_ALT"):
                if val:
                    parts.append(f"[{tag_name}={val}]" if not val.startswith("[") else val)
        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["slot_values"] = dict(self.slot_values)
        return d


@dataclass(frozen=True)
class SuffixBundle:
    """Represents a unique combination of suffix features associated with a parse."""

    aspect_class: str = ""
    variant: int = 1
    aspect: str = ""
    tense: str = ""
    slot_values: tuple[tuple[str, str], ...] = ()

    @property
    def slots(self) -> dict[str, Any]:
        """Dictionary of all slot values in this bundle including standard and dynamic slots."""
        d: dict[str, Any] = {
            "aspect_class": self.aspect_class,
            "variant": self.variant,
            "aspect": self.aspect,
            "tense": self.tense,
        }
        for k, v in self.slot_values:
            d[k] = v
        return d

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a slot value by tag name or field name."""
        if hasattr(self, key):
            return getattr(self, key)
        for k, v in self.slot_values:
            if k == key or _pascal_to_snake(k) == key:
                return v
        return default

    def to_tag_string(self) -> str:
        """Returns the linear tag string representation of this suffix bundle."""
        parts = []
        if self.aspect_class:
            parts.append(f"[AspectClass={self.aspect_class}]")
        if self.variant > 1:
            parts.append(f"[Variant={self.variant}]")
        if self.aspect:
            parts.append(f"[Aspect={self.aspect}]")
        if self.tense:
            parts.append(f"[Tense={self.tense}]")
        for tag_name, val in self.slot_values:
            if tag_name not in ("AspectClass", "Variant", "Aspect", "Tense"):
                if val:
                    parts.append(f"[{tag_name}={val}]" if not val.startswith("[") else val)
        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["slot_values"] = dict(self.slot_values)
        return d


@dataclass(frozen=True)
class RootParseOptions:
    """
    Structured parse variation options for a single root equivalence class.
    Contains both the full factored bundles (prefixes and suffixes) and the
    per-slot unique choice sets.
    """

    root: str
    prefix_bundles: tuple[PrefixBundle, ...]
    suffix_bundles: tuple[SuffixBundle, ...]
    prepronominal_options: tuple[tuple[str, ...], ...]
    prefix_class_options: tuple[str, ...]
    pronominal_options: tuple[str, ...]
    h_metathesis_options: tuple[str, ...]
    h_alt_options: tuple[str, ...]
    aspect_class_options: tuple[str, ...]
    variant_options: tuple[int, ...]
    aspect_options: tuple[str, ...]
    tense_options: tuple[str, ...]
    total_parses: int
    slot_options: dict[str, tuple[Any, ...]]

    @classmethod
    def create(
        cls,
        root: str,
        prefix_bundles: tuple[PrefixBundle, ...],
        suffix_bundles: tuple[SuffixBundle, ...],
        total_parses: int,
        prepronominal_options: tuple[tuple[str, ...], ...] = (),
        prefix_class_options: tuple[str, ...] = (),
        pronominal_options: tuple[str, ...] = (),
        h_metathesis_options: tuple[str, ...] = (),
        h_alt_options: tuple[str, ...] = (),
        aspect_class_options: tuple[str, ...] = (),
        variant_options: tuple[int, ...] = (),
        aspect_options: tuple[str, ...] = (),
        tense_options: tuple[str, ...] = (),
        slot_options: dict[str, tuple[Any, ...]] | None = None,
    ) -> "RootParseOptions":
        """Factory method to construct RootParseOptions with clean slot_options initialization."""
        if slot_options is None:
            slot_options = {
                "prepronominal": prepronominal_options,
                "prefix_class": prefix_class_options,
                "pronominal": pronominal_options,
                "h_metathesis": h_metathesis_options,
                "h_alt": h_alt_options,
                "aspect_class": aspect_class_options,
                "variant": variant_options,
                "aspect": aspect_options,
                "tense": tense_options,
            }
        return cls(
            root=root,
            prefix_bundles=prefix_bundles,
            suffix_bundles=suffix_bundles,
            prepronominal_options=prepronominal_options,
            prefix_class_options=prefix_class_options,
            pronominal_options=pronominal_options,
            h_metathesis_options=h_metathesis_options,
            h_alt_options=h_alt_options,
            aspect_class_options=aspect_class_options,
            variant_options=variant_options,
            aspect_options=aspect_options,
            tense_options=tense_options,
            total_parses=total_parses,
            slot_options=slot_options,
        )

    @property
    def is_fully_factorable(self) -> bool:
        """
        True if all prefix bundles combine orthogonally with all suffix bundles
        for this root (i.e. total_parses == len(prefix_bundles) * len(suffix_bundles)).
        """
        return self.total_parses == (len(self.prefix_bundles) * len(self.suffix_bundles))

    def format_summary(self, indent: str = "  ") -> str:
        """Formats a human-readable summary of this root's variation options."""
        lines = [f"{indent}Root: {self.root} ({self.total_parses} parse{'s' if self.total_parses != 1 else ''})"]
        ind = indent + "  "

        ppp_str = ", ".join(
            ("+" + "+".join(p)) if p else "[none]" for p in self.prepronominal_options
        ) or "[none]"
        pc_str = ", ".join(self.prefix_class_options) or "[none]"
        pro_str = ", ".join(self.pronominal_options) or "[none]"
        h_meta_str = ", ".join(self.h_metathesis_options) or "[none]"
        h_alt_str = ", ".join(self.h_alt_options) or "[none]"
        ac_str = ", ".join(self.aspect_class_options) or "[none]"
        var_str = ", ".join(str(v) for v in self.variant_options) or "1"
        asp_str = ", ".join(self.aspect_options) or "[none]"
        tns_str = ", ".join(self.tense_options) or "[none]"

        lines.append(f"{ind}Prefix variations ({len(self.prefix_bundles)} bundle{'s' if len(self.prefix_bundles) != 1 else ''}):")
        lines.append(f"{ind}  Prepronominal : {ppp_str}")
        lines.append(f"{ind}  PrefixClass   : {pc_str}")
        lines.append(f"{ind}  Pronominal    : {pro_str}")
        if any(h != "[none]" and h != "[H_metathesis=none]" for h in self.h_metathesis_options):
            lines.append(f"{ind}  H_metathesis  : {h_meta_str}")
        if any(h != "[none]" and h != "[H_alt=none]" for h in self.h_alt_options):
            lines.append(f"{ind}  H_alt         : {h_alt_str}")

        known_prefix_slots = {"prepronominal", "prefix_class", "pronominal", "h_metathesis", "h_alt"}
        for k, v in self.slot_options.items():
            if k not in known_prefix_slots and k not in {"aspect_class", "variant", "aspect", "tense"} and v:
                lines.append(f"{ind}  {k:<14}: {', '.join(str(x) for x in v)}")

        lines.append(f"{ind}Suffix variations ({len(self.suffix_bundles)} bundle{'s' if len(self.suffix_bundles) != 1 else ''}):")
        lines.append(f"{ind}  AspectClass   : {ac_str}")
        if any(v != 1 for v in self.variant_options):
            lines.append(f"{ind}  Variant       : {var_str}")
        lines.append(f"{ind}  Aspect        : {asp_str}")
        lines.append(f"{ind}  Tense         : {tns_str}")

        factor_status = (
            f"Orthogonal product ({len(self.prefix_bundles)} × {len(self.suffix_bundles)} = {self.total_parses})"
            if self.is_fully_factorable
            else f"Coupled subset ({len(self.prefix_bundles)} prefixes, {len(self.suffix_bundles)} suffixes -> {self.total_parses} valid parses)"
        )
        lines.append(f"{ind}Structure: {factor_status}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        slot_opts_dict: dict[str, Any] = {}
        for k, v in self.slot_options.items():
            if k == "prepronominal":
                slot_opts_dict[k] = [list(p) for p in v]
            else:
                slot_opts_dict[k] = list(v)

        return {
            "root": self.root,
            "total_parses": self.total_parses,
            "is_fully_factorable": self.is_fully_factorable,
            "prefix_bundles": [b.to_dict() for b in self.prefix_bundles],
            "suffix_bundles": [b.to_dict() for b in self.suffix_bundles],
            "slot_options": slot_opts_dict,
        }


@dataclass(frozen=True)
class WordParseOptions:
    """Structured parse variation result for an entire surface word."""

    surface: str
    roots: tuple[RootParseOptions, ...]
    total_parses: int

    @property
    def distinct_roots_count(self) -> int:
        return len(self.roots)

    def get_root(self, root_str: str) -> RootParseOptions | None:
        """Finds root options for a specific root string."""
        for r in self.roots:
            if r.root == root_str:
                return r
        return None

    def format_report(self, verbose: bool = False) -> str:
        """Formats a full structured report for this word."""
        lines = [
            "=" * 60,
            f"WORD: {self.surface}",
            f"SUMMARY: {self.total_parses} total parse{'s' if self.total_parses != 1 else ''} across {len(self.roots)} distinct root equivalence class{'es' if len(self.roots) != 1 else ''}.",
            "=" * 60,
        ]

        if not self.roots:
            lines.append("  (no valid parses found)")
            return "\n".join(lines)

        for root_opts in self.roots:
            lines.append("")
            lines.append(root_opts.format_summary(indent="  "))
            if verbose:
                lines.append("    Prefix Bundles:")
                for pb in root_opts.prefix_bundles:
                    lines.append(f"      - {pb.to_tag_string()}")
                lines.append("    Suffix Bundles:")
                for sb in root_opts.suffix_bundles:
                    lines.append(f"      - {sb.to_tag_string()}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface": self.surface,
            "total_parses": self.total_parses,
            "distinct_roots_count": len(self.roots),
            "roots": [r.to_dict() for r in self.roots],
        }


def extract_lattice_paths(fst: pynini.Fst) -> list[list[str]]:
    """
    Extracts all token paths from an acyclic FST lattice via DFS traversal.
    Returns a list of token lists preserving linear arc label ordering.
    """
    if fst.num_states() == 0:
        return []

    syms = fst.output_symbols() or get_default_symbol_table()
    paths: list[list[str]] = []

    def dfs(state: int, current_path: list[str]) -> None:
        if fst.final(state) != pynini.Weight.zero(fst.weight_type()):
            paths.append(list(current_path))
        for arc in fst.arcs(state):
            sym = syms.find(arc.olabel) if syms and arc.olabel != 0 else (chr(arc.olabel) if arc.olabel != 0 else "")
            if sym:
                current_path.append(sym)
            dfs(arc.nextstate, current_path)
            if sym:
                current_path.pop()

    dfs(fst.start(), [])
    return paths


def parse_token_sequence(
    tokens: list[str] | tuple[str, ...],
    manifest: dict[str, Any] | None = None,
) -> tuple[PrefixBundle, str, SuffixBundle]:
    """
    Decomposes a single linear parse token sequence into:
    (PrefixBundle, root_string, SuffixBundle) dynamically driven by the slot manifest.
    """
    partition = _get_manifest_partition(manifest)
    prefix_slots = partition["prefix_slots"]
    suffix_slots = partition["suffix_slots"]
    left_boundary = partition["left_boundary"]
    right_boundary = partition["right_boundary"]

    prepronominal: list[str] = []
    prefix_class = ""
    pronominal = ""
    h_metathesis_tag = ""
    h_alt_tag = ""
    root_chars: list[str] = []
    aspect_class = ""
    variant = 1
    aspect = ""
    tense = ""
    other_prefix_slots: dict[str, str] = {}
    other_suffix_slots: dict[str, str] = {}

    in_suffix = False
    in_prefix = True

    for tok in tokens:
        if tok in ("[BOW]", "[EOW]"):
            continue

        is_tag = tok.startswith("[") and tok.endswith("]")
        tag_key = ""
        tag_val = ""
        if is_tag and "=" in tok:
            inner = tok[1:-1]
            eq_idx = inner.find("=")
            tag_key = inner[:eq_idx]
            tag_val = inner[eq_idx + 1 :]

        # Suffix boundary check: right_boundary tag or any suffix slot tag
        if tag_key and (tag_key == right_boundary or tag_key in suffix_slots):
            in_suffix = True
            in_prefix = False

        if in_suffix:
            if tag_key == "AspectClass":
                aspect_class = tag_val
            elif tag_key == "Variant":
                variant = int(tag_val) if tag_val.isdigit() else 1
            elif tag_key == "Aspect":
                aspect = tag_val
            elif tag_key == "Tense":
                tense = tag_val
            elif tag_key:
                other_suffix_slots[tag_key] = tag_val
            elif is_tag:
                other_suffix_slots[tok] = ""
        elif in_prefix:
            if tag_key == "PrefixClass":
                prefix_class = tag_val
            elif tag_key == "Pro":
                pronominal = tag_val
            elif tag_key in ("H_metathesis", "H_METATHESIS"):
                h_metathesis_tag = tok
            elif tag_key in ("H_alt", "H_ALT"):
                h_alt_tag = tok
            elif tag_key and (tag_key in prefix_slots or tag_key == left_boundary):
                other_prefix_slots[tag_key] = tag_val
            elif tok.startswith("[TEMP"):
                h_alt_tag = tok
            elif not is_tag:
                # First non-tag character begins the root
                in_prefix = False
                root_chars.append(tok)
            elif h_alt_tag or (left_boundary and tag_key == left_boundary):
                # We reached/passed the left root boundary; non-prefix tag is an initial root tag (e.g. VoiceInfix)
                in_prefix = False
                root_chars.append(tok)
            else:
                # Tag before PrefixClass/Pro/H_alt (e.g. [WI], [DIST], [DIST=de], or dynamic prepronominal prefix)
                prepronominal.append(tok)
        else:
            root_chars.append(tok)

    prefix_b = PrefixBundle(
        prepronominal_prefixes=tuple(prepronominal),
        prefix_class=prefix_class,
        pronominal=pronominal,
        h_metathesis_tag=h_metathesis_tag,
        h_alt_tag=h_alt_tag,
        slot_values=tuple(sorted(other_prefix_slots.items())),
    )
    suffix_b = SuffixBundle(
        aspect_class=aspect_class,
        variant=variant,
        aspect=aspect,
        tense=tense,
        slot_values=tuple(sorted(other_suffix_slots.items())),
    )
    root = "".join(root_chars)
    return prefix_b, root, suffix_b


def extract_parse_options_from_lattice(
    surface: str,
    lattice: pynini.Fst,
    manifest: dict[str, Any] | None = None,
) -> WordParseOptions:
    """
    Inspects and factorizes an output lattice into structured WordParseOptions.
    """
    if lattice.num_states() == 0:
        return WordParseOptions(surface=surface, roots=(), total_parses=0)

    # Ensure acyclic or bounded paths
    lat = lattice
    if lat.properties(pynini.CYCLIC, True) == pynini.CYCLIC:
        lat = pynini.shortestpath(lat, nshortest=5000).optimize()

    paths = extract_lattice_paths(lat)
    if not paths:
        return WordParseOptions(surface=surface, roots=(), total_parses=0)

    # Group valid pairs by root
    root_groups: dict[str, list[tuple[PrefixBundle, SuffixBundle]]] = {}
    for path in paths:
        prefix_b, root, suffix_b = parse_token_sequence(path, manifest=manifest)
        if root not in root_groups:
            root_groups[root] = []
        root_groups[root].append((prefix_b, suffix_b))

    # Construct RootParseOptions for each root
    root_options_list: list[RootParseOptions] = []
    total_parses = len(paths)

    # Sort roots: shorter roots first, then alphabetically
    sorted_roots = sorted(root_groups.keys(), key=lambda r: (len(r), r))

    for root in sorted_roots:
        pairs = root_groups[root]
        # Preserve deterministic ordering for bundles
        seen_prefixes: dict[PrefixBundle, None] = {}
        seen_suffixes: dict[SuffixBundle, None] = {}
        for pb, sb in pairs:
            seen_prefixes[pb] = None
            seen_suffixes[sb] = None

        prefix_bundles = tuple(seen_prefixes.keys())
        suffix_bundles = tuple(seen_suffixes.keys())

        # Collect unique slot values
        ppp_opts = tuple(sorted({pb.prepronominal_prefixes for pb in prefix_bundles}))
        pc_opts = tuple(sorted({pb.prefix_class for pb in prefix_bundles if pb.prefix_class}))
        pro_opts = tuple(sorted({pb.pronominal for pb in prefix_bundles if pb.pronominal}))
        h_meta_opts = tuple(sorted({pb.h_metathesis_tag for pb in prefix_bundles if pb.h_metathesis_tag}))
        h_alt_opts = tuple(sorted({pb.h_alt_tag for pb in prefix_bundles if pb.h_alt_tag}))

        ac_opts = tuple(sorted({sb.aspect_class for sb in suffix_bundles if sb.aspect_class}))
        var_opts = tuple(sorted({sb.variant for sb in suffix_bundles}))
        asp_opts = tuple(sorted({sb.aspect for sb in suffix_bundles if sb.aspect}))
        tns_opts = tuple(sorted({sb.tense for sb in suffix_bundles if sb.tense}))

        # Dynamic slot_options dictionary
        slot_options_map: dict[str, tuple[Any, ...]] = {
            "prepronominal": ppp_opts,
            "prefix_class": pc_opts,
            "pronominal": pro_opts,
            "h_metathesis": h_meta_opts,
            "h_alt": h_alt_opts,
            "aspect_class": ac_opts,
            "variant": var_opts,
            "aspect": asp_opts,
            "tense": tns_opts,
        }

        # Collect any additional dynamic slots from bundles
        tag_map = get_slot_tag_map(manifest)
        extra_prefix_keys = {k for pb in prefix_bundles for k, _ in pb.slot_values}
        for k in extra_prefix_keys:
            slot_name = tag_map.get(k, k.lower())
            vals = tuple(sorted({v for pb in prefix_bundles for tag_k, v in pb.slot_values if tag_k == k and v}))
            slot_options_map[slot_name] = vals

        extra_suffix_keys = {k for sb in suffix_bundles for k, _ in sb.slot_values}
        for k in extra_suffix_keys:
            slot_name = tag_map.get(k, k.lower())
            vals = tuple(sorted({v for sb in suffix_bundles for tag_k, v in sb.slot_values if tag_k == k and v}))
            slot_options_map[slot_name] = vals

        root_options_list.append(
            RootParseOptions(
                root=root,
                prefix_bundles=prefix_bundles,
                suffix_bundles=suffix_bundles,
                prepronominal_options=ppp_opts,
                prefix_class_options=pc_opts,
                pronominal_options=pro_opts,
                h_metathesis_options=h_meta_opts,
                h_alt_options=h_alt_opts,
                aspect_class_options=ac_opts,
                variant_options=var_opts,
                aspect_options=asp_opts,
                tense_options=tns_opts,
                total_parses=len(pairs),
                slot_options=slot_options_map,
            )
        )

    return WordParseOptions(
        surface=surface,
        roots=tuple(root_options_list),
        total_parses=total_parses,
    )


def extract_parse_options(
    surface: str,
    fst: pynini.Fst | None = None,
    manifest: dict[str, Any] | None = None,
) -> WordParseOptions:
    """
    Extracts structured parse options for a surface word using the parse graph FST.
    """
    if fst is None:
        fst = get_parse_graph()

    try:
        surface_fsa = word_fsa(surface)
    except Exception:
        # If surface fails phonological tokenization in word_fsa, return empty result
        return WordParseOptions(surface=surface, roots=(), total_parses=0)

    output_lattice = pynini.compose(surface_fsa, fst).optimize()
    output_lattice = pynini.project(output_lattice, project_type="output")
    output_lattice = pynini.rmepsilon(output_lattice).optimize()

    return extract_parse_options_from_lattice(surface, output_lattice, manifest=manifest)


def process_word(
    surface: str,
    fst: pynini.Fst | None = None,
    verbose: bool = False,
    as_json: bool = False,
) -> WordParseOptions:
    """
    Processes and displays structured parse options for a given surface word.
    """
    options = extract_parse_options(surface, fst=fst)
    if as_json:
        print(json.dumps(options.to_dict(), indent=2))
    else:
        print(options.format_report(verbose=verbose))
    return options


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Structured parse variation and option extraction tool for Cherokee verbs."
    )
    parser.add_argument(
        "words",
        nargs="*",
        help="Surface form(s) to inspect. If omitted, runs in interactive mode.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed breakdown of all prefix and suffix bundles.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    args = parser.parse_args()

    fst = get_parse_graph()

    if args.words:
        clean_words = [w.strip() for w in args.words if w.strip()]
        if not clean_words:
            return

        if args.json:
            if len(clean_words) == 1:
                options = extract_parse_options(clean_words[0], fst=fst)
                print(json.dumps(options.to_dict(), indent=2))
            else:
                results = [
                    extract_parse_options(w, fst=fst).to_dict()
                    for w in clean_words
                ]
                print(json.dumps({"results": results}, indent=2))
            return

        for word in clean_words:
            process_word(word, fst=fst, verbose=args.verbose, as_json=False)
        return

    # Interactive REPL mode
    print("Interactive parse options inspection - empty line or Ctrl-C/D to quit.")
    while True:
        try:
            surface = input("PARSE OPTIONS: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not surface:
            break
        process_word(surface, fst=fst, verbose=args.verbose, as_json=args.json)


if __name__ == "__main__":
    main()
