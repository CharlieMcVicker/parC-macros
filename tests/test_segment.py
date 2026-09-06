import subprocess
import sys
import pytest
from parse_chr_dict.parse import get_parse_graph
from parse_chr_dict.segment import (
    get_arc_alignment,
    segment_alignment,
    format_segmentation,
    process_word,
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

    assert "[PrefixClass=vowel_stem]" in out_symbols
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
    assert hyphenated == "k-atat-e-k-a"

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


def test_cli_argument_execution():
    res = subprocess.run(
        [sys.executable, "-m", "parse_chr_dict.segment", "katateka"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "WORD: katateka" in res.stdout
    assert "Segmentation: k-atat-e-k-a" in res.stdout
    assert "Arc Alignment:" in res.stdout
    assert "Parses (total:" in res.stdout


def test_cli_interactive_execution():
    proc = subprocess.Popen(
        [sys.executable, "-m", "parse_chr_dict.segment"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate("katateka\n\n")
    assert proc.returncode == 0
    assert "Interactive segmentation & parsing" in stdout
    assert "SEGMENT:" in stdout
    assert "Segmentation: k-atat-e-k-a" in stdout
    assert "Parses (total:" in stdout
