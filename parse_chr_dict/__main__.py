import os

from parC.grammar.paradigm_compilation import (
    build_inflect_graph_for_root_regex,
    word_fsa,
)

from parC.grammar.acceptor_compilation import fsm_strings

import pynini

PARSE_GRAPH = None


def get_parse_graph():
    # Build using root regex AND infer_lexical_features=True
    inflect_graph = build_inflect_graph_for_root_regex(
        "verb", "<Phone>*", infer_lexical_features=True
    )
    assert isinstance(inflect_graph, pynini.Fst)

    # Invert to build a parse graph
    return pynini.invert(inflect_graph).optimize()


def parse(surface: str):
    global PARSE_GRAPH
    if PARSE_GRAPH is None:
        PARSE_GRAPH = get_parse_graph()

    # Let's parse the surface form cant-o_a
    surface_fsa = word_fsa(surface)
    parse_lattice = pynini.compose(surface_fsa, PARSE_GRAPH).optimize()
    return fsm_strings(parse_lattice)


def main():

    for surface in ["atvneha", "uwatiyet"]:
        print(f"\nParsing surface form: {surface}")
        strings = parse(surface)

        for i, string in enumerate(strings):
            print(i, string)

    all_forms = [
        "kawonih",
        "tsiwonih",
        "kawonisk",
        "uwonis",
        "uwonihist",
    ]
    root_and_lexical_by_form = {}
    expected = "[BOW]won[EOW][prefix_class=r_stem][aspect_class=ih-ihi]"
    for surface in all_forms:
        strings = parse(surface)
        lexicals = set(s.split("[aspect=")[0] for s in strings)
        root_and_lexical_by_form[surface] = lexicals
        # print(
        #     f"\nPossible roots and lexical features for {surface}: {root_and_lexical_by_form[surface]}"
        # )
        if expected not in lexicals:
            print(f"Expected parse {expected} not found for surface {surface}.")
            print(lexicals)

    possible_lexical_roots = None
    for form in root_and_lexical_by_form.values():
        if possible_lexical_roots is None:
            possible_lexical_roots = form
        else:
            possible_lexical_roots = possible_lexical_roots.intersection(form)

    print(f"\nPossible lexical roots across all forms: {possible_lexical_roots}")


if __name__ == "__main__":
    main()
