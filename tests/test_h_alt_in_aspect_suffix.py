from parse_chr_dict.parse import parse
import pytest

CASES = [("[PrefixClass=a_stem][Pro=1sg.A][H_alt=glot]atit[AspectClass=ih-vh][Aspect=present][Tense=present_a]", "katiti'a")]

# parameterized by cases
@pytest.mark.parametrize(("target", "word"), CASES)
def test_foo(target, word):
    parses = parse(word)
    assert f"[BOW]{target}[EOW]" in parses, f"Expected [BOW]{target}[EOW] in parses, but got {parses}"
    