import csv
import os
from pathlib import Path
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
from parse_chr_dict.meta_label_compiler import derive_hypotheses_for_forms
from parse_chr_dict.reconstruct import validate_hypothesis
from parse_chr_dict.types import PRIMARY_VERB_ENTRY_TYPES


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
    "h_alt_tag",
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

            # Run derivation & validation per VerbEntryType in priority order
            for entry_type in PRIMARY_VERB_ENTRY_TYPES:
                # Gather forms specific to this entry type
                entry_forms = [
                    (respell_consonants(row[form.corpus_key]), form)
                    for form in entry_type.forms
                    if row.get(form.corpus_key)
                    and " " not in row[form.corpus_key]
                ]
                if not entry_forms:
                    continue

                derived_hypotheses = derive_hypotheses_for_forms(
                    entry_forms, entry_type=entry_type
                )
                if not derived_hypotheses:
                    continue

                if entry_type.name.startswith("Stative"):
                    derived_hypotheses = {
                        h for h in derived_hypotheses if h.aspect_class.startswith("stative")
                    }

                # Validate each candidate hypothesis against full row reconstruction
                valid_hypotheses = [
                    h for h in derived_hypotheses
                    if validate_hypothesis(h, row, entry_type)
                ]

                if valid_hypotheses:
                    row_written = True
                    for h in sorted(
                        valid_hypotheses,
                        key=lambda x: (
                            x.h_root,
                            x.h_alt_tag or "[H_alt=none]",
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

