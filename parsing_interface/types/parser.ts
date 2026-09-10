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
