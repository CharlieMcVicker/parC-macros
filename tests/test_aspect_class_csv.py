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
VERB_ASPECT_CSV = REPO_ROOT / "chr-config" / "verb-aspect.csv"
VERB_ASPECT_STATIVE_CSV = REPO_ROOT / "chr-config" / "verb-aspect-stative.csv"
ASPECT_EFFECTS_CSV = REPO_ROOT / "chr-config" / "aspect_effects.csv"


def test_parse_classes_csv_and_triggers():
    """Verify parsing classes.csv, row count, final-dropping triggers, and effects."""
    (
        eventful_rows,
        stative_rows,
        mark_final_triggers,
        mark_final_two_triggers,
        drop_final_rows,
        drop_final_two_rows,
        effects,
    ) = parse_classes_csv(str(CLASSES_CSV))

    # 49 eventful classes and 6 stative classes (55 total)
    assert len(eventful_rows) == 49
    assert len(stative_rows) == 6
    paradigms = [r["paradigm"] for r in eventful_rows + stative_rows]
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
    """Verify generated chr-config/verb-aspect.csv format and values."""
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
    assert len(rows) == 49

    class_dict = {r["paradigm"]: r for r in rows}

    # Statives should be in verb-aspect-stative.csv
    assert VERB_ASPECT_STATIVE_CSV.exists()
    with open(VERB_ASPECT_STATIVE_CSV, "r", encoding="utf-8") as f:
        stative_lines = [line.strip() for line in f if line.strip()]
    stative_data_lines = [line for line in stative_lines if not line.startswith("#")]
    assert stative_data_lines[0] == "paradigm,present,incompletive"
    stative_reader = csv.DictReader(stative_data_lines)
    stative_rows = list(stative_reader)
    assert len(stative_rows) == 6

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
    assert class_dict["oh-ol"]["infinitive"] in ("ot;st;ast", "ot;hst;ast")


def test_drop_final_csvs(tmp_path):
    """Verify drop-final CSV files generated from classes.csv."""
    drop_final_csv = tmp_path / "verb-aspect-drop-final.csv"
    drop_final_two_csv = tmp_path / "verb-aspect-drop-final-two.csv"
    generate_inplace_aspect_csv(
        src_path=str(CLASSES_CSV),
        dest_path=str(tmp_path / "verb-aspect.csv"),
        drop_final_path=str(drop_final_csv),
        drop_final_two_path=str(drop_final_two_csv),
    )
    assert drop_final_csv.exists()
    assert drop_final_two_csv.exists()

    with open(drop_final_csv, "r", encoding="utf-8") as f:
        df_rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    header = df_rows[0]
    assert header == ["paradigm", "immediate", "infinitive"]
    assert df_rows[1:] == [
        ["hvsk-nh[Variant=2]", "N", "Y"],
        ["hvsk-nh[Variant=4]", "N", "Y"],
        ["hvsk-n", "N", "Y"],
        ["apl", "Y", "N"],
    ]

    with open(drop_final_two_csv, "r", encoding="utf-8") as f:
        df2_rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
    header2 = df2_rows[0]
    assert header2 == ["paradigm", "immediate"]
    assert df2_rows[1:] == [
        ["apl[Variant=2]", "Y"],
    ]


def test_aspect_effects_csv_content():
    """Verify generated chr-config/aspect_effects.csv format and values."""
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
    """Verify chr-config/verb-aspect.csv and verb-aspect-stative.csv have zero '*' or '@' characters."""
    assert VERB_ASPECT_CSV.exists()
    content = VERB_ASPECT_CSV.read_text(encoding="utf-8")
    assert "*" not in content
    assert "@" not in content

    assert VERB_ASPECT_STATIVE_CSV.exists()
    stative_content = VERB_ASPECT_STATIVE_CSV.read_text(encoding="utf-8")
    assert "*" not in stative_content
    assert "@" not in stative_content


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
