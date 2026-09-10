import pytest

from parse_chr_dict.parse import parse


cases = [
    ("awhahthvhitoha", "AMB"),
    ("tsiwahthvhitoha", "AMB"),
    ("awhahthvhitoho'i", "AMB"),
    ("uwhahthvhitolv'i", "AMB"),
    ("hiwahthvhita", "AMB"),
    ("uhwahthvhitahsti", "AMB"),
]

@pytest.mark.parametrize("surface, expected_nfs", cases)
def test_nfs_parsing(surface, expected_nfs):
    parses = parse(surface)
    assert any(f"[NFS={expected_nfs}]" in p for p in parses)


def test_nfs_derivation_entry_208():
    from parse_chr_dict.derive import derive_hypotheses_for_forms
    from parse_chr_dict.types import EVENTFUL

    row = {
        "corpus_id": "208",
        "entry_no": "214",
        "definition": "he/she is visiting him/her",
        "present": "awhahthvhitoha",
        "present_1sg": "tsiwahthvhitoha",
        "imperfective": "awhahthvhitoho'i",
        "perfective": "uwhahthvhitolv'i",
        "imperative": "hiwahthvhita",
        "infinitive": "uwhahthvhitahsti",
    }
    forms = [
        (row[form.corpus_key], form)
        for form in EVENTFUL.forms
        if row.get(form.corpus_key) and " " not in row[form.corpus_key]
    ]
    hyps = derive_hypotheses_for_forms(forms, entry_type=EVENTFUL)
    roots = {h.h_root for h in hyps}
    assert "whahthvh[NFS=AMB]" in roots