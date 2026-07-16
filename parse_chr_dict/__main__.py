import csv
from tqdm import tqdm

from parse_chr_dict.create_aspect_class_csv import respell_consonants
from parse_chr_dict.parse import get_roots_for_forms

LEXICAL_FEATURES = {
    "aspect_class",
    "prefix_class",
    "tense_present_class",
    "translocutive",
}


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
        roots_writer = csv.DictWriter(
            roots_f, fieldnames=fieldnames + ["root"] + sorted(LEXICAL_FEATURES)
        )
        roots_writer.writeheader()
        next(reader)
        rows = list(reader)
        # rows = rows[:10]
        for row in tqdm(rows):
            # if not row["corpus_id"] == "1754":
            #     continue
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
            roots = get_roots_for_forms(forms, LEXICAL_FEATURES)
            # print(roots)
            if len(roots):
                for r, label_values in roots:
                    data = {**row}
                    data["root"] = r

                    for k, v in label_values:
                        data[k] = v

                    roots_writer.writerow(data)
            else:
                error_writer.writerow(row)


if __name__ == "__main__":
    main()
