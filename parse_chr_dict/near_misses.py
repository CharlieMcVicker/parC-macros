import csv
from collections import Counter
from dataclasses import asdict
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from parse_chr_dict.create_aspect_class_csv import respell_consonants
from parse_chr_dict.h_alternation import is_h_alternation_trigger
from parse_chr_dict.meta_label_compiler import (
    FORMS_TO_PARSE,
    PRIMARY_ENTRY_TYPES,
    FormParsingSpec,
    MetaConstraintCompiler,
    derive_hypotheses_for_forms,
    DerivationHypothesis,
)
from parse_chr_dict.reconstruct import memoized_inflect

ENTRY_TYPE_FORMS = {
    entry_type.name: [parsing for parsing in FORMS_TO_PARSE if parsing.name in entry_type.forms]
    for entry_type in PRIMARY_ENTRY_TYPES
}


def validate_form_subset(
    hypothesis: DerivationHypothesis,
    forms: List[tuple[str, FormParsingSpec]],
    compiler: MetaConstraintCompiler,
) -> bool:
    meta_comb = hypothesis.to_meta_combination()
    labels = {**hypothesis.lexical_labels(), "rules": "+"}
    for surf, parsing_meta in forms:
        if not meta_comb.validate(
            h_root=hypothesis.h_root,
            glottal_root=hypothesis.glottal_root,
            reference_form=surf,
            labels=labels,
            parsing_meta=parsing_meta,
            compiler=compiler,
        ):
            return False
    return True


def generate_for_slot(
    hypothesis: DerivationHypothesis,
    parsing_meta: FormParsingSpec,
    compiler: MetaConstraintCompiler,
) -> List[str]:
    meta_comb = hypothesis.to_meta_combination()
    target_tuples = compiler.get_feature_tuples_from_meta([parsing_meta.meta_label_id])
    form_labels = dict(target_tuples)
    pronominal_candidates = meta_comb.get_pronominal_candidates(
        person=parsing_meta.person, allow_set_a=parsing_meta.allows_set_a
    )
    pref = hypothesis.prefix_class
    prefix_candidates = (pref, "k_a_stem") if pref == "a_stem" else (pref,)
    generated = set()
    for pro in pronominal_candidates:
        if is_h_alternation_trigger(pro):
            if hypothesis.glottal_root is None:
                continue
            active_root = hypothesis.glottal_root
        else:
            active_root = hypothesis.h_root

        for p_cand in prefix_candidates:
            all_labels = {
                **hypothesis.lexical_labels(),
                **form_labels,
                "pronominal": pro,
                "prefix_class": p_cand,
                "rules": "+",
            }
            surfs = memoized_inflect(
                active_root,
                feature_values=all_labels,
                name="verb",
                open_root=True,
                infer_lexical_features=True,
            )
            generated.update(surfs)
    return sorted(list(generated))


def find_near_misses(
    errors_csv_path: str = "errors.csv",
    output_csv_path: str = "near_misses.csv",
):
    compiler = MetaConstraintCompiler()

    with open(errors_csv_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    near_miss_rows: List[Dict[str, Any]] = []
    slot_failure_counter = Counter()

    for row in tqdm(reader, desc="Analyzing near misses"):
        row_found = False

        for entry_type in PRIMARY_ENTRY_TYPES:
            if row_found:
                break

            entry_forms = [
                (respell_consonants(row[parsing.corpus_key]), parsing)
                for parsing in ENTRY_TYPE_FORMS[entry_type.name]
                if row.get(parsing.corpus_key) and " " not in row[parsing.corpus_key]
            ]
            if len(entry_forms) < 3:
                continue

            for idx in range(len(entry_forms)):
                omitted_surface, omitted_spec = entry_forms[idx]
                subset_forms = [f for j, f in enumerate(entry_forms) if j != idx]

                derived_hypotheses = derive_hypotheses_for_forms(subset_forms, compiler)
                if not derived_hypotheses:
                    continue

                if entry_type.name.startswith("Stative"):
                    derived_hypotheses = {
                        h for h in derived_hypotheses if h.aspect_class.startswith("stative")
                    }

                valid_hypotheses = [
                    h for h in derived_hypotheses
                    if validate_form_subset(h, subset_forms, compiler)
                ]

                if valid_hypotheses:
                    # Found near miss!
                    row_found = True
                    for h in sorted(
                        valid_hypotheses,
                        key=lambda x: (
                            x.h_root,
                            x.glottal_root or "",
                            x.aspect_class,
                            x.prefix_class,
                            x.tense_present_class,
                        ),
                    ):
                        generated = generate_for_slot(h, omitted_spec, compiler)
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
                            "glottal_root": h.glottal_root or "",
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
        "glottal_root",
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
