from parC.grammar.paradigm_compilation import (
    get_open_parse_graph,
    get_open_inflect_graph,
    word_fsa,
    fsa,
)

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
    return fsm_strings(output_lattice_with_tag, strip_all_tags=False)


def get_inflect_graph():
    return get_open_inflect_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=False
    )


def inflect(
    root: str,
    lexical_features: list[tuple[str, str]],
    inflectional_features: list[tuple[str, str]],
) -> list[str]:
    global INFLECT_GRAPH
    if INFLECT_GRAPH is None:
        INFLECT_GRAPH = get_inflect_graph()

    surface_fsa = word_fsa(root)
    for feat, value in sorted(lexical_features, key=lambda l: l[0]):
        surface_fsa = pynini.concat(surface_fsa, fsa(feature_tag(feat, value)))

    for feat, value in sorted(inflectional_features, key=lambda l: l[0]):
        surface_fsa = pynini.concat(surface_fsa, fsa(feature_tag(feat, value)))

    output_lattice_with_tag = pynini.compose(surface_fsa, INFLECT_GRAPH).optimize()
    output_lattice_with_tag = pynini.project(
        output_lattice_with_tag, project_type="output"
    )
    return fsm_strings(output_lattice_with_tag, strip_all_tags=False)


def feature_tag(feature, value):
    return f"[{feature}={value}]"


def read_labels(s: str):
    # s is a str like [BOW]foo[EOW][label=value][label2=value2]
    # we will return [BOW]foo[EOW] and {label: value, label2: value2} as a dict
    match = re.match(r"\[BOW\](.*)\[EOW\](.*)", s)
    if not match:
        return s, {}

    form = match.group(1)
    labels_str = match.group(2)

    labels_dict = {}
    pos = 0
    while pos < len(labels_str):
        if labels_str[pos] != "[":
            pos += 1
            continue

        depth = 1
        i = pos + 1
        while i < len(labels_str) and depth > 0:
            if labels_str[i] == "[":
                depth += 1
            elif labels_str[i] == "]":
                depth -= 1
            i += 1

        if depth != 0:
            break

        label_content = labels_str[pos + 1 : i - 1]
        if "=" in label_content:
            key, value = label_content.split("=", 1)
            labels_dict[key] = value

        pos = i

    return form, labels_dict


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
    forms: list[tuple[str, list[tuple[str, str]]]], lexical_features: set[str]
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


def get_roots_for_forms(
    forms: list[tuple[str, list[tuple[str, str]]]], lexical_features: set[str]
):
    possible_lexical_roots = None
    for _surface, lexicals in parses_by_form(forms, lexical_features):
        if possible_lexical_roots is None:
            possible_lexical_roots = lexicals
        else:
            possible_lexical_roots = possible_lexical_roots.intersection(lexicals)

    return possible_lexical_roots if possible_lexical_roots else set()


def main():
    import readline

    root = "atat"
    lexical = [
        # ("aspect_class", "go"),
        ("prefix_class", "a_stem"),
        ("tense_present_class", "a_present"),
    ]
    inflectional = [
        ("pronominal", "3sg.A"),
        # ("aspect", "present"),
        ("tense", "present"),
        # ("translocutive", "+"),
        # ("distributive", "-"),
        # ("partitive", "+"),
    ]

    words = inflect(root, lexical, inflectional)
    print(words)

    print("interactive parsing - newline to quit, . to flip modes")
    MODE = "PARSE"
    while True:
        surface = input(f"{MODE}: ").strip()
        if not surface:
            break

        if MODE == "INFLECT":
            if surface == ".":
                MODE = "PARSE"
                continue
            forms = inflect(surface, [], [])
            for p in forms:
                print("\t", p)

        elif MODE == "PARSE":
            if surface == ".":
                MODE = "INFLECT"
                continue
            parses = parse(surface)
            for p in parses:
                print("\t", p)


if __name__ == "__main__":
    main()
