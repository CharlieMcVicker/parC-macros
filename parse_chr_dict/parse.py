import os
import re
from pathlib import Path
from typing import Iterable

import pynini

from parC.grammar.acceptor_compilation import fsm_strings
from parC.grammar.paradigm_compilation import (
    fsa,
    get_open_parse_graph,
    inflect,
    word_fsa,
)
from parse_chr_dict.acceptors import get_cascade_domain_acceptor

PARSE_GRAPH = None
INFLECT_GRAPH = None


def is_inplace_grammar() -> bool:
    """Detects whether the active grammar uses in-place morpheme tags."""
    yaml_dir = os.environ.get("YAML_DIR", "")
    if "inplace" in yaml_dir:
        return True
    try:
        from parC.constants import get_yaml_dir

        yd = Path(get_yaml_dir())
        if "inplace" in yd.name or "inplace" in str(yd):
            return True
        paradigm_path = yd / "Morphotactics" / "Paradigm" / "verb.yaml"
        if paradigm_path.exists():
            content = paradigm_path.read_text(encoding="utf-8")
            if "<PrefixClass>" in content:
                return True
    except Exception:
        pass
    return False


def get_parse_graph():
    raw_parse = get_open_parse_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=True
    )
    if is_inplace_grammar():
        syms = raw_parse.output_symbols()
        domain_acceptor = get_cascade_domain_acceptor(syms=syms)
        return pynini.compose(raw_parse, domain_acceptor).optimize()
    return raw_parse


def parse(surface: str, labels: list[tuple[str, str]] = None) -> list[str]:
    global PARSE_GRAPH
    if PARSE_GRAPH is None:
        PARSE_GRAPH = get_parse_graph()

    # Let's parse the surface form cant-o_a
    if labels is None:
        labels = []
    surface_fsa = word_fsa(surface)
    for feat, value in sorted(labels, key=lambda l: l[0]):
        surface_fsa = pynini.concat(surface_fsa, fsa(feature_tag(feat, value)))

    output_lattice_with_tag = pynini.compose(surface_fsa, PARSE_GRAPH).optimize()
    output_lattice_with_tag = pynini.project(
        output_lattice_with_tag, project_type="output"
    )
    output_lattice_with_tag = pynini.rmepsilon(output_lattice_with_tag).optimize()
    if output_lattice_with_tag.properties(pynini.CYCLIC, True) == pynini.CYCLIC:
        output_lattice_with_tag = pynini.shortestpath(output_lattice_with_tag, nshortest=5000).optimize()
    return fsm_strings(output_lattice_with_tag, strip_all_tags=False)




def get_inflect_graph():
    return get_open_inflect_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=False
    )


def feature_tag(feature, value):
    return f"[{feature}={value}]"


from dataclasses import dataclass, field

INPLACE_SLOT_TAG_MAP: dict[str, str] = {
    "PrefixClass": "prefix_class",
    "Pro": "pronominal",
    "H_alt": "h_alt_tag",
    "H_ALT": "h_alt_tag",
    "AspectClass": "aspect_class",
    "Aspect": "aspect",
    "TenseClass": "tense_present_class",
    "Tense": "tense",
}

_READ_LABELS_CACHE: dict[str, tuple[str, dict[str, str]]] = {}


@dataclass
class InPlaceParseConfig:
    """Structured configuration object representing in-place morpheme slots and root."""
    root: str
    prefix_class: str = ""
    pronominal: str = ""
    aspect_class: str = ""
    aspect: str = ""
    tense_present_class: str = ""
    tense: str = ""
    prepronominal_prefixes: list[str] = field(default_factory=list)
    h_alt_tag: str = ""
    rules: str = "+"
    raw_tokens: list[str] = field(default_factory=list)

    @property
    def canonical_root(self) -> str:
        """Returns the root wrapped in legacy marker format for backwards compatibility."""
        h_part = (
            self.h_alt_tag
            if self.h_alt_tag and self.h_alt_tag not in self.root
            else ""
        )
        clean_root = (
            self.root.replace("[DIST=de]", "[DIST]").replace("[DIST=di]", "[DIST]")
        )
        return f"[Pro]{h_part}{clean_root}[Aspect][Tense]"

    def to_labels_dict(self) -> dict[str, str]:
        d = {
            "prefix_class": self.prefix_class,
            "pronominal": self.pronominal,
            "aspect_class": self.aspect_class,
            "aspect": self.aspect,
            "tense_present_class": self.tense_present_class,
            "tense": self.tense,
            "rules": self.rules,
        }
        if "[WI]" in self.prepronominal_prefixes:
            d["translocutive"] = "+"
        if "[DIST]" in self.prepronominal_prefixes or any(
            p.startswith("[DIST") for p in self.prepronominal_prefixes
        ):
            d["distributive"] = "+"
        if self.h_alt_tag:
            d["h_alt_tag"] = self.h_alt_tag
        return {k: v for k, v in d.items() if v}


def read_inplace_parse(s: str) -> InPlaceParseConfig:
    """
    Parses an in-place morpheme parse string into an InPlaceParseConfig object.
    Uses bracket-depth tracking to safely handle nested brackets (e.g. [AspectClass=become[inf2]]).
    Slot tags ([PrefixClass=...], [Pro=...], [AspectClass=...], etc.) and PPP tags ([WI], [DIST])
    are extracted as metadata; any internal root mutation tags (like [H_NONE]) remain in the root.
    """
    if s.startswith("[BOW]"):
        s = s[5:]
    eow_idx = s.find("[EOW]")
    if eow_idx != -1:
        trailing = s[eow_idx + 5 :]
        s = s[:eow_idx]
    else:
        trailing = ""

    tokens = []
    root_chars = []
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
            tok = s[start:i]
            inner = tok[1:-1]
            eq_idx = inner.find("=")
            if eq_idx != -1 and inner[:eq_idx] in INPLACE_SLOT_TAG_MAP:
                tokens.append(tok)
            elif tok in ("[WI]", "[DIST]", "[DIST=de]", "[DIST=di]") or tok.startswith("[DIST="):
                tokens.append(tok)
            else:
                # Internal root tag (e.g. [H_NONE], [H_GLOT], [H_DROP]) or phonological tag
                tokens.append(tok)
                root_chars.append(tok)
        else:
            root_chars.append(s[i])
            i += 1

    cfg = InPlaceParseConfig(root="".join(root_chars), raw_tokens=tokens)
    for tok in tokens:
        inner = tok[1:-1]
        eq_idx = inner.find("=")
        if eq_idx != -1:
            k = inner[:eq_idx]
            v = inner[eq_idx + 1 :]
            if k == "PrefixClass":
                cfg.prefix_class = v
            elif k == "Pro":
                cfg.pronominal = v
            elif k == "AspectClass":
                cfg.aspect_class = v
            elif k == "Aspect":
                cfg.aspect = v
            elif k == "TenseClass":
                cfg.tense_present_class = v
            elif k == "Tense":
                cfg.tense = v
            elif k == "DIST":
                cfg.prepronominal_prefixes.append(tok)
            elif k in ("H_alt", "H_ALT"):
                cfg.h_alt_tag = tok
        else:
            if tok in ("[WI]", "[DIST]"):
                cfg.prepronominal_prefixes.append(tok)
            elif tok.startswith("[H_") or tok.startswith("[H_alt=") or tok.startswith("[TEMP"):
                cfg.h_alt_tag = tok

    if trailing and trailing.startswith("[") and trailing.endswith("]"):
        for chunk in trailing[1:-1].split("]["):
            eq = chunk.find("=")
            if eq != -1:
                k, v = chunk[:eq], chunk[eq + 1 :]
                if k == "rules":
                    cfg.rules = v

    return cfg


def read_labels(s: str):
    cached = _READ_LABELS_CACHE.get(s)
    if cached is not None:
        form, labels_dict = cached
        return form, dict(labels_dict)

    # s is a str like [BOW]foo[EOW][label=value][label2=value2]
    eow_idx = s.find("[EOW]")
    if eow_idx == -1 or not s.startswith("[BOW]"):
        _READ_LABELS_CACHE[s] = (s, {})
        return s, {}

    # Detect in-place morpheme tags
    form_candidate = s[5:eow_idx]
    if "[" in form_candidate and ("PrefixClass=" in form_candidate or "AspectClass=" in form_candidate or "Pro=" in form_candidate):
        cfg = read_inplace_parse(s)
        form = cfg.root
        labels_dict = cfg.to_labels_dict()
        _READ_LABELS_CACHE[s] = (form, labels_dict)
        return form, dict(labels_dict)

    # Legacy trailing-tag format
    form = form_candidate
    labels_str = s[eow_idx + 5 :]

    labels_dict = {}
    if labels_str and labels_str.startswith("[") and labels_str.endswith("]"):
        for chunk in labels_str[1:-1].split("]["):
            eq_idx = chunk.find("=")
            if eq_idx != -1:
                labels_dict[chunk[:eq_idx]] = chunk[eq_idx + 1 :]

    _READ_LABELS_CACHE[s] = (form, labels_dict)
    return form, dict(labels_dict)


def str_to_lexical_hashable(parse_str: str, lexical_features: set[str]):
    root, labels = read_labels(parse_str)
    label_tuple = tuple(
        sorted(
            [(k, v) for k, v in labels.items() if k in lexical_features],
            key=lambda x: x[0],
        )
    )
    return root, label_tuple


def parses_by_form(
    forms: Iterable[tuple[str, list[tuple[str, str]]]], lexical_features: set[str]
):
    for surface, constraints in forms:
        if not surface:
            continue
        strings = parse(surface, labels=constraints)
        lexicals = set(
            str_to_lexical_hashable(s, lexical_features=lexical_features)
            for s in strings
        )
        yield surface, lexicals


def get_roots_for_parses(lexicals: list[set[tuple[tuple[str, str], ...]]]):
    possible_lexical_roots: set = None
    for form_lexicals in lexicals:
        if possible_lexical_roots is None:
            possible_lexical_roots = form_lexicals
        else:
            possible_lexical_roots = possible_lexical_roots.intersection(form_lexicals)

    return possible_lexical_roots if possible_lexical_roots else set()

def get_just_root(s: str):
    # s is something like [PrefixClass=a_stem][Pro=3sg.A]tateka[AspectClass=a][Aspect=completive][TenseClass=a_present][Tense=immediate]
    # don't use a regexp, just read [ and ] and find the part that isn't in brackets, keeping in mind there are several bracketed parts at the beginning and end
    chars = []
    bracket_depth = 0

    for ch in s:
        if ch == "[":
            bracket_depth += 1
            continue
        if ch == "]":
            if bracket_depth > 0:
                bracket_depth -= 1
            continue
        if bracket_depth == 0:
            chars.append(ch)

    return "".join(chars)


def main():
    import readline

    root = "atat"
    lexical = [
        # ("aspect_class", "go"),
        # ("prefix_class", "a_stem"),
        ("tense_present_class", "a_present"),
    ]
    inflectional = [
        # ("pronominal", "3sg.A"),
        # ("aspect", "present"),
        ("tense", "present"),
        # ("translocutive", "+"),
        # ("distributive", "-"),
        # ("partitive", "+"),
    ]

    # words = inflect(
    #     "[BOW][Pro]atat[Aspect][Tense][EOW][aspect_class=go][prefix_class=a_stem][tense_present_class=a_present][aspect=present][pronominal=3sg.A][rules=+][tense=present]"
    # )
    # print(words)

    print("interactive parsing - newline to quit, . to flip modes")
    MODE = "PARSE"
    while True:
        surface = input(f"{MODE}: ").strip()
        if not surface:
            break

        # if MODE == "INFLECT":
        #     if surface == ".":
        #         MODE = "PARSE"
        #         continue
        #     forms = inflect(surface, [], [])
        #     for p in forms:
        #         print("\t", p)

        elif MODE == "PARSE":
            if surface == ".":
                MODE = "INFLECT"
                continue
            parses = parse(surface)
            groups = {}
            for p in parses:
                parsed_word, labels = p.split("[EOW]")
                parsed_word = parsed_word[5:] # cut off [BOW]
                root = get_just_root(parsed_word)
                if not root in groups:
                    groups[root] = []
                groups[root].append(parsed_word)
            root_list = sorted(groups.keys(), key=lambda x: len(x))
            for root in root_list[:10]:
                print("\t", root)
                for parsed_word in groups[root][:10]:
                    print("\t\t",parsed_word)
            print(len(parses), "parses found with", len(groups), "distinct roots")


if __name__ == "__main__":
    main()
