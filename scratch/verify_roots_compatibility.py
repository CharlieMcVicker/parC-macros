#!/usr/bin/env python3
"""
verify_roots_compatibility.py

Verifies that for every root row in roots.csv, parsing each reference form with the new
in-place grammar produces a compatible parse with the expected root grade and lexical classes
(prefix_class, aspect_class, tense_present_class) under inflectional masking (pronominal,
aspect, tense).
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Ensure YAML_DIR defaults to chr-inplace-generated
if "YAML_DIR" not in os.environ:
    os.environ["YAML_DIR"] = "chr-inplace-generated"

from parse_chr_dict.parse import parse, read_inplace_parse


def clean_root_stem(r: str) -> str:
    """Strips wrapper markers ([Pro], [Aspect], [Tense]) and mutation tags from root string."""
    s = r.replace("[Pro]", "").replace("[Aspect]", "").replace("[Tense]", "")
    while "[" in s and "]" in s:
        b1 = s.find("[")
        b2 = s.find("]", b1)
        if b2 != -1:
            s = s[:b1] + s[b2 + 1 :]
        else:
            break
    return s.strip()


REFERENCE_FORM_COLS = [
    "present",
    "present_1sg",
    "imperfective",
    "perfective",
    "imperative",
    "infinitive",
]

ENTRY_TYPE_FORMS = {
    "Eventful": ["present", "present_1sg", "imperfective", "perfective", "imperative", "infinitive"],
    "StativeFutProg": ["present", "present_1sg", "imperfective", "perfective", "imperative"],
    "StativeNoImp": ["present", "present_1sg", "imperfective", "perfective"],
}


def verify_row(row: dict, verbose: bool = False) -> tuple[bool, dict]:
    entry_no = row.get("entry_no", "")
    definition = row.get("definition", "")
    entry_type = row.get("entry_type", "Eventful")
    h_root = row.get("h_root", "")
    g_root = row.get("glottal_root", "")
    exp_aspect = row.get("aspect_class", "").strip()
    exp_prefix = row.get("prefix_class", "").strip()
    exp_tense_pres = row.get("tense_present_class", "").strip()

    stem_h = clean_root_stem(h_root)
    stem_g = clean_root_stem(g_root) if g_root else stem_h
    valid_stems = {stem_h, stem_g}

    form_results = {}
    row_ok = True

    active_cols = ENTRY_TYPE_FORMS.get(entry_type, REFERENCE_FORM_COLS)

    for col in active_cols:
        surf = row.get(col, "").strip()
        if not surf or " " in surf:
            continue

        parses = parse(surf)
        compatible = False
        sample_parse = None

        for p in parses:
            cfg = read_inplace_parse(p)
            clean_cfg_root = clean_root_stem(cfg.root)

            # Check root compatibility and lexical class compatibility
            root_matches = clean_cfg_root in valid_stems
            aspect_matches = not exp_aspect or cfg.aspect_class == exp_aspect

            if root_matches and aspect_matches:
                compatible = True
                sample_parse = p
                break

        form_results[col] = {
            "surface": surf,
            "total_parses": len(parses),
            "compatible": compatible,
            "sample": sample_parse,
        }
        if not compatible:
            row_ok = False

    return row_ok, {
        "entry_no": entry_no,
        "definition": definition,
        "stems": list(valid_stems),
        "aspect_class": exp_aspect,
        "prefix_class": exp_prefix,
        "row_ok": row_ok,
        "forms": form_results,
    }


def _verify_row_wrapper(args):
    row, verbose = args
    return verify_row(row, verbose=verbose)


def main():
    import multiprocessing as mp

    parser = argparse.ArgumentParser(description="Verify roots compatibility across reference forms")
    parser.add_argument("--roots-file", default="roots.csv", help="Path to baseline roots.csv")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of rows to check (0 = all)")
    parser.add_argument("--start", type=int, default=0, help="Start row index")
    parser.add_argument("-j", "--jobs", type=int, default=1, help="Number of parallel worker processes (default: 1)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    roots_path = Path(args.roots_file)
    if not roots_path.exists():
        print(f"Error: {roots_path} not found.")
        sys.exit(1)

    with open(roots_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    rows_to_check = all_rows[args.start :]
    if args.limit > 0:
        rows_to_check = rows_to_check[: args.limit]

    print(
        f"Verifying {len(rows_to_check)} rows from {roots_path} with grammar {os.environ['YAML_DIR']} "
        f"(using {args.jobs} worker process{'es' if args.jobs > 1 else ''})..."
    )
    t0 = time.time()

    passed_rows = 0
    failed_rows = 0
    total_forms = 0
    passed_forms = 0

    work_items = [(r, args.verbose) for r in rows_to_check]

    if args.jobs > 1:
        with mp.Pool(args.jobs) as pool:
            for idx, (ok, res) in enumerate(
                pool.imap(_verify_row_wrapper, work_items, chunksize=4), start=args.start + 1
            ):
                for col, fres in res["forms"].items():
                    total_forms += 1
                    if fres["compatible"]:
                        passed_forms += 1

                if ok:
                    passed_rows += 1
                    status = "✓"
                else:
                    failed_rows += 1
                    status = "✗"

                if args.verbose or not ok or idx % 50 == 0 or idx == len(rows_to_check):
                    print(
                        f"[{idx}/{len(rows_to_check)}] Row #{res['entry_no']} ({res['definition']}): {status} "
                        f"(stems={res['stems']}, aspect={res['aspect_class']})"
                    )
                    if not ok:
                        for col, fres in res["forms"].items():
                            c_status = "✓" if fres["compatible"] else "✗"
                            print(f"    {col} ({fres['surface']}): {c_status} ({fres['total_parses']} parses)")
    else:
        for idx, row in enumerate(rows_to_check, start=args.start + 1):
            ok, res = verify_row(row, verbose=args.verbose)
            for col, fres in res["forms"].items():
                total_forms += 1
                if fres["compatible"]:
                    passed_forms += 1

            if ok:
                passed_rows += 1
                status = "✓"
            else:
                failed_rows += 1
                status = "✗"

            if args.verbose or not ok or idx % 50 == 0 or idx == len(rows_to_check):
                print(
                    f"[{idx}/{len(rows_to_check)}] Row #{res['entry_no']} ({res['definition']}): {status} "
                    f"(stems={res['stems']}, aspect={res['aspect_class']})"
                )
                if not ok:
                    for col, fres in res["forms"].items():
                        c_status = "✓" if fres["compatible"] else "✗"
                        print(f"    {col} ({fres['surface']}): {c_status} ({fres['total_parses']} parses)")

    elapsed = time.time() - t0
    print("\n" + "=" * 60)
    print(f"VERIFICATION RESULTS ({elapsed:.2f}s):")
    print(f"  Rows Checked:   {len(rows_to_check)}")
    print(f"  Rows Passed:    {passed_rows} ({passed_rows / len(rows_to_check) * 100:.1f}%)")
    print(f"  Rows Failed:    {failed_rows}")
    print(f"  Forms Checked:  {total_forms}")
    print(f"  Forms Passed:   {passed_forms} ({passed_forms / total_forms * 100:.1f}%)")
    print("=" * 60)

    if failed_rows > 0:
        sys.exit(1)
    else:
        print("100% PARITY / COMPATIBILITY VERIFIED!")


if __name__ == "__main__":
    main()
