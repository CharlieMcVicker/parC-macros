import functools
import os
import re
from pathlib import Path
from typing import Any, Iterable

# Ensure YAML_DIR defaults to chr-generated
if "YAML_DIR" not in os.environ:
    repo_root = Path(__file__).parent.parent.resolve()
    gen_dir = repo_root / "chr-generated"
    if gen_dir.exists():
        os.environ["YAML_DIR"] = str(gen_dir)
        try:
            from parC.constants import set_yaml_dir
            set_yaml_dir(str(gen_dir))
        except ImportError:
            pass

import pynini

from parC.grammar.acceptor_compilation import fsm_strings
from parC.grammar.paradigm_compilation import (
    fsa,
    get_open_parse_graph,
    inflect,
    word_fsa,
)
from parse_chr_dict.acceptors import (
    get_cascade_domain_acceptor,
    get_default_symbol_table,
)

PARSE_GRAPH = None
INFLECT_GRAPH = None


def is_inplace_grammar() -> bool:
    """Detects whether the active grammar uses in-place morpheme tags."""
    yaml_dir = os.environ.get("YAML_DIR", "")
    if "chr-generated" in str(yaml_dir) or "inplace" in str(yaml_dir):
        return True
    try:
        from parC.constants import get_yaml_dir

        yd = Path(get_yaml_dir())
        if "chr-generated" in str(yd) or "inplace" in yd.name or "inplace" in str(yd):
            return True
        paradigm_path = yd / "Morphotactics" / "Paradigm" / "verb.yaml"
        if paradigm_path.exists():
            content = paradigm_path.read_text(encoding="utf-8")
            if "<PrefixClass>" in content or "<AspectClass>" in content:
                return True
    except Exception:
        pass
    return False


def get_parse_graph():
    global PARSE_GRAPH
    if PARSE_GRAPH is not None:
        return PARSE_GRAPH
    raw_parse = get_open_parse_graph(
        "verb", infer_lexical_features=True, non_deterministic_cleanup=True
    )
    if is_inplace_grammar():
        syms = raw_parse.output_symbols() or get_default_symbol_table()
        domain_acceptor = get_cascade_domain_acceptor(syms=syms)
        PARSE_GRAPH = pynini.compose(raw_parse, domain_acceptor).optimize()
        if syms is not None:
            if raw_parse.input_symbols() is not None:
                PARSE_GRAPH.set_input_symbols(raw_parse.input_symbols())
            PARSE_GRAPH.set_output_symbols(syms)
    else:
        PARSE_GRAPH = raw_parse
    return PARSE_GRAPH


def parse(surface: str, labels: list[tuple[str, str]] = None) -> list[str]:
    global PARSE_GRAPH
    if PARSE_GRAPH is None:
        PARSE_GRAPH = get_parse_graph()

    # Let's parse the surface form cant-o_a
    if labels is None:
        labels = []
    surface_fsa = word_fsa(surface)
    for feat, value in sorted(labels, key=lambda l: l[0]):
        surface_fsa = pynini.concat(surface_fsa, fsa(feature_tag(feat, value)))

    output_lattice_with_tag = pynini.compose(surface_fsa, PARSE_GRAPH).optimize()
    output_lattice_with_tag = pynini.project(
        output_lattice_with_tag, project_type="output"
    )
    output_lattice_with_tag = pynini.rmepsilon(output_lattice_with_tag).optimize()
    if output_lattice_with_tag.properties(pynini.CYCLIC, True) == pynini.CYCLIC:
        output_lattice_with_tag = pynini.shortestpath(output_lattice_with_tag, nshortest=5000).optimize()
    return fsm_strings(output_lattice_with_tag, strip_all_tags=False)




def get_inflect_graph():
    global INFLECT_GRAPH
    if INFLECT_GRAPH is not None:
        return INFLECT_GRAPH
    from parC.grammar.paradigm_compilation import get_open_inflect_graph
    if is_inplace_grammar():
        INFLECT_GRAPH = get_open_inflect_graph("verb", infer_lexical_features=False)
    else:
        INFLECT_GRAPH = get_open_inflect_graph("verb", infer_lexical_features=True, non_deterministic_cleanup=False)
    return INFLECT_GRAPH


SLOT_NAME_TO_INPLACE_TAG: dict[str, str] = {
    "prefix_class": "PrefixClass",
    "pronominal": "Pro",
    "h_alt_tag": "H_alt",
    "aspect_class": "AspectClass",
    "variant": "Variant",
    "aspect": "Aspect",
    "tense_present_class": "TenseClass",
    "tense": "Tense",
}


def feature_tag(feature: str, value: str) -> str:
    if is_inplace_grammar():
        slot = SLOT_NAME_TO_INPLACE_TAG.get(feature, feature)
        return f"[{slot}={value}]"
    return f"[{feature}={value}]"


from parse_chr_dict.types import (
    ParseData,
    InPlaceParseConfig,
    VerbTemplate,
    AspectVariants,
    VerbMetadata,
    LexicalVerb,
)

INPLACE_SLOT_TAG_MAP: dict[str, str] = {
    "PrefixClass": "prefix_class",
    "Pro": "pronominal",
    "H_alt": "h_alt_tag",
    "H_ALT": "h_alt_tag",
    "AspectClass": "aspect_class",
    "Variant": "variant",
    "Aspect": "aspect",
    "TenseClass": "tense_present_class",
    "Tense": "tense",
}

_READ_LABELS_CACHE: dict[str, tuple[str, dict[str, str]]] = {}


_READ_INPLACE_PARSE_CACHE: dict[str, ParseData] = {}


def read_inplace_parse(s: str) -> ParseData:
    """
    Parses an in-place morpheme parse string into a ParseData (InPlaceParseConfig) object.
    Uses bracket-depth tracking to safely handle nested brackets (e.g. [AspectClass=become[inf2]]).
    Slot tags ([PrefixClass=...], [Pro=...], [AspectClass=...], etc.) and PPP tags ([WI], [DIST])
    are extracted as metadata; any internal root mutation tags (like [H_NONE]) remain in the root.
    Memoized directly via _READ_INPLACE_PARSE_CACHE.
    """
    cached = _READ_INPLACE_PARSE_CACHE.get(s)
    if cached is not None:
        return cached

    clean_s = s
    if clean_s.startswith("[BOW]"):
        clean_s = clean_s[5:]
    eow_idx = clean_s.find("[EOW]")
    if eow_idx != -1:
        clean_s = clean_s[:eow_idx]

    tokens: list[str] = []
    root_parts: list[str] = []
    i = 0
    n = len(clean_s)
    root_start = -1

    while i < n:
        if clean_s[i] == "[":
            if root_start != -1:
                root_parts.append(clean_s[root_start:i])
                root_start = -1
            depth = 1
            start = i
            i += 1
            while i < n and depth > 0:
                ch = clean_s[i]
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                i += 1
            tok = clean_s[start:i]
            inner = tok[1:-1]
            eq_idx = inner.find("=")
            if eq_idx != -1 and inner[:eq_idx] in INPLACE_SLOT_TAG_MAP:
                tokens.append(tok)
            elif tok in ("[WI]", "[DIST]", "[DIST=de]", "[DIST=di]") or tok.startswith("[DIST="):
                tokens.append(tok)
            else:
                # Internal root tag (e.g. [H_NONE], [H_GLOT], [H_DROP]) or phonological tag
                tokens.append(tok)
                root_parts.append(tok)
        else:
            if root_start == -1:
                root_start = i
            i += 1

    if root_start != -1:
        root_parts.append(clean_s[root_start:n])

    prefix_class = ""
    pronominal = ""
    aspect_class = ""
    variant = 1
    aspect = ""
    tense_present_class = ""
    tense = ""
    prepronominal_prefixes: list[str] = []
    h_alt_tag = ""

    for tok in tokens:
        inner = tok[1:-1]
        eq_idx = inner.find("=")
        if eq_idx != -1:
            k = inner[:eq_idx]
            v = inner[eq_idx + 1 :]
            if k == "PrefixClass":
                prefix_class = v
            elif k == "Pro":
                pronominal = v
            elif k == "AspectClass":
                aspect_class = v
            elif k == "Variant":
                variant = int(v) if v.isdigit() else 1
            elif k == "Aspect":
                aspect = v
            elif k == "TenseClass":
                tense_present_class = v
            elif k == "Tense":
                tense = v
            elif k == "DIST":
                prepronominal_prefixes.append(tok)
            elif k in ("H_alt", "H_ALT"):
                h_alt_tag = tok
        else:
            if tok in ("[WI]", "[DIST]"):
                prepronominal_prefixes.append(tok)
            elif tok.startswith("[H_") or tok.startswith("[H_alt=") or tok.startswith("[TEMP"):
                h_alt_tag = tok

    res = ParseData(
        root="".join(root_parts),
        prefix_class=prefix_class,
        pronominal=pronominal,
        h_alt_tag=h_alt_tag,
        aspect_class=aspect_class,
        variant=variant,
        aspect=aspect,
        tense_present_class=tense_present_class,
        tense=tense,
        prepronominal_prefixes=tuple(prepronominal_prefixes),
        raw_tokens=tuple(tokens),
    )
    _READ_INPLACE_PARSE_CACHE[s] = res
    return res


def read_labels(s: str):
    cached = _READ_LABELS_CACHE.get(s)
    if cached is not None:
        form, labels_dict = cached
        return form, dict(labels_dict)

    # s is a str like [BOW]foo[EOW][label=value][label2=value2]
    eow_idx = s.find("[EOW]")
    if eow_idx == -1 or not s.startswith("[BOW]"):
        _READ_LABELS_CACHE[s] = (s, {})
        return s, {}

    # Detect in-place morpheme tags
    form_candidate = s[5:eow_idx]
    if "[" in form_candidate and ("PrefixClass=" in form_candidate or "AspectClass=" in form_candidate or "Pro=" in form_candidate):
        cfg = read_inplace_parse(s)
        form = cfg.root
        labels_dict = cfg.to_labels_dict()
        _READ_LABELS_CACHE[s] = (form, labels_dict)
        return form, dict(labels_dict)

    # Legacy trailing-tag format
    form = form_candidate
    labels_str = s[eow_idx + 5 :]

    labels_dict = {}
    if labels_str and labels_str.startswith("[") and labels_str.endswith("]"):
        for chunk in labels_str[1:-1].split("]["):
            eq_idx = chunk.find("=")
            if eq_idx != -1:
                labels_dict[chunk[:eq_idx]] = chunk[eq_idx + 1 :]

    _READ_LABELS_CACHE[s] = (form, labels_dict)
    return form, dict(labels_dict)


_SURFACE_PARSE_CACHE: dict[tuple, list[str]] = {}
_SURFACE_FSA_CACHE: dict[str, pynini.Fst] = {}
_PARSE_DATA_CACHE: dict[str, ParseData] = {}
_SPECIALIZED_PARSE_GRAPHS: dict[tuple[bool, str], pynini.Fst] = {}
_ROOT_FILTER_CACHE: dict[frozenset[str], pynini.Fst] = {}


def get_specialized_parse_graph(form: Any, is_stative: bool = False) -> pynini.Fst:
    """
    Returns an optimized FST specialized for a specific VerbForm and entry type category
    (Eventful vs. Stative), restricting the output domain to only licensed aspect class,
    aspect, tense, and pronominal tags.
    """
    form_name = getattr(form, "name", str(form))
    key = (is_stative, form_name)
    if key in _SPECIALIZED_PARSE_GRAPHS:
        return _SPECIALIZED_PARSE_GRAPHS[key]

    base_graph = get_parse_graph()
    if not is_inplace_grammar():
        _SPECIALIZED_PARSE_GRAPHS[key] = base_graph
        return base_graph

    syms = base_graph.output_symbols() or get_default_symbol_table()
    if syms is None:
        _SPECIALIZED_PARSE_GRAPHS[key] = base_graph
        return base_graph
    all_syms = [syms.find(i) for i in range(1, syms.num_symbols())]
    sigma = pynini.union(*[pynini.accep(s, token_type=syms) for s in all_syms]).optimize()
    sigma_star = sigma.star.optimize()

    # 1. Aspect Class filter (stative vs eventful)
    aspect_classes = [s for s in all_syms if s.startswith("[AspectClass=")]
    if is_stative:
        target_asp_classes = [c for c in aspect_classes if c.startswith("[AspectClass=stative")]
    else:
        target_asp_classes = [c for c in aspect_classes if not c.startswith("[AspectClass=stative")]

    if target_asp_classes:
        asp_cls_fsa = pynini.union(*[pynini.accep(c, token_type=syms) for c in target_asp_classes]).optimize()
        f_asp_cls = pynini.concat(sigma_star, pynini.concat(asp_cls_fsa, sigma_star)).optimize()
    else:
        f_asp_cls = sigma_star

    # 2. Pronominal filter
    from parse_chr_dict.types import filter_pronominals
    person = getattr(form, "person", None)
    allows_set_a = getattr(form, "allows_set_a", True)
    p_set = "B" if not allows_set_a else None
    pro_tags = [f"[Pro={t}]" for t in filter_pronominals(person=person, pronoun_set=p_set)]
    valid_pros = [t for t in pro_tags if syms.member(t)]
    if valid_pros:
        pro_fsa = pynini.union(*[pynini.accep(t, token_type=syms) for t in valid_pros]).optimize()
        f_pro = pynini.concat(sigma_star, pynini.concat(pro_fsa, sigma_star)).optimize()
    else:
        f_pro = sigma_star

    # 3. Aspect tag filter
    aspect = getattr(form, "aspect", "")
    asp_tag = f"[Aspect={aspect}]"
    if aspect and syms.member(asp_tag):
        f_asp = pynini.concat(sigma_star, pynini.concat(pynini.accep(asp_tag, token_type=syms), sigma_star)).optimize()
    else:
        f_asp = sigma_star

    # 4. Tense tag filter
    tense = getattr(form, "tense", "")
    tense_tag = f"[Tense={tense}]"
    if tense and syms.member(tense_tag):
        f_tense = pynini.concat(sigma_star, pynini.concat(pynini.accep(tense_tag, token_type=syms), sigma_star)).optimize()
    else:
        f_tense = sigma_star

    filter_fsa = pynini.intersect(
        pynini.intersect(f_asp_cls, f_pro),
        pynini.intersect(f_asp, f_tense),
    ).optimize()

    specialized_graph = pynini.compose(base_graph, filter_fsa).optimize()
    _SPECIALIZED_PARSE_GRAPHS[key] = specialized_graph
    return specialized_graph


def build_root_filter_fsa(allowed_roots: Iterable[str]) -> pynini.Fst | None:
    """
    Constructs an optimized FSA filter that restricts the output of a parse graph to
    match only roots in allowed_roots.
    Boundary structure: sigma* + [H_alt=...] + root_union + [AspectClass=...] + sigma*
    """
    if not is_inplace_grammar():
        return None
    key = frozenset(allowed_roots)
    if not key:
        return None
    if key in _ROOT_FILTER_CACHE:
        return _ROOT_FILTER_CACHE[key]

    base_graph = get_parse_graph()
    syms = base_graph.output_symbols() or get_default_symbol_table()
    if syms is None:
        return None

    all_syms = [syms.find(i) for i in range(1, syms.num_symbols())]
    sigma = pynini.union(*[pynini.accep(s, token_type=syms) for s in all_syms]).optimize()
    sigma_star = sigma.star.optimize()

    # Pre-root boundary tags: all [H_alt=...] tags
    h_alt_tags = [s for s in all_syms if s.startswith("[H_alt=")]
    if not h_alt_tags:
        return None
    h_alt_fsa = pynini.union(*[pynini.accep(t, token_type=syms) for t in h_alt_tags if syms.member(t)]).optimize()

    # Post-root boundary tags: all [AspectClass=...] tags
    asp_tags = [s for s in all_syms if s.startswith("[AspectClass=")]
    if not asp_tags:
        return None
    asp_fsa = pynini.union(*[pynini.accep(t, token_type=syms) for t in asp_tags if syms.member(t)]).optimize()

    root_fsas = []
    for r in key:
        clean_r = get_just_root(r) if "[" in r else r
        if clean_r and all(syms.member(c) for c in clean_r):
            chars = [pynini.accep(c, token_type=syms) for c in clean_r]
            root_fsas.append(functools.reduce(pynini.concat, chars))

    if not root_fsas:
        return None

    root_fsa = pynini.union(*root_fsas).optimize()

    exact_root_filter = pynini.concat(
        sigma_star,
        pynini.concat(
            h_alt_fsa,
            pynini.concat(root_fsa, pynini.concat(asp_fsa, sigma_star))
        )
    ).optimize()

    _ROOT_FILTER_CACHE[key] = exact_root_filter
    return exact_root_filter


def parse_surface(
    surface: str,
    parse_graph: pynini.Fst | None = None,
    form: Any | None = None,
    is_stative: bool = False,
    allowed_roots: Iterable[str] | None = None,
) -> list[str]:
    """
    Parses a bare surface form by executing pynini.compose(linear_surface_fsa, parse_graph).
    When form is provided, uses the specialized, domain-restricted FST for that form
    and entry type category (Eventful vs. Stative).
    When allowed_roots is provided, constrains the parse graph output to only accept
    those roots.
    Memoized by (surface, id(graph), frozenset(allowed_roots) if allowed_roots else None).
    """
    if not surface:
        return []

    if form is not None and parse_graph is None:
        graph = get_specialized_parse_graph(form, is_stative=is_stative)
    elif parse_graph is not None:
        graph = parse_graph
    else:
        graph = get_parse_graph()

    roots_key = frozenset(allowed_roots) if allowed_roots else None
    cache_key = (surface, id(graph), roots_key)
    if cache_key in _SURFACE_PARSE_CACHE:
        return _SURFACE_PARSE_CACHE[cache_key]

    if surface in _SURFACE_FSA_CACHE:
        surface_fsa = _SURFACE_FSA_CACHE[surface]
    else:
        surface_fsa = word_fsa(surface)
        _SURFACE_FSA_CACHE[surface] = surface_fsa

    output_lattice = pynini.compose(surface_fsa, graph).optimize()
    if roots_key and is_inplace_grammar():
        root_filter = build_root_filter_fsa(roots_key)
        if root_filter is not None:
            output_lattice = pynini.compose(output_lattice, root_filter).optimize()
    output_lattice = pynini.project(output_lattice, project_type="output")
    output_lattice = pynini.rmepsilon(output_lattice).optimize()
    if output_lattice.properties(pynini.CYCLIC, True) == pynini.CYCLIC:
        output_lattice = pynini.shortestpath(output_lattice, nshortest=2000).optimize()

    results = fsm_strings(output_lattice, strip_all_tags=False)
    _SURFACE_PARSE_CACHE[cache_key] = results
    return results


def parse_string_to_parse_data(p: str) -> ParseData:
    """Converts a raw parse string (in-place morphemes or legacy trailing tags) to ParseData."""
    cached = _PARSE_DATA_CACHE.get(p)
    if cached is not None:
        return cached

    if "[" in p and ("PrefixClass=" in p or "AspectClass=" in p or "Pro=" in p):
        res = read_inplace_parse(p)
        _PARSE_DATA_CACHE[p] = res
        return res

    form, labels = read_labels(p)
    var_raw = labels.get("variant", 1)
    var = int(var_raw) if str(var_raw).isdigit() else 1
    h_alt_tag = labels.get("h_alt_tag", "")
    if not h_alt_tag:
        for tag in (
            "[H_alt=drop]",
            "[H_alt=glot]",
            "[H_alt=lat]",
            "[H_alt=vowel]",
            "[H_alt=none]",
            "[H_DROP]",
            "[H_GLOT]",
            "[H_LAT]",
            "[H_VOWEL]",
            "[H_NONE]",
        ):
            if tag in form:
                h_alt_tag = tag
                break
    res = ParseData(
        root=form,
        prefix_class=labels.get("prefix_class", ""),
        pronominal=labels.get("pronominal", ""),
        h_alt_tag=h_alt_tag,
        aspect_class=labels.get("aspect_class", ""),
        variant=var,
        aspect=labels.get("aspect", ""),
        tense_present_class=labels.get("tense_present_class", ""),
        tense=labels.get("tense", ""),
    )
    _PARSE_DATA_CACHE[p] = res
    return res


def str_to_lexical_hashable(parse_str: str, lexical_features: set[str]):
    root, labels = read_labels(parse_str)
    label_tuple = tuple(
        sorted(
            [(k, v) for k, v in labels.items() if k in lexical_features],
            key=lambda x: x[0],
        )
    )
    return root, label_tuple


def parses_by_form(
    forms: Iterable[tuple[str, list[tuple[str, str]]]], lexical_features: set[str]
):
    for surface, constraints in forms:
        if not surface:
            continue
        strings = parse(surface, labels=constraints)
        lexicals = set(
            str_to_lexical_hashable(s, lexical_features=lexical_features)
            for s in strings
        )
        yield surface, lexicals


def get_roots_for_parses(lexicals: list[set[tuple[tuple[str, str], ...]]]):
    possible_lexical_roots: set = None
    for form_lexicals in lexicals:
        if possible_lexical_roots is None:
            possible_lexical_roots = form_lexicals
        else:
            possible_lexical_roots = possible_lexical_roots.intersection(form_lexicals)

    return possible_lexical_roots if possible_lexical_roots else set()

def get_just_root(s: str):
    # s is something like [PrefixClass=a_stem][Pro=3sg.A]tateka[AspectClass=a][Aspect=completive][TenseClass=a_present][Tense=immediate]
    # don't use a regexp, just read [ and ] and find the part that isn't in brackets, keeping in mind there are several bracketed parts at the beginning and end
    chars = []
    bracket_depth = 0

    for ch in s:
        if ch == "[":
            bracket_depth += 1
            continue
        if ch == "]":
            if bracket_depth > 0:
                bracket_depth -= 1
            continue
        if bracket_depth == 0:
            chars.append(ch)

    return "".join(chars)


def main():
    import readline

    root = "atat"
    lexical = [
        # ("aspect_class", "go"),
        # ("prefix_class", "a_stem"),
        ("tense_present_class", "a_present"),
    ]
    inflectional = [
        # ("pronominal", "3sg.A"),
        # ("aspect", "present"),
        ("tense", "present"),
        # ("translocutive", "+"),
        # ("distributive", "-"),
        # ("partitive", "+"),
    ]

    # words = inflect(
    #     "[BOW][Pro]atat[Aspect][Tense][EOW][aspect_class=go][prefix_class=a_stem][tense_present_class=a_present][aspect=present][pronominal=3sg.A][rules=+][tense=present]"
    # )
    # print(words)

    print("interactive parsing - newline to quit, . to flip modes")
    MODE = "PARSE"
    while True:
        surface = input(f"{MODE}: ").strip()
        if not surface:
            break

        # if MODE == "INFLECT":
        #     if surface == ".":
        #         MODE = "PARSE"
        #         continue
        #     forms = inflect(surface, [], [])
        #     for p in forms:
        #         print("\t", p)

        elif MODE == "PARSE":
            if surface == ".":
                MODE = "INFLECT"
                continue
            parses = parse(surface)
            groups = {}
            for p in parses:
                parsed_word, labels = p.split("[EOW]")
                parsed_word = parsed_word[5:] # cut off [BOW]
                root = get_just_root(parsed_word)
                if not root in groups:
                    groups[root] = []
                groups[root].append(parsed_word)
            root_list = sorted(groups.keys(), key=lambda x: len(x))
            for root in root_list[:10]:
                print("\t", root)
                for parsed_word in groups[root][:10]:
                    print("\t\t",parsed_word)
            print(len(parses), "parses found with", len(groups), "distinct roots")


if __name__ == "__main__":
    main()
