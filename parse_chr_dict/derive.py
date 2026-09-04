from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple, Any
import warnings

from parse_chr_dict.parse import (
    parse_surface,
    parse_string_to_parse_data,
)
from parse_chr_dict.types import (
    ParseData,
    VerbTemplate,
    AspectVariants,
    VerbMetadata,
    LexicalVerb,
    Pronominal,
    VerbForm,
    VERB_FORMS_BY_NAME,
    PRES_3RD,
    PRES_1SG,
    HABITUAL_3RD,
    COMPLETIVE_3RD,
    INCOMPLETIVE_ASSERTIVE_3RD,
    IMPERATIVE_2ND,
    FUT_PROG_2ND,
    INFINITIVE_3RD,
)
from parse_chr_dict.h_alternation import (
    H_ALT_TAGS,
    is_h_alternation_trigger,
    validate_h_alternation_trigger,
    strip_h_alt_tags,
)

VERB_FORMS_BY_META_ID: Dict[str, VerbForm] = {
    "[FORM=3RD_PRES]": PRES_3RD,
    "[FORM=1ST_PRES]": PRES_1SG,
    "[FORM=3RD_HABITUAL]": HABITUAL_3RD,
    "[FORM=3RD_COMPLETIVE]": COMPLETIVE_3RD,
    "[FORM=3RD_INCOMPLETIVE_ASSERTIVE]": INCOMPLETIVE_ASSERTIVE_3RD,
    "[FORM=2ND_IMPERATIVE]": IMPERATIVE_2ND,
    "[FORM=2ND_FUT_PROG]": FUT_PROG_2ND,
    "[FORM=3RD_INFINITIVE]": INFINITIVE_3RD,
}


def derive_hypotheses_for_forms(
    forms: List[Tuple[str, VerbForm | Any]],
    compiler: Optional[Any] = None,
    lexical_features: Optional[Set[str]] = None,
) -> Set[LexicalVerb]:
    """
    Derives and iteratively narrows candidate LexicalVerb objects form-by-form across a row
    via pure surface parsing:
    1. Parse the initial form bare surface to generate candidate hypotheses
       as LexicalVerb instances (VerbTemplate x VerbMetadata).
    2. For each subsequent form, parse its bare surface, filter via VerbForm.matches,
       and prune hypotheses in pure Python (prefix compatibility, present-tense variant
       consistency, plurality, animacy, root equality, and H-alternation).
    """
    if not forms:
        return set()

    # Normalize forms to List[Tuple[str, VerbForm]]
    normalized_forms: List[Tuple[str, VerbForm]] = []
    for surface, spec_or_form in forms:
        if isinstance(spec_or_form, VerbForm):
            v_form = spec_or_form
        elif hasattr(spec_or_form, "to_verb_form"):
            v_form = spec_or_form.to_verb_form()
        elif isinstance(spec_or_form, str):
            if spec_or_form in VERB_FORMS_BY_META_ID:
                v_form = VERB_FORMS_BY_META_ID[spec_or_form]
            elif spec_or_form in VERB_FORMS_BY_NAME:
                v_form = VERB_FORMS_BY_NAME[spec_or_form]
            else:
                v_form = VerbForm(
                    name=spec_or_form,
                    corpus_key="",
                    aspect="present",
                    tense="present",
                    person="3rd",
                    allows_set_a=True,
                )
        elif hasattr(spec_or_form, "matches"):
            v_form = spec_or_form
        else:
            raise TypeError(f"Unsupported form specification: {type(spec_or_form)}")
        normalized_forms.append((surface, v_form))

    # Step 1: Initial form
    init_surface, init_form = normalized_forms[0]
    if not init_surface:
        return set()

    init_parses = parse_surface(init_surface)
    if not init_parses:
        return set()

    candidate_hypotheses: Set[LexicalVerb] = set()

    for p in init_parses:
        p_data = parse_string_to_parse_data(p)
        if not init_form.matches(p_data):
            continue

        tmpl = VerbTemplate.from_parse(p_data)
        pref = tmpl.prefix_class
        asp = tmpl.aspect_class
        t_pres = tmpl.tense_present_class
        pro_tag = p_data.pronominal
        pres_var = tmpl.variant
        if not pref or not asp or not t_pres or not pro_tag:
            continue

        pro = Pronominal.from_tag(pro_tag)
        is_plural = pro.number in ("ns", "pl", "dl")
        is_transitive = pro.pronoun_set == "transitive"
        is_set_a = pro.pronoun_set in ("A", "transitive")

        # Validate trigger if mutation tag is present
        has_mutation = any(
            tag in p_data.root
            for tag in H_ALT_TAGS
            if tag.lower() not in ("[h_none]", "[h_alt=none]")
        )
        if not validate_h_alternation_trigger(pro_tag, has_h_alt=has_mutation):
            continue

        # Set A candidate values
        if init_form.allows_set_a:
            set_a_options = [is_set_a]
        else:
            set_a_options = [True, False]

        # Plural candidate values
        plural_options = [is_plural]

        # Animate object candidate values
        if is_plural:
            animate_options = [False]
        elif is_transitive:
            animate_options = [True]
        elif init_form.person == "3rd":
            animate_options = [False, True]
        else:
            animate_options = [False]

        h_alt_val = p_data.h_alt_tag or "[H_alt=none]"
        aspect_variants = AspectVariants(present=pres_var)

        for sa in set_a_options:
            for pl in plural_options:
                for anim in animate_options:
                    meta = VerbMetadata(
                        entry_type="Eventful",
                        is_set_a=sa,
                        is_plural=pl,
                        animate_objects=anim,
                        aspect_variants=aspect_variants,
                    )
                    candidate_hypotheses.add(
                        LexicalVerb(
                            template=tmpl,
                            metadata=meta,
                            h_alt_tag=h_alt_val,
                        )
                    )

    if not candidate_hypotheses or len(normalized_forms) == 1:
        return candidate_hypotheses

    # Step 2: Form-by-form refinement
    def prefix_compat(p1: str, p2: str) -> bool:
        return p1 == p2 or (p1 in ("k_a_stem", "a_stem") and p2 in ("k_a_stem", "a_stem"))

    for surface, form in normalized_forms[1:]:
        if not surface:
            continue
        if not candidate_hypotheses:
            break

        parses = parse_surface(surface)
        if not parses:
            return set()

        # Group parses by (p_asp, p_t_pres)
        parsed_by_asp_tense: Dict[
            Tuple[str, str],
            List[Tuple[ParseData, VerbTemplate, str, bool, bool, bool, bool, int]],
        ] = {}
        for p in parses:
            p_data = parse_string_to_parse_data(p)
            if not form.matches(p_data):
                continue

            p_tmpl = VerbTemplate.from_parse(p_data)
            p_pref = p_tmpl.prefix_class
            p_asp = p_tmpl.aspect_class
            p_t_pres = p_tmpl.tense_present_class
            pro_tag = p_data.pronominal
            p_var = p_tmpl.variant
            if not p_pref or not p_asp or not p_t_pres or not pro_tag:
                continue

            pro = Pronominal.from_tag(pro_tag)
            p_plural = pro.number in ("ns", "pl", "dl")
            p_set_a = pro.pronoun_set in ("A", "transitive")
            p_trans = pro.pronoun_set == "transitive"
            p_is_glottal = is_h_alternation_trigger(pro_tag)

            has_mutation = any(
                tag in p_data.root
                for tag in H_ALT_TAGS
                if tag.lower() not in ("[h_none]", "[h_alt=none]")
            )
            if not validate_h_alternation_trigger(pro_tag, has_h_alt=has_mutation):
                continue

            key = (p_asp, p_t_pres)
            if key not in parsed_by_asp_tense:
                parsed_by_asp_tense[key] = []
            parsed_by_asp_tense[key].append(
                (p_data, p_tmpl, pro_tag, p_plural, p_set_a, p_trans, p_is_glottal, p_var)
            )

        if not parsed_by_asp_tense:
            return set()

        surviving: Set[LexicalVerb] = set()

        for hyp in candidate_hypotheses:
            matching_items = parsed_by_asp_tense.get(
                (hyp.aspect_class, hyp.tense_present_class)
            )
            if not matching_items:
                continue

            for p_data, p_tmpl, pro_tag, p_plural, p_set_a, p_trans, p_is_glottal, p_var in matching_items:
                if not prefix_compat(hyp.prefix_class, p_tmpl.prefix_class):
                    continue

                # Enforce present-tense variant consistency: template_3sg.variant == template_1sg.variant
                if (
                    form.name == "1st_present"
                    or form.corpus_key == "present_1sg"
                    or (hasattr(form, "meta_label_id") and form.meta_label_id == "[FORM=1ST_PRES]")
                ):
                    if p_var != hyp.template.variant:
                        continue

                if p_plural != hyp.plural:
                    continue

                if form.allows_set_a and not p_trans:
                    if p_set_a != hyp.set_a:
                        continue

                if form.person in ("1st", "2nd"):
                    if hyp.animate_objects:
                        # Allow fallback for 2nd person imperative if transitive not available
                        if not p_trans and not (
                            form.person == "2nd" and form.corpus_key == "imperative"
                        ):
                            continue
                    else:
                        if p_trans:
                            continue

                # Root compatibility check: all forms must match hyp.h_root
                if strip_h_alt_tags(p_data.root) != hyp.h_root:
                    continue

                if p_is_glottal:
                    p_alt = p_data.h_alt_tag or "[H_alt=none]"
                    if (
                        hyp.h_alt_tag
                        and hyp.h_alt_tag != "[H_alt=none]"
                        and p_alt != "[H_alt=none]"
                    ):
                        if hyp.h_alt_tag != p_alt:
                            continue
                    new_h_alt_tag = (
                        p_alt if p_alt != "[H_alt=none]" else (hyp.h_alt_tag or "[H_alt=none]")
                    )
                else:
                    new_h_alt_tag = hyp.h_alt_tag or "[H_alt=none]"

                # Fold non-shared form variant into metadata.aspect_variants
                aspect_name = p_data.aspect or form.corpus_key
                new_aspect_variants = hyp.metadata.aspect_variants.with_variant(
                    aspect_name, p_var
                )
                new_metadata = VerbMetadata(
                    entry_type=hyp.metadata.entry_type,
                    is_set_a=hyp.metadata.is_set_a,
                    is_plural=hyp.metadata.is_plural,
                    animate_objects=hyp.metadata.animate_objects,
                    aspect_variants=new_aspect_variants,
                )

                # Determine canonical prefix class
                p_pref = p_tmpl.prefix_class
                canon_pref = (
                    hyp.prefix_class
                    if hyp.prefix_class != "k_a_stem"
                    else (p_pref if p_pref != "k_a_stem" else "a_stem")
                )
                new_template = VerbTemplate(
                    root=hyp.template.root,
                    prefix_class=canon_pref,
                    aspect_class=hyp.template.aspect_class,
                    tense_present_class=hyp.template.tense_present_class,
                    variant=hyp.template.variant,
                    distributive=hyp.template.distributive,
                    translocutive=hyp.template.translocutive,
                    h_alt_tag=new_h_alt_tag,
                )

                surviving.add(
                    LexicalVerb(
                        template=new_template,
                        metadata=new_metadata,
                        h_alt_tag=new_h_alt_tag,
                    )
                )

        # If any hypotheses underwent actual H-mutation on a trigger form, reject unmutated fallbacks for the same root
        mutated_h_roots = {
            h.h_root
            for h in surviving
            if h.h_alt_tag and h.h_alt_tag != "[H_alt=none]"
        }
        if mutated_h_roots:
            surviving = {
                h
                for h in surviving
                if not (
                    h.h_root in mutated_h_roots
                    and (not h.h_alt_tag or h.h_alt_tag == "[H_alt=none]")
                )
            }

        candidate_hypotheses = surviving

    return candidate_hypotheses


def derive_lexical_features_4step(
    forms: List[Tuple[str, Any]],
    compiler: Optional[Any] = None,
    lexical_features: Optional[Set[str]] = None,
) -> Set[Tuple[str, Tuple[Tuple[str, str], ...]]]:
    """
    Legacy derivation wrapper returning lexical tuples for backwards compatibility.
    """
    hypotheses = derive_hypotheses_for_forms(
        forms, compiler=compiler, lexical_features=lexical_features
    )
    return {h.lexical_tuple() for h in hypotheses}
