from dataclasses import dataclass
import json

from typing import IO

from csv import DictWriter, DictReader
import re

DATA_COLS = {
    "present": "present",
    "incompletive": "imperfective",
    "completive": "perfective",
    "immediate": "imperative",
    "infinitive": "infinitive",
}


def respell_consonants(s):
    s = re.sub("([aeiouv])hs", "\\1s", s)
    if s.startswith("hs"):
        s = s[1:]
    return s


def write_metadata(dest: IO[str], *metadata: str):
    dest.writelines([line + "\n" for line in metadata])


def setup_aspect_class_writer(dest: IO[str]):
    write_metadata(
        dest,
        "# kind: suffix",
        "# stage: aspect_suffix",
        "# feature: aspect",
        "# part_of_speech: $verb",
        "# class_feature: aspect_class",
    )

    writer = DictWriter(dest, fieldnames=["paradigm"] + list(DATA_COLS.keys()))
    writer.writerows({"paradigm": metadata} for metadata in [])
    writer.writeheader()

    return writer


def setup_aspect_acceptor_writer(dest: IO[str]):
    write_metadata(dest, "# part_of_speech: $verb")

    writer = DictWriter(dest, fieldnames=["aspect_class", "acceptor"])
    writer.writeheader()

    return writer


def setup_aspect_rule_writer(dest: IO[str], rule: str, stage: str):
    write_metadata(
        dest,
        "# kind: rule",
        f"# stage: {stage}",
        f"# rule: {rule}",
        "# feature: aspect",
        "# part_of_speech: $verb",
        "# class_feature: aspect_class",
    )

    writer = DictWriter(dest, fieldnames=["paradigm"] + list(DATA_COLS.keys()))
    writer.writeheader()

    return writer


def main():

    with open("chr-data/classes_expanded.csv") as src, open(
        "chr-config/verb-aspect.csv", "w+"
    ) as aspect_class_dest, open(
        "chr-config/feature_acceptors/verb-aspect-acceptors.csv", "w+"
    ) as aspect_acceptor_dest, open(
        "chr-config/verb-aspect-drop-final.csv", "w+"
    ) as drop_final_dest, open(
        "chr-config/verb-aspect-drop-final-two.csv", "w+"
    ) as drop_final_two_dest:
        reader = DictReader(
            src,
            fieldnames=[
                "class",
                "preconditions",
                "present",
                "imperfective",
                "perfective",
                "imperative",
                "infinitive",
            ],
        )
        next(reader)

        aspect_classes_writer = setup_aspect_class_writer(aspect_class_dest)
        aspect_acceptor_writer = setup_aspect_acceptor_writer(aspect_acceptor_dest)
        drop_final_writer = setup_aspect_rule_writer(
            drop_final_dest, "$drop_final", stage="final_dropping"
        )
        drop_final_two_writer = setup_aspect_rule_writer(
            drop_final_two_dest, "$drop_final_two", stage="final_dropping"
        )

        for row in reader:
            aspect_class = row.pop("class")
            precon = row.pop("preconditions")
            acceptor = None
            if len(precon):
                precons = []
                for p in precon:
                    p = p.replace("C", "<C>")
                    p = p.replace("V", "<V>")
                    precons.append(f"(<Phone>*{p})")
                acceptor = "|".join(precons)

            if acceptor:
                aspect_acceptor_writer.writerow(
                    {
                        "aspect_class": aspect_class,
                        "acceptor": acceptor,
                    }
                )

            data = {}
            drop_final = set()
            drop_final_two = set()
            for k, v in DATA_COLS.items():
                literal = row[v]
                if literal.startswith("*"):
                    drop_final.add(k)
                    literal = literal[1:]
                if literal.startswith("@"):
                    drop_final_two.add(k)
                    literal = literal[1:]

                data[k] = respell_consonants(literal)

            if len(drop_final):
                drop_final_writer.writerow(
                    {
                        "paradigm": aspect_class,
                        **{
                            k: "Y" if k in drop_final else "N" for k in DATA_COLS.keys()
                        },
                    }
                )

            if len(drop_final_two):
                drop_final_two_writer.writerow(
                    {
                        "paradigm": aspect_class,
                        **{
                            k: "Y" if k in drop_final_two else "N"
                            for k in DATA_COLS.keys()
                        },
                    }
                )

            aspect_classes_writer.writerow({"paradigm": aspect_class, **data})


if __name__ == "__main__":
    main()
