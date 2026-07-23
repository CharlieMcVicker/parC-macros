from dataclasses import dataclass
import json

from parse_chr_dict.dict_structure import FORMS_TO_PARSE, EntryType, FormParsing
from parC.grammar.paradigm_compilation import inflect


@dataclass
class ReconstructionSpec:
    plural: bool
    set_a: bool
    animate_objects: bool

    def get_pronominal(self, person, allow_set_a):
        set = "A" if self.set_a and allow_set_a else "B"
        number = "sg" if not self.plural else "ns" if person == "3rd" else "pl"
        short_person = person[0]
        if short_person == "1" and self.plural:
            short_person = "E"

        if self.animate_objects and short_person in ["1", "2"]:
            return f"{short_person}sg>3sg"
        else:
            return f"{short_person}{number}.{set}"

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

    def validate(self, *, root: str, reference_form: str, labels: dict[str, str], parsing_meta: FormParsing):
        form_labels = {k: v for k, v in parsing_meta.lexical_features}
        form_labels["pronominal"] = self.get_pronominal(
            person=parsing_meta.person, allow_set_a=parsing_meta.allows_set_a
        )

        all_labels = {**labels, **form_labels}
        

        # print("[DEBUG]", root, json.dumps(all_labels))
        surface_forms = inflect(root, feature_values=all_labels, name="verb", open_root=True, infer_lexical_features=True)
        
        # print(surface_forms)
        if not any(surface == reference_form for surface in surface_forms):
            return False

        return True

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
