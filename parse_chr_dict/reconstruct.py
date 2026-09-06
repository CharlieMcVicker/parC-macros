from typing import Any, Optional
from parse_chr_dict.create_aspect_class_csv import respell_consonants
from parse_chr_dict.h_alternation import (
    is_h_alternation_trigger,
    validate_h_alternation_trigger,
)
from parC.grammar.paradigm_compilation import inflect

_INFLECT_CACHE: dict[tuple[str, frozenset[tuple[str, str]], str, bool, bool], list[str]] = {}


def build_inplace_tag_str(root: str, feature_values: dict[str, str]) -> str:
    pref = feature_values.get("prefix_class", "")
    pro = feature_values.get("pronominal", "")
    h_alt = feature_values.get("h_alt_tag", "")
    asp_cls = feature_values.get("aspect_class", "")
    var = feature_values.get("variant", 1)
    if isinstance(var, str):
        var = int(var) if var.isdigit() else 1
    asp = feature_values.get("aspect", "")
    tense = feature_values.get("tense", "")

    parts: list[str] = []
    if feature_values.get("translocutive") in ("+", True, "[WI]"):
        parts.append("[WI]")
    dist = feature_values.get("distributive")
    if dist:
        if dist in ("de", "di"):
            parts.append(f"[DIST={dist}]")
        elif (
            feature_values.get("tense") in ("infinitive", "immediate")
            or feature_values.get("aspect") in ("infinitive", "immediate")
            or pro.startswith("2")
        ):
            parts.append("[DIST=di]")
        else:
            parts.append("[DIST=de]")
    if pref:
        parts.append(f"[PrefixClass={pref}]")
    if pro:
        parts.append(f"[Pro={pro}]")
    if h_alt:
        parts.append(h_alt)
    elif not any(root.startswith(t) for t in ("[H_", "[TEMP")):
        parts.append("[H_alt=none]")
    import re
    clean_root = re.sub(r"\[(Pro|Aspect|Tense)\]", "", root)
    parts.append(clean_root)
    if asp_cls:
        parts.append(f"[AspectClass={asp_cls}]")
    if var > 1:
        parts.append(f"[Variant={var}]")
    if asp:
        parts.append(f"[Aspect={asp}]")
    if tense:
        parts.append(f"[Tense={tense}]")
    return "".join(parts)


def inflect_inplace_string(tag_str: str) -> list[str]:
    import pynini
    from parC.grammar.acceptor_compilation import fsm_strings, word_fsa
    from parse_chr_dict.parse import get_inflect_graph
    inflect_fst = get_inflect_graph()
    out_fst = pynini.compose(word_fsa(tag_str), inflect_fst)
    out_proj = pynini.project(out_fst, "output").optimize()
    return fsm_strings(out_proj, strip_all_tags=True)


def memoized_inflect(
    root: str,
    feature_values: dict[str, str] | frozenset[tuple[str, str]] | set[tuple[str, str]],
    name: str = "verb",
    open_root: bool = True,
    infer_lexical_features: bool = True,
) -> list[str]:
    """
    Memoized wrapper around inflect() to avoid repeated FST operations
    for identical root and feature configurations. Supports both in-place
    and legacy grammars.
    """
    if isinstance(feature_values, dict):
        feat_key = frozenset(feature_values.items())
    elif isinstance(feature_values, (set, frozenset)):
        feat_key = frozenset(feature_values)
    else:
        feat_key = frozenset(feature_values)

    cache_key = (root, feat_key, name, open_root, infer_lexical_features)
    if cache_key in _INFLECT_CACHE:
        return _INFLECT_CACHE[cache_key]

    from parse_chr_dict.parse import is_inplace_grammar
    if is_inplace_grammar():
        try:
            tag_str = build_inplace_tag_str(root, dict(feat_key))
            res = inflect_inplace_string(tag_str)
        except Exception:
            res = []
    else:
        legacy_features = {
            k: v for k, v in dict(feat_key).items()
            if v and k != "h_alt_tag" and not (k == "variant" and str(v) in ("", "1"))
        }
        try:
            res = inflect(
                root,
                feature_values=legacy_features,
                name=name,
                open_root=open_root,
                infer_lexical_features=infer_lexical_features,
            )
        except (ValueError, KeyError):
            res = []

    _INFLECT_CACHE[cache_key] = res
    return res


def validate_hypothesis(
    hypothesis: Any,
    row: dict,
    entry_type: Any,
    compiler: Optional[Any] = None,
) -> bool:
    """
    Validates a LexicalVerb / DerivationHypothesis against all non-empty forms in a row.
    Returns True if every non-empty form in the row reconstructs to the exact surface form.
    Fails fast immediately if any form fails.
    """
    from parse_chr_dict.types import VerbForm, VERB_FORMS_BY_NAME, VERB_ENTRY_TYPES_BY_NAME

    if isinstance(entry_type, str):
        if entry_type in VERB_ENTRY_TYPES_BY_NAME:
            entry_type = VERB_ENTRY_TYPES_BY_NAME[entry_type]

    forms = getattr(entry_type, "forms", ())
    for form_item in forms:
        if isinstance(form_item, VerbForm):
            form = form_item
        elif isinstance(form_item, str):
            form = VERB_FORMS_BY_NAME.get(form_item)
        else:
            continue

        if not form:
            continue

        reference_form = row.get(form.corpus_key)
        if reference_form and " " not in reference_form:
            if not hypothesis.validate_form(form, reference_form):
                return False
    return True


def reconstruct_row(
    row: dict,
    entry_type: Any,
    lexical_fields: Optional[list[str]] = None,
    compiler: Optional[Any] = None,
) -> list[Any]:
    from parse_chr_dict.types import VerbMetadata, LexicalVerb

    passing_metas: list[VerbMetadata] = []
    entry_type_name = getattr(entry_type, "name", str(entry_type))
    for meta in VerbMetadata.all_combinations(entry_type=entry_type_name):
        hypothesis = LexicalVerb(
            h_root=row.get("h_root", ""),
            h_alt_tag=row.get("h_alt_tag", ""),
            prefix_class=row.get("prefix_class", ""),
            aspect_class=row.get("aspect_class", ""),
            tense_present_class=row.get("tense_present_class", ""),
            set_a=meta.is_set_a,
            plural=meta.is_plural,
            animate_objects=meta.animate_objects,
        )
        if validate_hypothesis(hypothesis, row, entry_type, compiler=compiler):
            passing_metas.append(meta)
    return passing_metas

