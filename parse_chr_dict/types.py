from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Set, Tuple


@dataclass(frozen=True)
class ParseData:
    """
    Concrete parse data representing a single FST parse string.
    Isomorphic to the in-place morpheme tag sequence.
    """
    root: str
    prefix_class: str = ""
    pronominal: str = ""
    h_alt_tag: str = ""
    aspect_class: str = ""
    variant: int = 1
    aspect: str = ""
    tense_present_class: str = ""
    tense: str = ""
    prepronominal_prefixes: tuple[str, ...] = ()
    raw_tokens: tuple[str, ...] = ()

    def __post_init__(self):
        if isinstance(self.prepronominal_prefixes, list):
            object.__setattr__(self, "prepronominal_prefixes", tuple(self.prepronominal_prefixes))
        if isinstance(self.raw_tokens, list):
            object.__setattr__(self, "raw_tokens", tuple(self.raw_tokens))
        if isinstance(self.variant, str):
            v = int(self.variant) if self.variant.isdigit() else 1
            object.__setattr__(self, "variant", v)

    @property
    def has_distributive(self) -> bool:
        return any(p.startswith("[DIST") for p in self.prepronominal_prefixes)

    @property
    def has_translocutive(self) -> bool:
        return "[WI]" in self.prepronominal_prefixes

    @property
    def rules(self) -> str:
        return "+"

    @property
    def canonical_root(self) -> str:
        """Returns the root wrapped in legacy marker format for backwards compatibility."""
        h_part = (
            self.h_alt_tag
            if self.h_alt_tag and self.h_alt_tag not in self.root
            else ""
        )
        clean_root = (
            self.root.replace("[DIST=de]", "[DIST]").replace("[DIST=di]", "[DIST]")
        )
        return f"[Pro]{h_part}{clean_root}[Aspect][Tense]"

    def to_labels_dict(self) -> dict[str, str]:
        d: dict[str, str] = {
            "prefix_class": self.prefix_class,
            "pronominal": self.pronominal,
            "aspect_class": self.aspect_class,
            "aspect": self.aspect,
            "tense_present_class": self.tense_present_class,
            "tense": self.tense,
            "rules": self.rules,
        }
        if self.variant and self.variant != 1:
            d["variant"] = str(self.variant)
        if self.has_translocutive:
            d["translocutive"] = "+"
        if self.has_distributive:
            d["distributive"] = "+"
        if self.h_alt_tag:
            d["h_alt_tag"] = self.h_alt_tag
        return {k: v for k, v in d.items() if v}

    def to_inplace_string(self) -> str:
        """Serializes back to an in-place morpheme sequence for FST transduction."""
        parts: list[str] = []
        for p in self.prepronominal_prefixes:
            parts.append(p)
        if self.prefix_class:
            parts.append(f"[PrefixClass={self.prefix_class}]")
        if self.pronominal:
            parts.append(f"[Pro={self.pronominal}]")
        if self.h_alt_tag:
            parts.append(self.h_alt_tag)
        elif not any(self.root.startswith(t) for t in ("[H_", "[TEMP")):
            parts.append("[H_alt=none]")
        parts.append(self.root)
        if self.aspect_class:
            parts.append(f"[AspectClass={self.aspect_class}]")
        if self.variant and self.variant > 1:
            parts.append(f"[Variant={self.variant}]")
        if self.aspect:
            parts.append(f"[Aspect={self.aspect}]")
        if self.tense_present_class:
            parts.append(f"[TenseClass={self.tense_present_class}]")
        if self.tense:
            parts.append(f"[Tense={self.tense}]")
        return "".join(parts)


# Backward compatibility alias
InPlaceParseConfig = ParseData


@dataclass(frozen=True)
class VerbTemplate:
    """
    Coarse-grained projection of a single ParseData.
    Masks over inflectional features (pro, tense, aspect).
    Preserves lexical features observed in this parse:
    root, prefix_class, aspect_class, tense_present_class, variant,
    lexical prepronominal prefixes (distributive, translocutive), h_alt_tag.
    """
    root: str
    prefix_class: str = ""
    aspect_class: str = ""
    tense_present_class: str = ""
    variant: int = 1
    distributive: bool = False
    translocutive: bool = False
    h_alt_tag: str = ""

    @classmethod
    def from_parse(cls, parse: ParseData) -> VerbTemplate:
        return cls(
            root=parse.root,
            prefix_class=parse.prefix_class,
            aspect_class=parse.aspect_class,
            tense_present_class=parse.tense_present_class,
            variant=parse.variant,
            distributive=parse.has_distributive,
            translocutive=parse.has_translocutive,
            h_alt_tag=parse.h_alt_tag,
        )

    def lexical_labels(self) -> dict[str, str]:
        d = {
            "aspect_class": self.aspect_class,
            "prefix_class": self.prefix_class,
            "tense_present_class": self.tense_present_class,
        }
        if self.variant != 1:
            d["variant"] = str(self.variant)
        if self.translocutive:
            d["translocutive"] = "+"
        if self.distributive:
            d["distributive"] = "+"
        return d


@dataclass(frozen=True)
class AspectVariants:
    """Aspect variant indices across the 5 principal aspects (defaults to 1)."""
    present: int = 1
    incompletive: int = 1
    completive: int = 1
    immediate: int = 1
    infinitive: int = 1

    def with_variant(self, aspect: str, variant: int) -> AspectVariants:
        mapping = {
            "present": "present",
            "present_1sg": "present",
            "1st_present": "present",
            "3rd_present": "present",
            "incompletive": "incompletive",
            "imperfective": "incompletive",
            "3rd_habitual": "incompletive",
            "3rd_incompletive_habitual": "incompletive",
            "completive": "completive",
            "perfective": "completive",
            "3rd_completive": "completive",
            "3rd_completive_assertive": "completive",
            "immediate": "immediate",
            "imperative": "immediate",
            "2nd_imperative": "immediate",
            "infinitive": "infinitive",
            "3rd_infinitive": "infinitive",
        }
        field_name = mapping.get(aspect)
        if field_name:
            kwargs = {
                "present": self.present,
                "incompletive": self.incompletive,
                "completive": self.completive,
                "immediate": self.immediate,
                "infinitive": self.infinitive,
            }
            kwargs[field_name] = int(variant)
            return AspectVariants(**kwargs)
        return self

    def get_variant(self, aspect: str) -> int:
        mapping = {
            "present": self.present,
            "present_1sg": self.present,
            "1st_present": self.present,
            "3rd_present": self.present,
            "incompletive": self.incompletive,
            "imperfective": self.incompletive,
            "3rd_habitual": self.incompletive,
            "3rd_incompletive_habitual": "incompletive",
            "completive": self.completive,
            "perfective": self.completive,
            "3rd_completive": "completive",
            "3rd_completive_assertive": "completive",
            "immediate": self.immediate,
            "imperative": self.immediate,
            "2nd_imperative": "immediate",
            "infinitive": self.infinitive,
            "3rd_infinitive": "infinitive",
        }
        val = mapping.get(str(aspect))
        if isinstance(val, int):
            return val
        if hasattr(self, str(aspect)):
            attr_val = getattr(self, str(aspect))
            if isinstance(attr_val, int):
                return attr_val
        return 1

    def to_dict(self) -> dict[str, int]:
        return {
            "variant_present": self.present,
            "variant_incompletive": self.incompletive,
            "variant_completive": self.completive,
            "variant_immediate": self.immediate,
            "variant_infinitive": self.infinitive,
        }


@dataclass(frozen=True)
class VerbMetadata:
    """Paradigm-level metadata and pooled aspect variants."""
    entry_type: str = "Eventful"
    is_set_a: bool = True
    is_plural: bool = False
    animate_objects: bool = False
    aspect_variants: AspectVariants = field(default_factory=AspectVariants)

    def with_variant(self, aspect: str, variant: int) -> VerbMetadata:
        return VerbMetadata(
            entry_type=self.entry_type,
            is_set_a=self.is_set_a,
            is_plural=self.is_plural,
            animate_objects=self.animate_objects,
            aspect_variants=self.aspect_variants.with_variant(aspect, variant),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_type": self.entry_type,
            "set_a": self.is_set_a,
            "plural": self.is_plural,
            "animate_objects": self.animate_objects,
            **self.aspect_variants.to_dict(),
        }


@dataclass(frozen=True, init=False)
class LexicalVerb:
    """
    Canonical representation of a derived Cherokee lexical verb entry.
    Formed as the product type VerbTemplate x VerbMetadata, with alternating grade resolution.
    """
    template: VerbTemplate
    metadata: VerbMetadata
    glottal_root: Optional[str] = None
    h_alt_tag: str = ""

    def __init__(
        self,
        template: Optional[VerbTemplate] = None,
        metadata: Optional[VerbMetadata] = None,
        glottal_root: Optional[str] = None,
        h_alt_tag: str = "",
        *,
        h_root: Optional[str] = None,
        prefix_class: str = "",
        aspect_class: str = "",
        tense_present_class: str = "",
        set_a: bool = True,
        plural: bool = False,
        animate_objects: bool = False,
        present_variant: str | int = 1,
        distributive: bool = False,
        translocutive: bool = False,
        aspect_variants: Optional[AspectVariants] = None,
        entry_type: str = "Eventful",
    ):
        if template is None:
            var_int = int(present_variant) if str(present_variant).isdigit() else 1
            template = VerbTemplate(
                root=h_root or "",
                prefix_class=prefix_class,
                aspect_class=aspect_class,
                tense_present_class=tense_present_class,
                variant=var_int,
                distributive=distributive,
                translocutive=translocutive,
                h_alt_tag=h_alt_tag,
            )
        if metadata is None:
            if aspect_variants is None:
                aspect_variants = AspectVariants(present=template.variant)
            metadata = VerbMetadata(
                entry_type=entry_type,
                is_set_a=set_a,
                is_plural=plural,
                animate_objects=animate_objects,
                aspect_variants=aspect_variants,
            )
        object.__setattr__(self, "template", template)
        object.__setattr__(self, "metadata", metadata)
        object.__setattr__(self, "glottal_root", glottal_root)
        object.__setattr__(self, "h_alt_tag", h_alt_tag)

    @property
    def h_root(self) -> str:
        """The base/non-alternating root grade."""
        from parse_chr_dict.h_alternation import strip_h_alt_tags
        return strip_h_alt_tags(self.template.root)

    @property
    def prefix_class(self) -> str:
        return self.template.prefix_class

    @property
    def aspect_class(self) -> str:
        return self.template.aspect_class

    @property
    def tense_present_class(self) -> str:
        return self.template.tense_present_class

    @property
    def set_a(self) -> bool:
        return self.metadata.is_set_a

    @property
    def plural(self) -> bool:
        return self.metadata.is_plural

    @property
    def animate_objects(self) -> bool:
        return self.metadata.animate_objects

    @property
    def entry_type(self) -> str:
        return self.metadata.entry_type

    @property
    def present_variant(self) -> str:
        return str(self.template.variant) if self.template.variant > 1 else ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "h_root": self.h_root,
            "h_alt_tag": self.h_alt_tag or "[H_alt=none]",
            "prefix_class": self.prefix_class,
            "aspect_class": self.aspect_class,
            "tense_present_class": self.tense_present_class,
            "set_a": self.set_a,
            "plural": self.plural,
            "animate_objects": self.animate_objects,
            "present_variant": self.present_variant,
            **self.metadata.aspect_variants.to_dict(),
        }

    def to_row_dict(self, base_row: dict[str, str], entry_type: Optional[str] = None) -> dict[str, Any]:
        """Pure serialization into roots.csv row schema."""
        d = {k: base_row.get(k, "") for k in [
            "corpus_id", "entry_no", "definition", "present", "present_1sg",
            "imperfective", "perfective", "imperative", "infinitive"
        ]}
        d["entry_type"] = entry_type or self.metadata.entry_type
        d["h_root"] = self.h_root
        d["h_alt_tag"] = self.h_alt_tag or "[H_alt=none]"
        d["aspect_class"] = self.template.aspect_class
        d["prefix_class"] = self.template.prefix_class
        d["tense_present_class"] = self.template.tense_present_class
        d["set_a"] = self.metadata.is_set_a
        d["plural"] = self.metadata.is_plural
        d["animate_objects"] = self.metadata.animate_objects
        d.update(self.metadata.aspect_variants.to_dict())
        return d

    def lexical_labels(self) -> dict[str, str]:
        return self.template.lexical_labels()

    def lexical_tuple(self) -> tuple[str, str, tuple[tuple[str, str], ...]]:
        return (
            self.h_root,
            self.h_alt_tag or "[H_alt=none]",
            (
                ("aspect_class", self.aspect_class),
                ("prefix_class", self.prefix_class),
                ("tense_present_class", self.tense_present_class),
            ),
        )

    def to_meta_combination(self):
        from parse_chr_dict.reconstruct import MetaLabelCombination
        return MetaLabelCombination(
            set_a=self.set_a,
            plural=self.plural,
            animate_objects=self.animate_objects,
        )

    def get_dynamic_constraints(self, form_spec: Optional[Any] = None) -> list[Any]:
        from parse_chr_dict.meta_label_compiler import FeatureConstraint, MatchMode
        constraints = [
            FeatureConstraint(slot_name="aspect_class", mode=MatchMode.EXACT, values=[self.aspect_class]),
            FeatureConstraint(slot_name="tense_present_class", mode=MatchMode.EXACT, values=[self.tense_present_class]),
        ]
        if self.prefix_class in ("a_stem", "k_a_stem"):
            constraints.append(FeatureConstraint(slot_name="prefix_class", mode=MatchMode.ONE_OF, values=["a_stem", "k_a_stem"]))
        else:
            constraints.append(FeatureConstraint(slot_name="prefix_class", mode=MatchMode.EXACT, values=[self.prefix_class]))
        return constraints

    def get_meta_label_ids(self, form_spec: Any) -> list[str]:
        meta_ids = [form_spec.meta_label_id]
        if form_spec.allows_set_a:
            if self.set_a:
                meta_ids.append("[PRONOUN_SET=A]")

        if self.plural:
            meta_ids.append("[PLURAL=TRUE]")
        else:
            meta_ids.append("[PLURAL=FALSE]")

        if form_spec.person in ("1st", "2nd"):
            if self.animate_objects:
                meta_ids.append("[OBJECT_ANIMACY=ANIMATE]")
            else:
                meta_ids.append("[OBJECT_ANIMACY=INANIMATE]")

        return meta_ids

    def validate(
        self,
        row: dict[str, str],
        entry_type: Any,
        compiler: Optional[Any] = None,
    ) -> bool:
        from parse_chr_dict.reconstruct import validate_hypothesis
        return validate_hypothesis(self, row, entry_type, compiler=compiler)


# Backward compatibility aliases
DerivationHypothesis = LexicalVerb
LexicalVerbHypothesis = LexicalVerb
LexicalVerbEntry = LexicalVerb
