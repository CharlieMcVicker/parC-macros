import csv
from pathlib import Path
import pytest

from parse_chr_dict.create_aspect_class_csv import (
    parse_classes_csv,
    generate_inplace_aspect_csv,
    generate_aspect_effects_csv,
    respell_consonants,
)

REPO_ROOT = Path(__file__).parent.parent.resolve()
CLASSES_CSV = REPO_ROOT / "chr-data" / "classes.csv"
VERB_ASPECT_CSV = REPO_ROOT / "chr-inplace-config" / "verb-aspect.csv"
DROP_FINAL_CSV = REPO_ROOT / "chr-inplace-config" / "verb-aspect-drop-final.csv"
DROP_FINAL_TWO_CSV = REPO_ROOT / "chr-inplace-config" / "verb-aspect-drop-final-two.csv"
ASPECT_EFFECTS_CSV = REPO_ROOT / "chr-clean-inplace-config" / "aspect_effects.csv"
CLEAN_VERB_ASPECT_CSV = REPO_ROOT / "chr-clean-inplace-config" / "verb-aspect.csv"


def test_parse_classes_csv_and_triggers():
    """Verify parsing classes.csv, row count, final-dropping triggers, and effects."""
    (
        rows_out,
        mark_final_triggers,
        mark_final_two_triggers,
        drop_final_rows,
        drop_final_two_rows,
        effects,
    ) = parse_classes_csv(str(CLASSES_CSV))

    # Exactly 55 classes
    assert len(rows_out) == 55
    paradigms = [r["paradigm"] for r in rows_out]
    assert len(set(paradigms)) == 55

    # No bracketed variant names
    for p in paradigms:
        assert "[" not in p, f"Found bracketed paradigm: {p}"

    # Verify mark_final triggers
    expected_mark_final = [
        "[AspectClass=hvsk-nh][Variant=2][Aspect=infinitive]",
        "[AspectClass=hvsk-nh][Variant=4][Aspect=infinitive]",
        "[AspectClass=hvsk-n][Aspect=infinitive]",
        "[AspectClass=apl][Aspect=immediate]",
    ]
    assert mark_final_triggers == expected_mark_final

    # Verify mark_final_two triggers
    expected_mark_final_two = [
        "[AspectClass=apl][Variant=2][Aspect=immediate]",
    ]
    assert mark_final_two_triggers == expected_mark_final_two

    # Verify effects
    expected_effects = [
        {"aspect_class": "hvsk-nh", "aspect": "infinitive", "variant": 2, "effect": "drop_final"},
        {"aspect_class": "hvsk-nh", "aspect": "infinitive", "variant": 4, "effect": "drop_final"},
        {"aspect_class": "hvsk-n", "aspect": "infinitive", "variant": 1, "effect": "drop_final"},
        {"aspect_class": "apl", "aspect": "immediate", "variant": 1, "effect": "drop_final"},
        {"aspect_class": "apl", "aspect": "immediate", "variant": 2, "effect": "drop_final_two"},
    ]
    assert effects == expected_effects


def test_verb_aspect_csv_content():
    """Verify generated chr-inplace-config/verb-aspect.csv format and values."""
    assert VERB_ASPECT_CSV.exists()

    with open(VERB_ASPECT_CSV, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Metadata comments
    comments = [line for line in lines if line.startswith("#")]
    assert comments == [
        "# kind: morpheme_replace",
        "# morpheme_tag: [Aspect]",
        "# stage: aspect_suffix",
        "# feature: aspect",
        "# part_of_speech: $verb",
        "# class_feature: aspect_class",
    ]

    data_lines = [line for line in lines if not line.startswith("#")]
    assert data_lines[0] == "paradigm,present,incompletive,completive,immediate,infinitive"

    reader = csv.DictReader(data_lines)
    rows = list(reader)
    assert len(rows) == 55

    class_dict = {r["paradigm"]: r for r in rows}

    # Spot checks on multi-variant classes
    assert class_dict["become"]["infinitive"] == "st;'ist;yhst;ist"
    assert class_dict["sk-s-a"]["infinitive"] == "hist;st"
    assert class_dict["sk-s-hst"]["immediate"] == ";hi"
    assert class_dict["sk-h"]["immediate"] == "ha;"
    assert class_dict["hvsk-nh"]["infinitive"] == "ht;ht;hvst;oht"
    assert class_dict["apl"]["immediate"] == "si;si;isi;vla"
    assert class_dict["go"]["present"] == "ek;"
    assert class_dict["go-in"]["completive"] == "invs;es"
    assert class_dict["cause"]["present"] == "ih;"
    assert class_dict["cause"]["completive"] == "han;anh;an"
    assert class_dict["vnh-vsk"]["infinitive"] == "ht;vht;vnht;vst"
    assert class_dict["oh-ol"]["infinitive"] == "ot;st;ast"


def test_drop_final_csvs():
    """Verify drop-final CSV files generated in chr-inplace-config."""
    assert DROP_FINAL_CSV.exists()
    assert DROP_FINAL_TWO_CSV.exists()

    with open(DROP_FINAL_CSV, "r", encoding="utf-8") as f:
        df_rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    header = df_rows[0]
    assert header == ["paradigm", "immediate", "infinitive"]
    assert df_rows[1:] == [
        ["hvsk-nh[Variant=2]", "N", "Y"],
        ["hvsk-nh[Variant=4]", "N", "Y"],
        ["hvsk-n", "N", "Y"],
        ["apl", "Y", "N"],
    ]

    with open(DROP_FINAL_TWO_CSV, "r", encoding="utf-8") as f:
        df2_rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    header2 = df2_rows[0]
    assert header2 == ["paradigm", "immediate"]
    assert df2_rows[1:] == [
        ["apl[Variant=2]", "Y"],
    ]


def test_aspect_effects_csv_content():
    """Verify generated chr-clean-inplace-config/aspect_effects.csv format and values."""
    assert ASPECT_EFFECTS_CSV.exists()

    with open(ASPECT_EFFECTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["aspect_class", "aspect", "variant", "effect"]
        rows = list(reader)

    assert len(rows) == 5
    assert rows == [
        {"aspect_class": "hvsk-nh", "aspect": "infinitive", "variant": "2", "effect": "drop_final"},
        {"aspect_class": "hvsk-nh", "aspect": "infinitive", "variant": "4", "effect": "drop_final"},
        {"aspect_class": "hvsk-n", "aspect": "infinitive", "variant": "1", "effect": "drop_final"},
        {"aspect_class": "apl", "aspect": "immediate", "variant": "1", "effect": "drop_final"},
        {"aspect_class": "apl", "aspect": "immediate", "variant": "2", "effect": "drop_final_two"},
    ]


def test_clean_verb_aspect_csv_no_symbols():
    """Verify chr-clean-inplace-config/verb-aspect.csv has zero '*' or '@' characters."""
    assert CLEAN_VERB_ASPECT_CSV.exists()
    content = CLEAN_VERB_ASPECT_CSV.read_text(encoding="utf-8")
    assert "*" not in content
    assert "@" not in content


def test_generate_aspect_effects_csv_helper(tmp_path):
    """Verify generate_aspect_effects_csv creates valid CSV with expected rows."""
    out_file = tmp_path / "effects.csv"
    sample_effects = [
        {"aspect_class": "test-cls", "aspect": "immediate", "variant": 1, "effect": "drop_final"}
    ]
    generate_aspect_effects_csv(sample_effects, str(out_file))
    assert out_file.exists()
    with open(out_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["aspect_class", "aspect", "variant", "effect"]
        rows = list(reader)
    assert rows == [{"aspect_class": "test-cls", "aspect": "immediate", "variant": "1", "effect": "drop_final"}]
