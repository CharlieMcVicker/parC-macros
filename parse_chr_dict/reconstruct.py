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

    def get_pronominal(self, person: str, allow_set_a: bool) -> str:
        from parse_chr_dict.meta_label_compiler import filter_pronominals
        pronoun_set = "A" if self.set_a and allow_set_a else "B"
        if self.animate_objects and person in ["1st", "2nd"]:
            tags = filter_pronominals(person=person, pronoun_set="transitive")
            return tags[0] if tags else f"{person[0]}sg>3sg"

        number = "sg" if not self.plural else "ns" if person == "3rd" else "pl"
        target_person = "exclusive" if person == "1st" and self.plural else person
        tags = filter_pronominals(person=target_person, number=number, pronoun_set=pronoun_set)
        if tags:
            return tags[0]

        short_person = person[0] if person != "1st" or not self.plural else "E"
        return f"{short_person}{number}.{pronoun_set}"

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
        form_labels["pronominal"] = self.get_pronominal(
            person=parsing_meta.person, allow_set_a=parsing_meta.allows_set_a
        )

        all_labels = {**labels, **form_labels}
        surface_forms = inflect(
            root,
            feature_values=all_labels,
            name="verb",
            open_root=True,
            infer_lexical_features=True,
        )
        return any(surface == reference_form for surface in surface_forms)


# Backward compatibility alias
ReconstructionSpec = MetaLabelCombination


def reconstruct_row(row, entry_type: EntryType, lexical_fields: list[str]):
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
