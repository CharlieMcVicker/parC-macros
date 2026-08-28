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


def memoized_inflect(
    root: str,
    feature_values: dict[str, str] | frozenset[tuple[str, str]] | set[tuple[str, str]],
    name: str = "verb",
    open_root: bool = True,
    infer_lexical_features: bool = True,
) -> list[str]:
    """
    Memoized wrapper around inflect() to avoid repeated FST operations
    for identical root and feature configurations.
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

        for pro in pronominal_candidates:
            if is_h_alternation_trigger(pro):
                if glottal_root is None:
                    continue
                active_root = glottal_root
            else:
                active_root = h_root

            for p_cand in prefix_candidates:
                all_labels = {**labels, **form_labels, "pronominal": pro, "prefix_class": p_cand}
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
    Validates a DerivationHypothesis against all non-empty forms in a row.
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
            if not meta_comb.validate(
                h_root=hypothesis.h_root,
                glottal_root=hypothesis.glottal_root,
                reference_form=ref_surface,
                labels=labels,
                parsing_meta=parsing_meta,
                compiler=compiler,
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
                    glottal_root=row.get("glottal_root") or None,
                    reference_form=reference_form,
                    labels=labels,
                    parsing_meta=parsing_meta,
                    compiler=compiler,
                ):

                    valid = False
                    break

        if valid:
            passing_specs.append(spec)

    return passing_specs

