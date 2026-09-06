from dataclasses import dataclass
import json
from pathlib import Path
from typing import IO
from csv import DictWriter, DictReader
import functools
import re
import argparse

DATA_COLS = {
    "present": "present",
    "incompletive": "imperfective",
    "completive": "perfective",
    "immediate": "imperative",
    "infinitive": "infinitive",
}

STATIVE_DATA_COLS = {
    "present": "present",
    "incompletive": "imperfective",
}


@functools.lru_cache(maxsize=1024)
def respell_consonants(s: str) -> str:
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


def setup_inplace_aspect_class_writer(dest: IO[str], fieldnames: list[str] | None = None):
    write_metadata(
        dest,
        "# kind: morpheme_replace",
        "# morpheme_tag: [Aspect]",
        "# stage: aspect_suffix",
        "# feature: aspect",
        "# part_of_speech: $verb",
        "# class_feature: aspect_class",
    )

    if fieldnames is None:
        fieldnames = ["paradigm"] + list(DATA_COLS.keys())
    writer = DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()

    return writer


def setup_aspect_acceptor_writer(dest: IO[str]):
    write_metadata(dest, "# part_of_speech: $verb")

    writer = DictWriter(dest, fieldnames=["aspect_class", "acceptor"])
    writer.writeheader()

    return writer


def setup_aspect_rule_writer(
    dest: IO[str], rule: str, stage: str, fieldnames: list[str] | None = None
):
    write_metadata(
        dest,
        "# kind: rule",
        f"# stage: {stage}",
        f"# rule: {rule}",
        "# feature: aspect",
        "# part_of_speech: $verb",
        "# class_feature: aspect_class",
    )

    if fieldnames is None:
        fieldnames = ["paradigm"] + list(DATA_COLS.keys())
    writer = DictWriter(dest, fieldnames=fieldnames)
    writer.writeheader()

    return writer


def parse_classes_csv(
    src_path: str = "chr-data/classes.csv",
    separate_stative: bool = True,
):
    """
    Parses chr-data/classes.csv directly.
    Emits unified hyphenated aspect class names (f"{class}-{subclass}" or class).
    Processes semicolon-separated variants, strips '*' and '@', respells consonants.
    Tracks final-dropping triggers for mark_final (*) and mark_final_two (@).
    When separate_stative is True (default), returns (eventful_rows, stative_rows, ...),
    where stative_rows only contains 'present' and 'incompletive' aspect columns.
    When separate_stative is False, returns (rows_out, ...).
    """
    eventful_rows = []
    stative_rows = []
    mark_final_triggers = []
    mark_final_two_triggers = []
    drop_final_rows = []
    drop_final_two_rows = []
    effects = []

    with open(src_path, "r", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            class_name = (
                f"{row['class']}-{row['subclass']}"
                if row["subclass"]
                else row["class"]
            )
            is_stative = row["class"] == "stative" or class_name.startswith("stative")
            cols = (
                STATIVE_DATA_COLS
                if (separate_stative and is_stative)
                else DATA_COLS
            )
            row_data = {"paradigm": class_name}

            for col_name, src_col in cols.items():
                cell_raw = row[src_col]
                variants = cell_raw.split(";")
                processed_variants = []
                for idx, var in enumerate(variants, 1):
                    clean_var = var
                    if clean_var.startswith("*"):
                        clean_var = clean_var[1:]
                        effects.append(
                            {
                                "aspect_class": class_name,
                                "aspect": col_name,
                                "variant": idx,
                                "effect": "drop_final",
                            }
                        )
                        if idx == 1:
                            trigger = (
                                f"[AspectClass={class_name}][Aspect={col_name}]"
                            )
                            drop_paradigm = class_name
                        else:
                            trigger = f"[AspectClass={class_name}][Variant={idx}][Aspect={col_name}]"
                            drop_paradigm = f"{class_name}[Variant={idx}]"
                        mark_final_triggers.append(trigger)
                        drop_final_rows.append((drop_paradigm, col_name))
                    elif clean_var.startswith("@"):
                        clean_var = clean_var[1:]
                        effects.append(
                            {
                                "aspect_class": class_name,
                                "aspect": col_name,
                                "variant": idx,
                                "effect": "drop_final_two",
                            }
                        )
                        if idx == 1:
                            trigger = (
                                f"[AspectClass={class_name}][Aspect={col_name}]"
                            )
                            drop_paradigm = class_name
                        else:
                            trigger = f"[AspectClass={class_name}][Variant={idx}][Aspect={col_name}]"
                            drop_paradigm = f"{class_name}[Variant={idx}]"
                        mark_final_two_triggers.append(trigger)
                        drop_final_two_rows.append((drop_paradigm, col_name))

                    if class_name == "oh-ol" and clean_var == "hst":
                        respelled = "hst"
                    else:
                        respelled = respell_consonants(clean_var)
                    processed_variants.append(respelled)

                row_data[col_name] = ";".join(processed_variants)

            if separate_stative and is_stative:
                stative_rows.append(row_data)
            else:
                eventful_rows.append(row_data)

    if separate_stative:
        return (
            eventful_rows,
            stative_rows,
            mark_final_triggers,
            mark_final_two_triggers,
            drop_final_rows,
            drop_final_two_rows,
            effects,
        )
    return (
        eventful_rows,
        mark_final_triggers,
        mark_final_two_triggers,
        drop_final_rows,
        drop_final_two_rows,
        effects,
    )


def generate_aspect_effects_csv(effects: list[dict], dest_path: str) -> None:
    """
    Writes compact value-driven effect table CSV (aspect_class,aspect,variant,effect).
    """
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "w", encoding="utf-8", newline="") as f:
        writer = DictWriter(
            f, fieldnames=["aspect_class", "aspect", "variant", "effect"]
        )
        writer.writeheader()
        for eff in effects:
            writer.writerow(eff)


def generate_inplace_aspect_config(
    src_path: str = "chr-data/classes.csv",
    dest_path: str = "chr-config/verb-aspect.csv",
    stative_dest_path: str | None = "chr-config/verb-aspect-stative.csv",
    effects_path: str | None = "chr-config/aspect_effects.csv",
    drop_final_path: str | None = None,
    drop_final_two_path: str | None = None,
) -> dict:
    """
    Generates chr-config/verb-aspect.csv, verb-aspect-stative.csv (optional),
    and aspect_effects.csv (or drop-final CSVs) from chr-data/classes.csv.
    Returns summary dict containing triggers, effects, and count of generated rows.
    """
    if stative_dest_path:
        (
            eventful_rows,
            stative_rows,
            mark_final_triggers,
            mark_final_two_triggers,
            drop_final_rows,
            drop_final_two_rows,
            effects,
        ) = parse_classes_csv(src_path, separate_stative=True)

        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            writer = setup_inplace_aspect_class_writer(f)
            for r in eventful_rows:
                writer.writerow(r)

        Path(stative_dest_path).parent.mkdir(parents=True, exist_ok=True)
        with open(stative_dest_path, "w", encoding="utf-8") as f:
            stative_writer = setup_inplace_aspect_class_writer(
                f, fieldnames=["paradigm"] + list(STATIVE_DATA_COLS.keys())
            )
            for r in stative_rows:
                stative_writer.writerow(r)

        num_rows = len(eventful_rows) + len(stative_rows)
        num_eventful = len(eventful_rows)
        num_stative = len(stative_rows)
    else:
        (
            rows_out,
            mark_final_triggers,
            mark_final_two_triggers,
            drop_final_rows,
            drop_final_two_rows,
            effects,
        ) = parse_classes_csv(src_path, separate_stative=False)

        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            writer = setup_inplace_aspect_class_writer(f)
            for r in rows_out:
                writer.writerow(r)

        num_rows = len(rows_out)
        num_eventful = len(rows_out)
        num_stative = 0

    if effects_path:
        generate_aspect_effects_csv(effects, effects_path)

    if drop_final_path:
        Path(drop_final_path).parent.mkdir(parents=True, exist_ok=True)
        with open(drop_final_path, "w", encoding="utf-8") as f:
            writer = setup_aspect_rule_writer(
                f,
                "$drop_final",
                stage="final_dropping",
                fieldnames=["paradigm", "immediate", "infinitive"],
            )
            for paradigm, col in drop_final_rows:
                writer.writerow(
                    {
                        "paradigm": paradigm,
                        "immediate": "Y" if col == "immediate" else "N",
                        "infinitive": "Y" if col == "infinitive" else "N",
                    }
                )

    if drop_final_two_path:
        Path(drop_final_two_path).parent.mkdir(parents=True, exist_ok=True)
        with open(drop_final_two_path, "w", encoding="utf-8") as f:
            writer = setup_aspect_rule_writer(
                f,
                "$drop_final_two",
                stage="final_dropping",
                fieldnames=["paradigm", "immediate"],
            )
            for paradigm, col in drop_final_two_rows:
                writer.writerow(
                    {
                        "paradigm": paradigm,
                        "immediate": "Y" if col == "immediate" else "N",
                    }
                )

    return {
        "num_rows": num_rows,
        "num_eventful": num_eventful,
        "num_stative": num_stative,
        "mark_final_triggers": mark_final_triggers,
        "mark_final_two_triggers": mark_final_two_triggers,
        "effects": effects,
    }


generate_inplace_aspect_csv = generate_inplace_aspect_config


def generate_legacy_aspect_config(
    src_path: str = "chr-data/classes_expanded.csv",
):
    """Legacy generator for chr-config/ using classes_expanded.csv."""
    with open(src_path) as src, open(
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
                            k: "Y" if k in drop_final else "N"
                            for k in DATA_COLS.keys()
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


def main():
    parser = argparse.ArgumentParser(
        description="Generate verb aspect CSV files from Cherokee classes data."
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Run legacy generator from chr-data/classes_expanded.csv into chr-config/",
    )
    parser.add_argument(
        "--src",
        default="chr-data/classes.csv",
        help="Path to source classes.csv (default: chr-data/classes.csv)",
    )
    parser.add_argument(
        "--dest",
        default="chr-config/verb-aspect.csv",
        help="Path to destination verb-aspect.csv (default: chr-config/verb-aspect.csv)",
    )
    parser.add_argument(
        "--stative-dest",
        default="chr-config/verb-aspect-stative.csv",
        help="Path to destination verb-aspect-stative.csv (default: chr-config/verb-aspect-stative.csv)",
    )
    parser.add_argument(
        "--effects",
        default="chr-config/aspect_effects.csv",
        help="Path to destination aspect_effects.csv (default: chr-config/aspect_effects.csv)",
    )
    args = parser.parse_args()

    if args.legacy:
        generate_legacy_aspect_config()
        print("Legacy aspect CSVs generated successfully in chr-config/.")
    else:
        result = generate_inplace_aspect_config(
            src_path=args.src,
            dest_path=args.dest,
            stative_dest_path=args.stative_dest,
            effects_path=args.effects,
        )
        print(
            f"Generated {result['num_eventful']} eventful classes to {args.dest} "
            f"and {result['num_stative']} stative classes to {args.stative_dest}"
        )
        if args.effects:
            print(f"Generated {len(result['effects'])} effect rows to {args.effects}")
        print("\nVerified drop_root_final triggers:")
        print("mark_final (*):")
        for trig in result["mark_final_triggers"]:
            print(f"  {trig}")
        print("mark_final_two (@):")
        for trig in result["mark_final_two_triggers"]:
            print(f"  {trig}")


if __name__ == "__main__":
    main()
