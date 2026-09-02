from typing import Iterable

from parC.grammar.paradigm_compilation import (
    get_open_parse_graph,
    word_fsa,
    fsa,
)

from parC.grammar.paradigm_compilation import inflect

import re

from parC.grammar.acceptor_compilation import fsm_strings

import pynini

PARSE_GRAPH = None
INFLECT_GRAPH = None


def get_parse_graph():
    return get_open_parse_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=True
    )


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


INPLACE_SLOT_TAG_MAP: dict[str, str] = {
    "PrefixClass": "prefix_class",
    "Pro": "pronominal",
    "AspectClass": "aspect_class",
    "Aspect": "aspect",
    "TenseClass": "tense_present_class",
    "Tense": "tense",
}

_INPLACE_TAG_RE = re.compile(r"\[([A-Za-z0-9_]+)=([^\]]+)\]")
_READ_LABELS_CACHE: dict[str, tuple[str, dict[str, str]]] = {}


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

    form = s[5:eow_idx]
    labels_str = s[eow_idx + 5 :]

    labels_dict = {}
    if labels_str and labels_str.startswith("[") and labels_str.endswith("]"):
        for chunk in labels_str[1:-1].split("]["):
            eq_idx = chunk.find("=")
            if eq_idx != -1:
                labels_dict[chunk[:eq_idx]] = chunk[eq_idx + 1 :]

    # Extract in-place slot tags from form (e.g. [PrefixClass=...], [Pro=...], [AspectClass=...], etc.)
    if "[" in form and "=" in form:
        def _extract_tag(m: re.Match) -> str:
            k, v = m.group(1), m.group(2)
            mapped_k = INPLACE_SLOT_TAG_MAP.get(k, k)
            labels_dict[mapped_k] = v
            return ""

        form = _INPLACE_TAG_RE.sub(_extract_tag, form)

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
                head, tail = p.split("[EOW]")
                head = head[5:] # cut off [BOW]
                if not head in groups:
                    groups[head] = []
                groups[head].append(tail)
            for head in groups:
                print("\t", head)
                for tail in groups[head]:
                    print("\t\t",tail)


if __name__ == "__main__":
    main()
