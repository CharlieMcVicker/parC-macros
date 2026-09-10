export interface SlotDefinition {
  name: string;
  role: "prefix" | "suffix" | string;
  rule?: string;
  tags?: string[];
}

export interface SlotManifest {
  slots: SlotDefinition[];
  template: string[];
  tag_to_slot?: Record<string, string>;
  root_boundaries?: {
    left?: string;
    right?: string;
  };
}

export const FALLBACK_MANIFEST: SlotManifest = {
  slots: [
    {
      name: "pronominal",
      role: "prefix",
      rule: "pro_replace",
      tags: ["PrefixClass", "Pro"],
    },
    {
      name: "aspect",
      role: "suffix",
      rule: "aspect_replace",
      tags: ["AspectClass", "Variant", "Aspect"],
    },
    {
      name: "tense",
      role: "suffix",
      rule: "tense_replace",
      tags: ["Tense"],
    },
  ],
  template: [
    "<PrepronominalPrefixes>",
    "<PrefixClass>",
    "<Pro>",
    "<H_metathesis>",
    "<H_alt>",
    "<Root>",
    "<AspectClass>",
    "<Variant>",
    "<Aspect>",
    "<Tense>",
  ],
  tag_to_slot: {
    PrefixClass: "pronominal",
    Pro: "pronominal",
    AspectClass: "aspect",
    Variant: "aspect",
    Aspect: "aspect",
    Tense: "tense",
  },
  root_boundaries: {
    left: "<H_alt>",
    right: "<AspectClass>",
  },
};

export interface ColumnDef {
  key: string;
  label: string;
  category: "prefix" | "root" | "suffix";
  tag?: string;
}

export interface PrefixBundle {
  prepronominal_prefixes: string[];
  prefix_class: string;
  pronominal: string;
  h_metathesis_tag: string;
  h_alt_tag: string;
  slot_values: Record<string, string>;
}

export interface SuffixBundle {
  aspect_class: string;
  variant: number | string;
  aspect: string;
  tense: string;
  slot_values: Record<string, string>;
}

export interface SlotOptions {
  prepronominal?: string[][];
  prefix_class?: string[];
  pronominal?: string[];
  h_metathesis?: string[];
  h_alt?: string[];
  aspect_class?: string[];
  variant?: (number | string)[];
  aspect?: string[];
  tense?: string[];
  [key: string]: unknown;
}

export interface RootParseOption {
  root: string;
  total_parses: number;
  is_fully_factorable: boolean;
  prefix_bundles: PrefixBundle[];
  suffix_bundles: SuffixBundle[];
  slot_options: SlotOptions;
}

export interface WordParseResult {
  word: string;
  cleanWord: string;
  parseOptions: RootParseOption[];
  totalParses: number;
  error?: string;
}

export interface ParseApiResponse {
  results: WordParseResult[];
  rawTokens: string[];
}

export type SelectedSlots = Record<string, string>;
