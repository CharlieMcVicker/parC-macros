import os

from parC.grammar.paradigm_compilation import (
    build_inflect_graph_for_root_regex,
    build_parse_graph,
    word_fsa,
    fsa,
)

from parC.grammar.acceptor_compilation import fsm_strings

import pynini


def parse_word(wildcard_parse_graph, surface):
    form_fsa = word_fsa(surface)
    parse_lattice = (form_fsa @ wildcard_parse_graph).optimize()
    output_projected = pynini.project(parse_lattice, "output").optimize()

    return output_projected


def construct_target_pattern(root, pronominal, prefix_class, aspect, aspect_class):
    # Construct the expected tag sequence
    target_pattern = (
        f"[BOW]{root}[EOW]"
        f"[prefix_class={prefix_class}]"
        f"[aspect_class={aspect_class}]"
        f"[aspect={aspect}]"
        f"[pronominal={pronominal}]"
    )
    return target_pattern


def assert_parse_matches_target(output_projected, target_pattern):
    target_fsa = fsa(target_pattern)
    assert pynini.equivalent(output_projected, target_fsa), (
        f"Parse output does not match expected target pattern.\n"
        f"Output: {output_projected}\n"
        f"Target: {target_fsa}"
    )


def wildcard_parse_graph():
    # check if the graph already exists on disk
    if os.path.exists("wildcard_parse_graph.fst"):
        parse_graph = pynini.Fst.read("wildcard_parse_graph.fst")
        return parse_graph
    # Build the inflection graph with open ended "<Phone>*" root and infer_lexical_features=True
    inflect_graph = build_inflect_graph_for_root_regex(
        "verb", "<Phone>*", infer_lexical_features=True
    )
    # Invert to build the parse graph
    parse_graph = build_parse_graph(inflect_graph)
    # save to disk
    parse_graph.write("wildcard_parse_graph.fst")

    return parse_graph


def main():
    # Example usage of the wildcard_parse_graph function
    parse_graph = wildcard_parse_graph()
    print("Wildcard parse graph constructed successfully.")

    for surface in ["atvneha", "uwatiyet"]:
        print(f"\nParsing surface form: {surface}")
        forms = parse_word(parse_graph, surface)

        strings = fsm_strings(forms, nshortest=1000)

        for i, string in enumerate(strings):
            print(i, string)

    all_forms = ["kawoniha", "tsiwoniha", "kawonisk", "uwonis", "uwonihist"]
    root_and_lexical_by_form = {}
    expected = "[BOW]woni[EOW][prefix_class=r_stem][aspect_class=ha-hi-s]"
    for surface in all_forms:
        forms = parse_word(parse_graph, surface)
        strings = fsm_strings(forms, nshortest=1000)
        lexicals = set(s.split("[aspect=")[0] for s in strings)
        root_and_lexical_by_form[surface] = lexicals
        # print(
        #     f"\nPossible roots and lexical features for {surface}: {root_and_lexical_by_form[surface]}"
        # )
        if expected not in lexicals:
            print(f"Expected parse {expected} not found for surface {surface}.")

    possible_lexical_roots = None
    for form in root_and_lexical_by_form.values():
        if possible_lexical_roots is None:
            possible_lexical_roots = form
        else:
            possible_lexical_roots = possible_lexical_roots.intersection(form)

    print(f"\nPossible lexical roots across all forms: {possible_lexical_roots}")


if __name__ == "__main__":
    main()
