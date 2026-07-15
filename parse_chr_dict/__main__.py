import csv
import os
import re

from parC.grammar.paradigm_compilation import get_open_parse_graph, word_fsa, fsa

from parC.grammar.acceptor_compilation import fsm_strings

import pynini
from tqdm import tqdm

from parse_chr_dict.create_aspect_class_csv import respell_consonants

PARSE_GRAPH = None


def get_parse_graph():
    return get_open_parse_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=True
    )


def parse(surface: str, labels: list[tuple[str, str]] = None):
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


def feature_tag(feature, value):
    return f"[{feature}={value}]"


def parses_by_form(forms: list[tuple[str, list[tuple[str, str]]]]):
    for surface, constraints in forms:
        if not surface:
            continue
        strings = parse(surface, labels=constraints)
        lexicals = set(s.split("[aspect=")[0] for s in strings)
        yield surface, lexicals


def get_roots_for_forms(forms: list[tuple[str, list[tuple[str, str]]]]):
    possible_lexical_roots = None
    for _surface, lexicals in parses_by_form(forms):
        if possible_lexical_roots is None:
            possible_lexical_roots = lexicals
        else:
            possible_lexical_roots = possible_lexical_roots.intersection(lexicals)

    return possible_lexical_roots if possible_lexical_roots else set()


def main():

    # 1. open csv
    # 2. for each row create form and constraint list
    # 3. output roots
    fieldnames = [
        "corpus_id",
        "entry_no",
        "definition",
        "prediction",
        "present",
        "present_1sg",
        "imperfective",
        "perfective",
        "imperative",
        "infinitive",
    ]

    eventful_form_map = {
        "present": [
            ("tense", "present"),
            ("aspect", "present"),
            # ("pronominal", r"3[^\]]*"),
        ],
        "present_1sg": [
            ("tense", "present"),
            ("aspect", "present"),
            # ("pronominal", r"1[^\]]*"),
        ],
        "imperfective": [
            ("tense", "habitual"),
            ("aspect", "incompletive"),
            # ("pronominal", r"3[^\]]*"),
        ],
        "perfective": [
            ("tense", "assertive"),
            ("aspect", "completive"),
            # ("pronominal", r"3[^\]]*"),
        ],
        "imperative": [
            ("tense", "immediate"),
            ("aspect", "immediate"),
            # ("pronominal", r"3[^\]]*"),
        ],
        "infinitive": [
            ("tense", "infinitive"),
            ("aspect", "infinitive"),
            # ("pronominal", r"3[^\]]*"),
        ],
    }

    with open("chr-corpus/corpus.csv") as f, open("errors.csv", "w+") as error_f, open(
        "roots.csv", "w+"
    ) as roots_f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        error_writer = csv.DictWriter(error_f, fieldnames=fieldnames)
        error_writer.writeheader()
        roots_writer = csv.DictWriter(roots_f, fieldnames=fieldnames + ["lexical"])
        roots_writer.writeheader()
        next(reader)
        rows = list(reader)
        for row in tqdm(rows):
            # print()
            # input(row["definition"])
            forms = [
                (respell_consonants(row[fname]), constraints)
                for fname, constraints in eventful_form_map.items()
            ]
            if any(" " in f for f, _ in forms):
                continue
            # print(forms)
            # for surface, lexicals in parses_by_form(forms):
            #     print(surface)
            #     for l in lexicals:
            #         print("\t" + l)
            roots = get_roots_for_forms(forms)
            # print(roots)
            if len(roots):
                for r in roots:
                    data = {**row}
                    data["lexical"] = r
                    roots_writer.writerow(data)
            else:
                error_writer.writerow(row)


if __name__ == "__main__":
    main()
