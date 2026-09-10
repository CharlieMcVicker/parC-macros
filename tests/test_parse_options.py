import io
import json
import sys
import pytest

from parse_chr_dict.parse import (
    get_parse_graph,
    get_specialized_parse_graph,
    parse,
    read_parse,
)
from parse_chr_dict.parse_options import (
    PrefixBundle,
    SuffixBundle,
    RootParseOptions,
    WordParseOptions,
    extract_parse_options,
    main as parse_options_main,
)
from parse_chr_dict.types import PRES_1SG, PRES_3RD


@pytest.fixture(scope="module")
def parse_graph():
    return get_parse_graph()


def test_prefix_bundle_methods():
    pb = PrefixBundle(
        prepronominal_prefixes=("[WI]",),
        prefix_class="1",
        pronominal="1sg.A",
        h_metathesis_tag="[H_metathesis=none]",
        h_alt_tag="[H_alt=none]",
    )
    assert pb.to_tag_string() == "[WI][PrefixClass=1][Pro=1sg.A][H_metathesis=none][H_alt=none]"
    d = pb.to_dict()
    assert d["prefix_class"] == "1"
    assert d["pronominal"] == "1sg.A"
    assert d["prepronominal_prefixes"] == ("[WI]",)


def test_suffix_bundle_methods():
    sb = SuffixBundle(
        aspect_class="regular",
        variant=2,
        aspect="present",
        tense="present_a",
    )
    assert sb.to_tag_string() == "[AspectClass=regular][Variant=2][Aspect=present][Tense=present_a]"
    d = sb.to_dict()
    assert d["aspect_class"] == "regular"
    assert d["variant"] == 2
    assert d["aspect"] == "present"
    assert d["tense"] == "present_a"


def test_extract_parse_options_katateka(parse_graph):
    word_opts = extract_parse_options("katateka", fst=parse_graph)
    assert word_opts.surface == "katateka"
    assert word_opts.total_parses == 852
    assert word_opts.distinct_roots_count > 0

    # Total parses must equal the count of string parses from parse.py
    flat_parses = parse("katateka")
    assert len(flat_parses) == word_opts.total_parses

    # Verify root grouping matches parse.py
    expected_roots = {read_parse(p).root for p in flat_parses}
    actual_roots = {r.root for r in word_opts.roots}
    assert actual_roots == expected_roots

    # Check a specific root
    atateka_opts = word_opts.get_root("atateka")
    assert atateka_opts is not None
    assert atateka_opts.total_parses == 6
    assert atateka_opts.is_fully_factorable
    assert len(atateka_opts.prefix_bundles) == 3
    assert len(atateka_opts.suffix_bundles) == 2
    assert "1sg.A" in atateka_opts.pronominal_options
    assert "3sg.A" in atateka_opts.pronominal_options
    assert "sk-h" in atateka_opts.aspect_class_options
    assert "immediate" in atateka_opts.aspect_options

    # Verify JSON serialization
    data = word_opts.to_dict()
    assert data["surface"] == "katateka"
    assert data["total_parses"] == 852
    assert len(data["roots"]) == word_opts.distinct_roots_count


def test_extract_parse_options_with_nfs(parse_graph):
    word_opts = extract_parse_options("awhahthvhitoha", fst=parse_graph)
    assert word_opts.surface == "awhahthvhitoha"
    assert word_opts.total_parses > 0

    # Ensure NFS tagged roots are correctly extracted
    nfs_roots = [r for r in word_opts.roots if "[NFS=" in r.root]
    assert len(nfs_roots) > 0
    assert any("whahthvh[NFS=AMB]" in r.root for r in nfs_roots)


def test_extract_parse_options_with_specialized_graphs():
    sg_3rd = get_specialized_parse_graph(PRES_3RD)
    opts_3rd = extract_parse_options("katateka", fst=sg_3rd)
    assert opts_3rd.total_parses == 25
    assert all("3sg.A" in r.pronominal_options or "3sg.B" in r.pronominal_options or "3ns.A" in r.pronominal_options for r in opts_3rd.roots)

    sg_1sg = get_specialized_parse_graph(PRES_1SG)
    opts_1sg = extract_parse_options("katateka", fst=sg_1sg)
    assert opts_1sg.total_parses == 150
    assert all("1sg.A" in r.pronominal_options or "1sg.B" in r.pronominal_options for r in opts_1sg.roots)


def test_invalid_surface_returns_empty(parse_graph):
    word_opts = extract_parse_options("zzzzzzzzzzzz", fst=parse_graph)
    assert word_opts.total_parses == 0
    assert word_opts.roots == ()
    assert word_opts.distinct_roots_count == 0
    assert "(no valid parses found)" in word_opts.format_report()


def test_cli_argument_execution(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["parse_options", "katateka"])
    parse_options_main()
    captured = capsys.readouterr()
    assert "WORD: katateka" in captured.out
    assert "SUMMARY: 852 total parses across" in captured.out
    assert "Prefix variations" in captured.out
    assert "Suffix variations" in captured.out


def test_cli_verbose_and_json(monkeypatch, capsys):
    # Test --json flag
    monkeypatch.setattr(sys, "argv", ["parse_options", "katateka", "--json"])
    parse_options_main()
    captured = capsys.readouterr()
    parsed_json = json.loads(captured.out)
    assert parsed_json["surface"] == "katateka"
    assert parsed_json["total_parses"] == 852

    # Test --verbose flag
    monkeypatch.setattr(sys, "argv", ["parse_options", "katateka", "-v"])
    parse_options_main()
    captured_verbose = capsys.readouterr()
    assert "Prefix Bundles:" in captured_verbose.out
    assert "Suffix Bundles:" in captured_verbose.out


def test_cli_batch_json(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["parse_options", "--json", "katateka", "awhahthvhitoha"])
    parse_options_main()
    captured = capsys.readouterr()
    parsed_json = json.loads(captured.out)
    assert "results" in parsed_json
    assert len(parsed_json["results"]) == 2
    assert parsed_json["results"][0]["surface"] == "katateka"
    assert parsed_json["results"][0]["total_parses"] == 852
    assert parsed_json["results"][1]["surface"] == "awhahthvhitoha"
    assert parsed_json["results"][1]["total_parses"] > 0


def test_cli_batch_multiple_words_text(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["parse_options", "katateka", "awhahthvhitoha"])
    parse_options_main()
    captured = capsys.readouterr()
    assert "WORD: katateka" in captured.out
    assert "WORD: awhahthvhitoha" in captured.out


def test_cli_positional_delimiter(monkeypatch, capsys):
    # Test -- delimiter allowing surface tokens starting with hyphens
    monkeypatch.setattr(sys, "argv", ["parse_options", "--json", "--", "-v", "katateka"])
    parse_options_main()
    captured = capsys.readouterr()
    parsed_json = json.loads(captured.out)
    assert "results" in parsed_json
    assert len(parsed_json["results"]) == 2
    assert parsed_json["results"][0]["surface"] == "-v"
    assert parsed_json["results"][0]["total_parses"] == 0
    assert parsed_json["results"][1]["surface"] == "katateka"
    assert parsed_json["results"][1]["total_parses"] == 852


def test_cli_interactive_execution(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["parse_options"])
    monkeypatch.setattr("sys.stdin", io.StringIO("katateka\n\n"))
    parse_options_main()
    captured = capsys.readouterr()
    assert "Interactive parse options inspection" in captured.out
    assert "PARSE OPTIONS:" in captured.out
    assert "WORD: katateka" in captured.out


def test_dynamic_slot_manifest_adaptation():
    from parse_chr_dict.parse_options import parse_token_sequence

    custom_manifest = {
        "slots": [
            {
                "name": "voice",
                "role": "prefix",
                "tags": ["VoicePrefix"],
            },
            {
                "name": "pronominal",
                "role": "prefix",
                "tags": ["PrefixClass", "Pro"],
            },
            {
                "name": "aspect",
                "role": "suffix",
                "tags": ["AspectClass", "Variant", "Aspect"],
            },
            {
                "name": "nfs",
                "role": "suffix",
                "tags": ["NFSClass", "NFSSuffix"],
            },
        ],
        "template": [
            "<PrepronominalPrefixes>",
            "<VoicePrefix>",
            "<PrefixClass>",
            "<Pro>",
            "<H_alt>",
            "<Root>",
            "<AspectClass>",
            "<Variant>",
            "<Aspect>",
            "<NFSClass>",
            "<NFSSuffix>",
        ],
        "tag_to_slot": {
            "VoicePrefix": "voice",
            "PrefixClass": "pronominal",
            "Pro": "pronominal",
            "AspectClass": "aspect",
            "Variant": "aspect",
            "Aspect": "aspect",
            "NFSClass": "nfs",
            "NFSSuffix": "nfs",
        },
        "root_boundaries": {
            "left": "<H_alt>",
            "right": "<AspectClass>",
        },
    }

    tokens = [
        "[VoicePrefix=mid]",
        "[PrefixClass=1]",
        "[Pro=1sg.A]",
        "[H_alt=none]",
        "t",
        "a",
        "t",
        "e",
        "k",
        "a",
        "[AspectClass=regular]",
        "[Variant=1]",
        "[Aspect=present]",
        "[NFSClass=noun]",
        "[NFSSuffix=amb]",
    ]

    prefix_b, root, suffix_b = parse_token_sequence(tokens, manifest=custom_manifest)
    assert root == "tateka"
    assert prefix_b.prefix_class == "1"
    assert prefix_b.pronominal == "1sg.A"
    assert prefix_b.h_alt_tag == "[H_alt=none]"
    assert ("VoicePrefix", "mid") in prefix_b.slot_values

    assert suffix_b.aspect_class == "regular"
    assert suffix_b.variant == 1
    assert suffix_b.aspect == "present"
    assert ("NFSClass", "noun") in suffix_b.slot_values
    assert ("NFSSuffix", "amb") in suffix_b.slot_values


def test_root_parse_options_dynamic_slot_options(parse_graph):
    word_opts = extract_parse_options("katateka", fst=parse_graph)
    atateka = word_opts.get_root("atateka")
    assert atateka is not None
    assert isinstance(atateka.slot_options, dict)
    assert "pronominal" in atateka.slot_options
    assert "prefix_class" in atateka.slot_options
    assert "aspect_class" in atateka.slot_options
    assert "aspect" in atateka.slot_options
    assert "tense" in atateka.slot_options
    assert "1sg.A" in atateka.slot_options["pronominal"]


def test_root_parse_options_create_factory():
    pb = PrefixBundle(
        prefix_class="1",
        pronominal="1sg.A",
        slot_values=(("VoicePrefix", "mid"),),
    )
    sb = SuffixBundle(
        aspect_class="regular",
        aspect="present",
        slot_values=(("NFSClass", "noun"),),
    )
    rpo = RootParseOptions.create(
        root="test_root",
        prefix_bundles=(pb,),
        suffix_bundles=(sb,),
        total_parses=1,
        pronominal_options=("1sg.A",),
        aspect_options=("present",),
    )
    assert rpo.root == "test_root"
    assert rpo.total_parses == 1
    assert rpo.slot_options["pronominal"] == ("1sg.A",)
    assert rpo.slot_options["aspect"] == ("present",)


def test_bundle_get_and_slots_properties():
    pb = PrefixBundle(
        prefix_class="1",
        pronominal="1sg.A",
        slot_values=(("VoicePrefix", "mid"),),
    )
    assert pb.get("prefix_class") == "1"
    assert pb.get("VoicePrefix") == "mid"
    assert pb.get("voice_prefix") == "mid"
    assert pb.get("nonexistent", "fallback") == "fallback"
    assert pb.slots["VoicePrefix"] == "mid"

    sb = SuffixBundle(
        aspect_class="regular",
        variant=2,
        aspect="present",
        tense="present_a",
        slot_values=(("NFSSuffix", "amb"),),
    )
    assert sb.get("aspect_class") == "regular"
    assert sb.get("variant") == 2
    assert sb.get("NFSSuffix") == "amb"
    assert sb.get("nfs_suffix") == "amb"
    assert sb.get("missing", 42) == 42
    assert sb.slots["NFSSuffix"] == "amb"


