import io
import sys
import pytest
from parse_chr_dict.parse import get_parse_graph
from parse_chr_dict.segment import (
    get_arc_alignment,
    segment_alignment,
    format_segmentation,
    process_word,
    main as segment_main,
)


@pytest.fixture(scope="module")
def parse_graph():
    return get_parse_graph()


def test_get_arc_alignment_katateka(parse_graph):
    alignment = get_arc_alignment(parse_graph, "katateka")
    assert alignment is not None
    assert len(alignment) > 0

    # Ensure symbols are human-readable (not raw non-printable byte codepoints)
    in_symbols = [i for i, _ in alignment]
    out_symbols = [o for _, o in alignment]

    assert "[BOW]" in in_symbols
    assert "[EOW]" in in_symbols
    assert "k" in in_symbols
    assert "a" in in_symbols
    assert "t" in in_symbols

    assert any(s in out_symbols for s in ("[PrefixClass=vowel_stem]", "[PrefixClass=long_stem]"))
    assert "[Pro=3sg.A]" in out_symbols
    assert "[AspectClass=go-in]" in out_symbols
    assert "[Aspect=present]" in out_symbols


def test_segment_alignment_katateka(parse_graph):
    alignment = get_arc_alignment(parse_graph, "katateka")
    assert alignment is not None
    segments = segment_alignment(alignment)

    stages = [s["stage"] for s in segments]
    assert stages == ["Prefix", "Root", "AspectClass", "Aspect", "Tense"]

    hyphenated = format_segmentation(segments)
    assert hyphenated in ("k-atat-e-k-a", "ka-tat-e-k-a")

    # Verify surface reconstructs the word
    assert "".join(s["surface"] for s in segments) == "katateka"


def test_segment_alignment_atateka(parse_graph):
    alignment = get_arc_alignment(parse_graph, "atateka")
    assert alignment is not None
    segments = segment_alignment(alignment)

    hyphenated = format_segmentation(segments)
    assert hyphenated == "a-tat-e-k-a"
    assert "".join(s["surface"] for s in segments) == "atateka"


def test_segment_alignment_hatatuka(parse_graph):
    alignment = get_arc_alignment(parse_graph, "hatatuka")
    assert alignment is not None
    segments = segment_alignment(alignment)

    hyphenated = format_segmentation(segments)
    assert hyphenated == "h-atat-u-ka"
    assert "".join(s["surface"] for s in segments) == "hatatuka"


def test_get_arc_alignment_invalid_surface(parse_graph):
    alignment = get_arc_alignment(parse_graph, "zzzzzzzzzzzz")
    assert alignment is None


def test_segment_alignment_with_nfs(parse_graph):
    alignment = get_arc_alignment(parse_graph, "awhahthvhitoha")
    assert alignment is not None
    segments = segment_alignment(alignment)

    stages = [s["stage"] for s in segments]
    assert stages == ["Prefix", "Root", "NFS", "AspectClass", "Aspect", "Tense"]

    root_seg = next(s for s in segments if s["stage"] == "Root")
    assert root_seg["surface"] == "whahthvh"

    nfs_seg = next(s for s in segments if s["stage"] == "NFS")
    assert nfs_seg["surface"] == "it"
    assert "[NFS=AMB]" in nfs_seg["info"]

    hyphenated = format_segmentation(segments)
    assert hyphenated == "a-whahthvh-it-o-h-a"
    assert "".join(s["surface"] for s in segments) == "awhahthvhitoha"


def test_segment_alignment_with_nfs_at_long(parse_graph):
    alignment = get_arc_alignment(parse_graph, "atahwatvhitoha")
    assert alignment is not None
    segments = segment_alignment(alignment)

    stages = [s["stage"] for s in segments]
    assert stages == ["Prefix", "Root", "NFS", "AspectClass", "Aspect", "Tense"]

    hyphenated = format_segmentation(segments)
    assert hyphenated == "a-tahwatvh-it-o-h-a"
    assert "".join(s["surface"] for s in segments) == "atahwatvhitoha"



def test_cli_argument_execution(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["segment", "katateka"])
    segment_main()
    captured = capsys.readouterr()
    assert "WORD: katateka" in captured.out
    assert ("Segmentation: k-atat-e-k-a" in captured.out or "Segmentation: ka-tat-e-k-a" in captured.out)
    assert "Arc Alignment:" in captured.out
    assert "Parses (total:" in captured.out


def test_cli_interactive_execution(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["segment"])
    monkeypatch.setattr("sys.stdin", io.StringIO("katateka\n\n"))
    segment_main()
    captured = capsys.readouterr()
    assert "Interactive segmentation & parsing" in captured.out
    assert "SEGMENT:" in captured.out
    assert ("Segmentation: k-atat-e-k-a" in captured.out or "Segmentation: ka-tat-e-k-a" in captured.out)
    assert "Parses (total:" in captured.out

