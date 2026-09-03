import csv
import os
from pathlib import Path
from dataclasses import asdict
from tqdm import tqdm

if "YAML_DIR" not in os.environ:
    repo_root = Path(__file__).parent.parent.resolve()
    inplace_dir = repo_root / "chr-inplace-generated"
    if inplace_dir.exists():
        os.environ["YAML_DIR"] = str(inplace_dir)
        try:
            from parC.constants import set_yaml_dir
            set_yaml_dir(str(inplace_dir))
        except ImportError:
            pass

from parse_chr_dict.create_aspect_class_csv import respell_consonants
from parse_chr_dict.meta_label_compiler import (
    FORMS_TO_PARSE,
    PRIMARY_ENTRY_TYPES,
    SHIM_ENTRY_TYPES,
    MetaConstraintCompiler,
    derive_hypotheses_for_forms,
    DerivationHypothesis,
)
from parse_chr_dict.parse import (
    get_roots_for_parses,
    parses_by_form,
)
from parse_chr_dict.reconstruct import (
    ReconstructionSpec,
    reconstruct_row,
    validate_hypothesis,
)

LEXICAL_FEATURES = {
    "aspect_class",
    "prefix_class",
    "tense_present_class",
}

ENTRY_TYPE_FORMS = {
    entry_type.name: [parsing for parsing in FORMS_TO_PARSE if parsing.name in entry_type.forms]
    for entry_type in PRIMARY_ENTRY_TYPES
}


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


def write_roots(row, entry_type, roots, writer, compiler=None):
    for entry, label_values in sorted(roots, key=str):
        data = {**row}
        data["entry_type"] = entry_type.name
        if isinstance(entry, tuple):
            data["h_root"] = entry[0]
            data["glottal_root"] = entry[1] or ""
        else:
            data["h_root"] = entry
            data["glottal_root"] = ""

        for k, v in label_values:
            data[k] = v

        specs = reconstruct_row(data, entry_type, LEXICAL_FEATURES, compiler=compiler)
        for spec in specs:
            row_data = {**data, **asdict(spec)}
            writer.writerow(row_data)


def write_shims(row, roots, form_parses, roots_writer):
    roots_without_aspect = [
        (r, [(k, v) for k, v in labels if not k == "aspect_class"])
        for r, labels in roots
    ]
    for shim_type in SHIM_ENTRY_TYPES:
        shim_roots = get_roots_for_parses(
            [form_parses[name][1] for name in shim_type.forms if name in form_parses]
        )

        valid_shims = [
            (shim_r, shim_labels)
            for shim_r, shim_labels in shim_roots
            if any(
                shim_r == parent_r
                and all(
                    (
                        labels_match(shim_labels, parent_labels, k)
                        for k, _ in parent_labels
                    )
                )
                for parent_r, parent_labels in roots_without_aspect
            )
        ]
        if len(valid_shims):
            write_roots(row, shim_type, valid_shims, roots_writer)


ROOTS_FIELDNAMES = [
    "corpus_id",
    "entry_no",
    "definition",
    "present",
    "present_1sg",
    "imperfective",
    "perfective",
    "imperative",
    "infinitive",
    "entry_type",
    "h_root",
    "glottal_root",
    "aspect_class",
    "prefix_class",
    "tense_present_class",
    "set_a",
    "plural",
    "animate_objects",
    "variant_present",
    "variant_incompletive",
    "variant_completive",
    "variant_immediate",
    "variant_infinitive",
]


def main():
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

    compiler = MetaConstraintCompiler()

    with open("chr-corpus/corpus.csv") as f, open("errors.csv", "w+") as error_f, open(
        "roots.csv", "w+"
    ) as roots_f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        error_writer = csv.DictWriter(error_f, fieldnames=fieldnames)
        error_writer.writeheader()
        roots_writer = csv.DictWriter(
            roots_f,
            fieldnames=ROOTS_FIELDNAMES,
        )
        roots_writer.writeheader()

        next(reader)
        rows = list(reader)
        for row in tqdm(rows):
            row_written = False

            # Run derivation & validation per EntryTypeSpec in priority order
            for entry_type in PRIMARY_ENTRY_TYPES:
                # Gather forms specific to this entry type
                entry_forms = [
                    (respell_consonants(row[parsing.corpus_key]), parsing)
                    for parsing in ENTRY_TYPE_FORMS[entry_type.name]
                    if row.get(parsing.corpus_key)
                    and " " not in row[parsing.corpus_key]
                ]
                if not entry_forms:
                    continue

                derived_hypotheses = derive_hypotheses_for_forms(entry_forms, compiler)
                if not derived_hypotheses:
                    continue

                if entry_type.name.startswith("Stative"):
                    derived_hypotheses = {
                        h for h in derived_hypotheses if h.aspect_class.startswith("stative")
                    }

                # Validate each candidate hypothesis against full row reconstruction
                valid_hypotheses = [
                    h for h in derived_hypotheses
                    if validate_hypothesis(h, row, entry_type, compiler=compiler)
                ]

                if valid_hypotheses:
                    row_written = True
                    for h in sorted(
                        valid_hypotheses,
                        key=lambda x: (
                            x.h_root,
                            x.glottal_root or "",
                            x.aspect_class,
                            x.prefix_class,
                            x.tense_present_class,
                            x.set_a,
                            x.plural,
                            x.animate_objects,
                            x.metadata.aspect_variants.present,
                            x.metadata.aspect_variants.incompletive,
                            x.metadata.aspect_variants.completive,
                            x.metadata.aspect_variants.immediate,
                            x.metadata.aspect_variants.infinitive,
                        ),
                    ):
                        row_data = h.to_row_dict(row, entry_type=entry_type.name)
                        roots_writer.writerow(row_data)
                    break

            if not row_written:
                error_writer.writerow(row)


if __name__ == "__main__":
    main()

