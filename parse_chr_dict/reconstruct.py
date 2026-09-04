from dataclasses import dataclass
from typing import Optional
from parse_chr_dict.create_aspect_class_csv import respell_consonants
from parse_chr_dict.h_alternation import (
    is_h_alternation_trigger,
    validate_h_alternation_trigger,
)
from parse_chr_dict.meta_label_compiler import (
    FORMS_TO_PARSE,
    EntryTypeSpec as EntryType,
    FormParsingSpec as FormParsing,
    MetaConstraintCompiler,
    filter_pronominals,
)
from parC.grammar.paradigm_compilation import inflect

FORMS_BY_NAME: dict[str, FormParsing] = {p.name: p for p in FORMS_TO_PARSE}

_INFLECT_CACHE: dict[tuple[str, frozenset[tuple[str, str]], str, bool, bool], list[str]] = {}
_PRONOMINAL_CANDIDATE_CACHE: dict[tuple[bool, bool, bool, str, bool], list[str]] = {}


def build_inplace_tag_str(root: str, feature_values: dict[str, str]) -> str:
    pref = feature_values.get("prefix_class", "")
    pro = feature_values.get("pronominal", "")
    h_alt = feature_values.get("h_alt_tag", "")
    asp_cls = feature_values.get("aspect_class", "")
    var = feature_values.get("variant", 1)
    if isinstance(var, str):
        var = int(var) if var.isdigit() else 1
    asp = feature_values.get("aspect", "")
    tense_cls = feature_values.get("tense_present_class", "")
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
    if tense_cls:
        parts.append(f"[TenseClass={tense_cls}]")
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
        try:
            res = inflect(
                root,
                feature_values=dict(feat_key),
                name=name,
                open_root=open_root,
                infer_lexical_features=infer_lexical_features,
            )
        except (ValueError, KeyError):
            res = []

    _INFLECT_CACHE[cache_key] = res
    return res


@dataclass
class MetaLabelCombination:
    """Represents a combination of meta-labels for pronominal reconstruction."""
    set_a: bool
    plural: bool
    animate_objects: bool

    @property
    def meta_labels(self) -> list[str]:
        labels = []
        if self.set_a:
            labels.append("[PRONOUN_SET=A]")
        if self.plural:
            labels.append("[PLURAL=TRUE]")
        else:
            labels.append("[PLURAL=FALSE]")
        if self.animate_objects:
            labels.append("[OBJECT_ANIMACY=ANIMATE]")
        else:
            labels.append("[OBJECT_ANIMACY=INANIMATE]")
        return labels

    def get_pronominal_candidates(self, person: str, allow_set_a: bool) -> list[str]:
        key = (self.set_a, self.plural, self.animate_objects, person, allow_set_a)
        cached = _PRONOMINAL_CANDIDATE_CACHE.get(key)
        if cached is not None:
            return cached

        pronoun_set = "A" if self.set_a and allow_set_a else "B"
        if self.animate_objects and person in ["1st", "2nd"]:
            tags = filter_pronominals(person=person, pronoun_set="transitive")
            candidates = list(tags) if tags else [f"{person[0]}sg>3sg"]
            if person == "2nd":
                candidates.append(f"2sg.{pronoun_set}")
            _PRONOMINAL_CANDIDATE_CACHE[key] = candidates
            return candidates

        if self.plural:
            if person == "3rd":
                candidates = [f"3ns.{pronoun_set}", f"3dl.{pronoun_set}"]
            elif person == "1st":
                candidates = [f"Epl.{pronoun_set}", f"Edl.{pronoun_set}", f"1pl.{pronoun_set}", f"1dl.{pronoun_set}"]
            elif person == "2nd":
                candidates = [f"2pl.{pronoun_set}", f"2dl.{pronoun_set}"]
            else:
                candidates = [f"{person[0]}sg.{pronoun_set}"]
        else:
            candidates = [f"{person[0]}sg.{pronoun_set}"]

        _PRONOMINAL_CANDIDATE_CACHE[key] = candidates
        return candidates

    def get_pronominal(self, person: str, allow_set_a: bool) -> str:
        candidates = self.get_pronominal_candidates(person, allow_set_a)
        return candidates[0] if candidates else ("3sg.A" if self.set_a and allow_set_a else "3sg.B")

    @classmethod
    def all_combinations(cls):
        for plural in [True, False]:
            for set_a in [True, False]:
                for animate_objects in [False] if plural else [True, False]:
                    yield MetaLabelCombination(
                        set_a=set_a, plural=plural, animate_objects=animate_objects
                    )

    @classmethod
    def all_specs(cls):
        return cls.all_combinations()

    @classmethod
    def fieldnames(cls):
        return ["set_a", "plural", "animate_objects"]

    def validate(
        self,
        *,
        h_root: str,
        glottal_root: Optional[str] = None,
        reference_form: str,
        labels: dict[str, str],
        parsing_meta: FormParsing,
        compiler: Optional[MetaConstraintCompiler] = None,
        h_alt_tag: str = "",
        variant: int = 1,
    ) -> bool:
        if compiler is None:
            compiler = MetaConstraintCompiler()
        target_tuples = compiler.get_feature_tuples_from_meta([parsing_meta.meta_label_id])
        form_labels = dict(target_tuples)

        pronominal_candidates = self.get_pronominal_candidates(
            person=parsing_meta.person, allow_set_a=parsing_meta.allows_set_a
        )

        pref = labels.get("prefix_class")
        prefix_candidates = (pref, "k_a_stem") if pref == "a_stem" else (pref,)

        var = variant if variant > 1 else int(labels.get("variant", 1))

        from parse_chr_dict.parse import is_inplace_grammar
        is_inplace = is_inplace_grammar()

        for pro in pronominal_candidates:
            active_root = h_root
            if is_h_alternation_trigger(pro):
                active_h_alt = h_alt_tag or "[H_alt=none]"
            else:
                active_h_alt = "[H_alt=none]"

            for p_cand in prefix_candidates:
                all_labels = {
                    **labels,
                    **form_labels,
                    "pronominal": pro,
                    "prefix_class": p_cand,
                }
                if is_inplace:
                    all_labels["h_alt_tag"] = active_h_alt
                if var > 1:
                    all_labels["variant"] = str(var)
                elif "variant" in all_labels:
                    del all_labels["variant"]

                surface_forms = memoized_inflect(
                    active_root,
                    feature_values=all_labels,
                    name="verb",
                    open_root=True,
                    infer_lexical_features=True,
                )
                if reference_form in surface_forms:
                    return True
        return False


# Backward compatibility alias
ReconstructionSpec = MetaLabelCombination
ALL_META_COMBINATIONS = list(MetaLabelCombination.all_combinations())


def validate_hypothesis(
    hypothesis,
    row: dict,
    entry_type: EntryType,
    compiler: Optional[MetaConstraintCompiler] = None,
) -> bool:
    """
    Validates a LexicalVerb / DerivationHypothesis against all non-empty forms in a row.
    Returns True if every non-empty form in the row reconstructs to the exact surface form.
    Fails fast immediately if any form fails.
    """
    if compiler is None:
        compiler = MetaConstraintCompiler()

    meta_comb = hypothesis.to_meta_combination()
    labels = {
        **hypothesis.lexical_labels(),
        "rules": "+",
    }

    for form_name in entry_type.forms:
        parsing_meta = FORMS_BY_NAME.get(form_name)
        if not parsing_meta:
            continue
        reference_form = row.get(parsing_meta.corpus_key)
        if reference_form and " " not in reference_form:
            ref_surface = respell_consonants(reference_form)
            target_aspect = parsing_meta.corpus_key
            if hasattr(hypothesis, "metadata") and hasattr(hypothesis.metadata, "aspect_variants"):
                form_var = hypothesis.metadata.aspect_variants.get_variant(target_aspect)
            else:
                form_var = int(getattr(hypothesis, "present_variant", 1) or 1)

            form_labels = dict(labels)
            if form_var > 1:
                form_labels["variant"] = str(form_var)
            elif "variant" in form_labels:
                del form_labels["variant"]

            h_alt_val = getattr(hypothesis, "h_alt_tag", "")

            if not meta_comb.validate(
                h_root=hypothesis.h_root,
                reference_form=ref_surface,
                labels=form_labels,
                parsing_meta=parsing_meta,
                compiler=compiler,
                h_alt_tag=h_alt_val,
                variant=form_var,
            ):
                return False
    return True



def reconstruct_row(row, entry_type: EntryType, lexical_fields: list[str], compiler: Optional[MetaConstraintCompiler] = None):
    if compiler is None:
        compiler = MetaConstraintCompiler()
    passing_specs: list[MetaLabelCombination] = list()
    for spec in ALL_META_COMBINATIONS:
        valid = True
        for parsing in entry_type.forms:
            parsing_meta = FORMS_BY_NAME.get(parsing)
            if not parsing_meta:
                continue
            reference_form = row.get(parsing_meta.corpus_key)
            if reference_form:
                labels = {k: row[k] for k in lexical_fields if k in row}
                labels["rules"] = "+"
                if not spec.validate(
                    h_root=row["h_root"],
                    reference_form=reference_form,
                    labels=labels,
                    parsing_meta=parsing_meta,
                    compiler=compiler,
                    h_alt_tag=row.get("h_alt_tag") or "",
                ):

                    valid = False
                    break

        if valid:
            passing_specs.append(spec)

    return passing_specs

