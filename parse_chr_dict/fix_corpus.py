import csv

from parse_chr_dict.create_aspect_class_csv import respell_consonants


def main():
    input_path = "chr-corpus/corpus_export.csv"
    output_path = "chr-corpus/corpus.csv"
    meta_cols = [
        "corpus_id",
        "entry_no",
        "definition",
    ]

    value_cols = [
        "present",
        "present_1sg",
        "imperfective",
        "perfective",
        "imperative",
        "infinitive",
    ]

    def make_output_row(input_row):
        data = {k: input_row[k] for k in meta_cols}
        for val in value_cols:
            data[val] = respell_consonants(input_row[val])
        return data

    with open(input_path, newline="", encoding="utf-8") as infile, open(
        output_path, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(
            infile, fieldnames=meta_cols + ["prediction"] + value_cols
        )
        next(reader)
        writer = csv.DictWriter(outfile, fieldnames=meta_cols + value_cols)
        writer.writeheader()

        last_row = None
        for row in reader:
            if last_row is None:
                last_row = row
                continue

            if row["corpus_id"] == last_row["corpus_id"]:
                for col in value_cols:
                    if row[col] != last_row[col]:
                        raise ValueError(
                            f"Mismatch for corpus_id {row['corpus_id']} on column {col}: "
                            f"{last_row[col]} != {row[col]}"
                        )
                continue

            writer.writerow(make_output_row(last_row))
            last_row = row

        if last_row is not None:
            writer.writerow(make_output_row(last_row))


if __name__ == "__main__":
    main()
