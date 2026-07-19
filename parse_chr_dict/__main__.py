import csv
from dataclasses import dataclass
from tqdm import tqdm

from parse_chr_dict.create_aspect_class_csv import respell_consonants
from parse_chr_dict.parse import (
    get_roots_for_parses,
    parses_by_form,
)

LEXICAL_FEATURES = {
    "aspect_class",
    "prefix_class",
    "tense_present_class",
}


@dataclass
class FormParsing:
    """Spec for how to parse a form + a name"""

    corpus_key: str
    name: str
    lexical_features: list[tuple]


@dataclass
class EntryType:
    """A set of forms to parse from a row"""

    name: str
    """Name for the spec"""

    forms: list[str]
    """Names of FormParsings to use"""

    def get_forms_from_parses(self, form_parses):
        return [form_parses[name][1] for name in self.forms if name in form_parses]


def get_label(a: list[tuple[str, str]], key: str):
    return next((v for l, v in a if l == key), None)


def labels_match(
    a: list[tuple[str, str]],
    b: list[tuple[str, str]],
    key: str,
):
    a_val = get_label(a, key)
    b_val = get_label(b, key)
    if a_val == None or b_val == None:
        return False
    else:
        return a_val == b_val


def write_roots(row, entry_type, roots, writer):
    for r, label_values in roots:
        data = {**row}
        data["entry_type"] = entry_type.name
        data["root"] = r

        for k, v in label_values:
            data[k] = v

        writer.writerow(data)


def main():

    # 1. open csv
    # 2. for each row create form and constraint list
    # 3. output roots
    fieldnames = [
        "corpus_id",
        "entry_no",
        "definition",
        "present",
        "present_1sg",
        "imperfective",
        "perfective",
        "imperative",
        "infinitive",
    ]

    # parse the words a bunch of different ways
    # compare subsets of the parses
    # two kinds of dataclasses
    # 1. a parse to do
    # 2. a group of parses to compare together (tied to parses on name)

    forms_to_parse: list[FormParsing] = [
        FormParsing(
            corpus_key="present",
            name="3rd_present",
            lexical_features=[
                ("tense", "present"),
                ("aspect", "present"),
            ],
        ),
        FormParsing(
            corpus_key="present_1sg",
            name="1st_present",
            lexical_features=[
                ("tense", "present"),
                ("aspect", "present"),
            ],
        ),
        FormParsing(
            corpus_key="imperfective",
            name="3rd_incompletive_habitual",
            lexical_features=[
                ("tense", "habitual"),
                ("aspect", "incompletive"),
            ],
        ),
        FormParsing(
            corpus_key="perfective",
            name="3rd_completive_assertive",
            lexical_features=[
                ("tense", "assertive"),
                ("aspect", "completive"),
            ],
        ),
        FormParsing(
            corpus_key="perfective",
            name="3rd_incompletive_assertive",
            lexical_features=[
                ("tense", "assertive"),
                ("aspect", "incompletive"),
            ],
        ),
        FormParsing(
            corpus_key="imperative",
            name="2nd_imperative",
            lexical_features=[
                ("tense", "immediate"),
                ("aspect", "immediate"),
            ],
        ),
        FormParsing(
            corpus_key="imperative",
            name="2nd_future_prog",
            lexical_features=[
                ("tense", "future_prog"),
                ("aspect", "incompletive"),
            ],
        ),
        FormParsing(
            corpus_key="infinitive",
            name="3rd_infinitive",
            lexical_features=[
                ("tense", "infinitive"),
                ("aspect", "infinitive"),
            ],
        ),
    ]

    primary_entry_types = [
        EntryType(
            name="Eventful",
            forms=[
                "3rd_present",
                "1st_present",
                "3rd_incompletive_habitual",
                "3rd_completive_assertive",
                "2nd_imperative",
                "3rd_infinitive",
            ],
        ),
        EntryType(
            name="StativeFutProg",
            forms=[
                "3rd_present",
                "1st_present",
                "3rd_incompletive_habitual",
                "3rd_completive_assertive",
                "2nd_future_prog",
            ],
        ),
        EntryType(
            name="StativeNoImp",
            forms=[
                "3rd_present",
                "1st_present",
                "3rd_incompletive_habitual",
                "3rd_completive_assertive",
            ],
        ),
    ]

    shim_entry_types = [
        EntryType(
            name="EventfulInfinitive",
            forms=["3rd_infinitive"],
        ),
        EntryType(
            name="EventfulImperativeInfinitive",
            forms=["2nd_imperative", "3rd_infinitive"],
        ),
    ]

    with open("chr-corpus/corpus.csv") as f, open("errors.csv", "w+") as error_f, open(
        "roots.csv", "w+"
    ) as roots_f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        error_writer = csv.DictWriter(error_f, fieldnames=fieldnames)
        error_writer.writeheader()
        roots_writer = csv.DictWriter(
            roots_f,
            fieldnames=fieldnames + ["entry_type", "root"] + sorted(LEXICAL_FEATURES),
        )
        roots_writer.writeheader()

        def write_shims(roots, form_parses):
            roots_without_aspect = [
                (r, [(k, v) for k, v in labels if not k == "aspect_class"])
                for r, labels in roots
            ]
            for shim_type in shim_entry_types:
                shim_roots = get_roots_for_parses(
                    [
                        form_parses[name][1]
                        for name in shim_type.forms
                        if name in form_parses
                    ]
                )

                valid_shims = [
                    (shim_r, shim_labels)
                    for shim_r, shim_labels in shim_roots
                    if any(
                        shim_r == parent_r
                        and all(
                            (
                                labels_match(shim_labels, parent_labels, k)
                                for k in parent_labels
                            )
                        )
                        for parent_r, parent_labels in roots_without_aspect
                    )
                ]
                if len(valid_shims):
                    write_roots(row, entry_type, valid_shims, roots_writer)

        next(reader)
        rows = list(reader)
        # rows = rows[:10]
        for row in tqdm(rows):
            forms = {
                parsing.name: (
                    respell_consonants(row[parsing.corpus_key]),
                    parsing.lexical_features,
                )
                for parsing in forms_to_parse
            }
            if any(" " in f for f, _ in forms.values()):
                continue

            form_parses = {
                name: (parses)
                for name, parses in zip(
                    forms.keys(), parses_by_form(forms.values(), LEXICAL_FEATURES)
                )
            }

            row_written = False
            shims_generated = False

            for entry_type in primary_entry_types:
                roots = get_roots_for_parses(
                    entry_type.get_forms_from_parses(form_parses)
                )

                roots = sorted(roots, key=str)
                # print(roots)
                if len(roots):
                    row_written = True
                    if entry_type.name.startswith("Stative"):
                        roots = [
                            (root, labels)
                            for root, labels in roots
                            if get_label(labels, "aspect_class").startswith("stative")
                        ]
                        if not shims_generated:
                            shims_generated = True
                            write_shims(roots, form_parses)

                    write_roots(row, entry_type, roots, roots_writer)

            if not row_written:
                error_writer.writerow(row)


if __name__ == "__main__":
    main()
