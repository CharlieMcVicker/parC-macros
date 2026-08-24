from dataclasses import dataclass
from typing import Optional
from parse_chr_dict.meta_label_compiler import (
    FORMS_TO_PARSE,
    EntryTypeSpec as EntryType,
    FormParsingSpec as FormParsing,
    MetaConstraintCompiler,
)
from parC.grammar.paradigm_compilation import inflect


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
        from parse_chr_dict.meta_label_compiler import filter_pronominals
        pronoun_set = "A" if self.set_a and allow_set_a else "B"
        if self.animate_objects and person in ["1st", "2nd"]:
            tags = filter_pronominals(person=person, pronoun_set="transitive")
            candidates = list(tags) if tags else [f"{person[0]}sg>3sg"]
            if person == "2nd":
                candidates.append(f"2sg.{pronoun_set}")
            return candidates

        if self.plural:
            if person == "3rd":
                return [f"3ns.{pronoun_set}", f"3dl.{pronoun_set}"]
            elif person == "1st":
                return [f"Epl.{pronoun_set}", f"Edl.{pronoun_set}", f"1pl.{pronoun_set}", f"1dl.{pronoun_set}"]
            elif person == "2nd":
                return [f"2pl.{pronoun_set}", f"2dl.{pronoun_set}"]

        return [f"{person[0]}sg.{pronoun_set}"]

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
        root: str,
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

        prefix_candidates = [labels.get("prefix_class")]
        if labels.get("prefix_class") == "a_stem":
            prefix_candidates.append("k_a_stem")

        for pro in pronominal_candidates:
            for pref in prefix_candidates:
                all_labels = {**labels, **form_labels, "pronominal": pro, "prefix_class": pref}
                try:
                    surface_forms = inflect(
                        root,
                        feature_values=all_labels,
                        name="verb",
                        open_root=True,
                        infer_lexical_features=True,
                    )
                    if any(surface == reference_form for surface in surface_forms):
                        return True
                except (ValueError, KeyError):
                    continue
        return False


# Backward compatibility alias
ReconstructionSpec = MetaLabelCombination


def validate_hypothesis(
    hypothesis,
    row: dict,
    entry_type: EntryType,
    compiler: Optional[MetaConstraintCompiler] = None,
) -> bool:
    """
    Validates a DerivationHypothesis against all non-empty forms in a row.
    Returns True if every non-empty form in the row reconstructs to the exact surface form.
    """
    if compiler is None:
        compiler = MetaConstraintCompiler()

    meta_comb = hypothesis.to_meta_combination()
    labels = {
        **hypothesis.lexical_labels(),
        "rules": "+",
    }

    for form_name in entry_type.forms:
        parsing_meta = next((p for p in FORMS_TO_PARSE if p.name == form_name), None)
        if not parsing_meta:
            continue
        reference_form = row.get(parsing_meta.corpus_key)
        if reference_form and " " not in reference_form:
            from parse_chr_dict.create_aspect_class_csv import respell_consonants
            ref_surface = respell_consonants(reference_form)
            if not meta_comb.validate(
                root=hypothesis.root,
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
    for spec in MetaLabelCombination.all_combinations():
        valid = True
        for parsing in entry_type.forms:
            parsing_meta = next(p for p in FORMS_TO_PARSE if p.name == parsing)
            reference_form = row.get(parsing_meta.corpus_key)
            if reference_form:
                labels = {k: row[k] for k in lexical_fields if k in row}
                labels["rules"] = "+"
                if not spec.validate(
                    root=row["root"],
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

