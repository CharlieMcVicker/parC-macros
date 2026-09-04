import csv
from collections import Counter
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from parse_chr_dict.create_aspect_class_csv import respell_consonants
from parse_chr_dict.meta_label_compiler import derive_hypotheses_for_forms
from parse_chr_dict.types import (
    VerbForm,
    PRIMARY_VERB_ENTRY_TYPES,
    VERB_FORMS_BY_NAME,
    LexicalVerb,
    DerivationHypothesis,
)


def validate_form_subset(
    hypothesis: DerivationHypothesis | LexicalVerb,
    forms: List[tuple[str, VerbForm | Any]],
    compiler: Optional[Any] = None,
) -> bool:
    for surf, form_item in forms:
        if isinstance(form_item, VerbForm):
            form = form_item
        elif hasattr(form_item, "to_verb_form"):
            form = form_item.to_verb_form()
        else:
            form = VERB_FORMS_BY_NAME.get(getattr(form_item, "name", str(form_item)))
        if form:
            if not hypothesis.validate_form(form, surf):
                return False
    return True


def generate_for_slot(
    hypothesis: DerivationHypothesis | LexicalVerb,
    parsing_meta: VerbForm | Any,
    compiler: Optional[Any] = None,
) -> List[str]:
    if isinstance(parsing_meta, VerbForm):
        form = parsing_meta
    elif hasattr(parsing_meta, "to_verb_form"):
        form = parsing_meta.to_verb_form()
    else:
        form = VERB_FORMS_BY_NAME.get(getattr(parsing_meta, "name", str(parsing_meta)))
    if form:
        return hypothesis.inflect_form(form)
    return []


def find_near_misses(
    errors_csv_path: str = "errors.csv",
    output_csv_path: str = "near_misses.csv",
):
    with open(errors_csv_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    near_miss_rows: List[Dict[str, Any]] = []
    slot_failure_counter = Counter()

    for row in tqdm(reader, desc="Analyzing near misses"):
        row_found = False

        for entry_type in PRIMARY_VERB_ENTRY_TYPES:
            if row_found:
                break

            entry_forms = [
                (respell_consonants(row[form.corpus_key]), form)
                for form in entry_type.forms
                if row.get(form.corpus_key) and " " not in row[form.corpus_key]
            ]
            if len(entry_forms) < 3:
                continue

            for idx in range(len(entry_forms)):
                omitted_surface, omitted_spec = entry_forms[idx]
                subset_forms = [f for j, f in enumerate(entry_forms) if j != idx]

                derived_hypotheses = derive_hypotheses_for_forms(subset_forms)
                if not derived_hypotheses:
                    continue

                if entry_type.name.startswith("Stative"):
                    derived_hypotheses = {
                        h for h in derived_hypotheses if h.aspect_class.startswith("stative")
                    }

                valid_hypotheses = [
                    h for h in derived_hypotheses
                    if validate_form_subset(h, subset_forms)
                ]

                if valid_hypotheses:
                    # Found near miss!
                    row_found = True
                    for h in sorted(
                        valid_hypotheses,
                        key=lambda x: (
                            x.h_root,
                            x.h_alt_tag or "[H_alt=none]",
                            x.aspect_class,
                            x.prefix_class,
                            x.tense_present_class,
                        ),
                    ):
                        generated = generate_for_slot(h, omitted_spec)
                        slot_failure_counter[omitted_spec.corpus_key] += 1
                        near_miss_rows.append({
                            "corpus_id": row["corpus_id"],
                            "entry_no": row["entry_no"],
                            "definition": row["definition"],
                            "entry_type": entry_type.name,
                            "failed_slot": omitted_spec.corpus_key,
                            "corpus_form": row[omitted_spec.corpus_key],
                            "generated_forms": "; ".join(generated) if generated else "<none>",
                            "h_root": h.h_root,
                            "h_alt_tag": h.h_alt_tag or "[H_alt=none]",
                            "aspect_class": h.aspect_class,
                            "prefix_class": h.prefix_class,
                            "tense_present_class": h.tense_present_class,
                            "set_a": h.set_a,
                            "plural": h.plural,
                            "animate_objects": h.animate_objects,
                            "present": row.get("present", ""),
                            "present_1sg": row.get("present_1sg", ""),
                            "imperfective": row.get("imperfective", ""),
                            "perfective": row.get("perfective", ""),
                            "imperative": row.get("imperative", ""),
                            "infinitive": row.get("infinitive", ""),
                        })
                    break

    fieldnames = [
        "corpus_id",
        "entry_no",
        "definition",
        "entry_type",
        "failed_slot",
        "corpus_form",
        "generated_forms",
        "h_root",
        "h_alt_tag",
        "aspect_class",
        "prefix_class",
        "tense_present_class",
        "set_a",
        "plural",
        "animate_objects",
        "present",
        "present_1sg",
        "imperfective",
        "perfective",
        "imperative",
        "infinitive",
    ]

    with open(output_csv_path, mode="w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in near_miss_rows:
            writer.writerow(r)

    print(f"\nCreated {output_csv_path} with {len(near_miss_rows)} near-miss rows across {len(set(r['corpus_id'] for r in near_miss_rows))} unique error verbs.")
    print("Breakdown by failed slot:")
    for slot, count in slot_failure_counter.most_common():
        print(f"  - {slot}: {count}")


if __name__ == "__main__":
    find_near_misses()
