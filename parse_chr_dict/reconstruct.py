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
class ReconstructionSpec:
    plural: bool
    set_a: bool
    animate_objects: bool

    def get_pronominal(self, person, allow_set_a):
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
        
        # Fallback string calculation
        short_person = person[0] if person != "1st" or not self.plural else "E"
        return f"{short_person}{number}.{pronoun_set}"

    @classmethod
    def all_specs(_cls):
        for plural in [True, False]:
            for set_a in [True, False]:
                for animate_objects in [False] if plural else [True, False]:
                    yield ReconstructionSpec(
                        plural=plural, set_a=set_a, animate_objects=animate_objects
                    )
    
    @classmethod
    def fieldnames(_cls):
        return ["set_a", "plural", "animate_objects"]

    def validate(self, *, root: str, reference_form: str, labels: dict[str, str], parsing_meta: FormParsing, compiler: Optional[MetaConstraintCompiler] = None):
        if compiler is None:
            compiler = MetaConstraintCompiler()
        target_tuples = compiler.get_feature_tuples_from_meta([parsing_meta.meta_label_id])
        form_labels = dict(target_tuples)
        form_labels["pronominal"] = self.get_pronominal(
            person=parsing_meta.person, allow_set_a=parsing_meta.allows_set_a
        )

        all_labels = {**labels, **form_labels}
        surface_forms = inflect(root, feature_values=all_labels, name="verb", open_root=True, infer_lexical_features=True)
        return any(surface == reference_form for surface in surface_forms)

def reconstruct_row(row, entry_type: EntryType, lexical_fields: list[str]):
    passing_specs: list[ReconstructionSpec] = list()
    for spec in ReconstructionSpec.all_specs():
        valid = True
        for parsing in entry_type.forms:
            parsing_meta = next(p for p in FORMS_TO_PARSE if p.name == parsing)
            reference_form = row[parsing_meta.corpus_key]
            if reference_form:
                labels = {k: row[k] for k in lexical_fields}
                labels["rules"] = "+"
                if not spec.validate(root=row["root"], reference_form=reference_form, labels=labels, parsing_meta=parsing_meta):
                    valid = False
                    break
        
        if valid:
            passing_specs.append(spec)

    
    return passing_specs
