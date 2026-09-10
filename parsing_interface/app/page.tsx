"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  ColumnDef,
  FALLBACK_MANIFEST,
  ParseApiResponse,
  PrefixBundle,
  RootParseOption,
  SlotManifest,
  SuffixBundle,
  WordParseResult,
} from "@/types/parser";

function tagToSnake(name: string): string {
  return name
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2")
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1_$2")
    .toLowerCase();
}

function tagToLabel(name: string): string {
  const clean = name.replace(/[<>]/g, "");
  if (clean === "PrepronominalPrefixes" || clean === "prepronominal") return "Prepronominal";
  if (clean === "PrefixClass" || clean === "prefix_class") return "Prefix Class";
  if (clean === "Pro" || clean === "pronominal") return "Pronominal";
  if (clean === "H_metathesis" || clean === "h_metathesis") return "H-Metathesis";
  if (clean === "H_alt" || clean === "h_alt") return "H-Alt";
  if (clean === "Root" || clean === "root") return "Root";
  if (clean === "AspectClass" || clean === "aspect_class") return "Aspect Class";
  if (clean === "Variant" || clean === "variant") return "Variant";
  if (clean === "Aspect" || clean === "aspect") return "Aspect";
  if (clean === "Tense" || clean === "tense") return "Tense";

  const words = clean
    .replace(/_/g, " ")
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2");
  return words
    .split(/\s+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

function tagToKey(name: string): string {
  const clean = name.replace(/[<>]/g, "");
  if (clean === "PrepronominalPrefixes" || clean === "PPP") return "prepronominal";
  if (clean === "Pro") return "pronominal";
  if (clean === "Root") return "root";
  if (clean === "H_metathesis") return "h_metathesis";
  if (clean === "H_alt") return "h_alt";
  if (clean === "AspectClass") return "aspect_class";
  if (clean === "PrefixClass") return "prefix_class";
  if (clean === "Variant") return "variant";
  if (clean === "Aspect") return "aspect";
  if (clean === "Tense") return "tense";
  return tagToSnake(clean);
}

function buildColumnDefs(manifest: SlotManifest): ColumnDef[] {
  const template = manifest.template || [];
  const rootIndex = template.findIndex((t) => t.replace(/[<>]/g, "").toLowerCase() === "root");

  const slotRoleMap = new Map<string, "prefix" | "suffix">();
  for (const s of manifest.slots || []) {
    const role = s.role === "prefix" || s.role === "suffix" ? s.role : "suffix";
    slotRoleMap.set(s.name, role);
    for (const t of s.tags || []) {
      slotRoleMap.set(t, role);
    }
  }

  return template.map((rawTag, idx) => {
    const cleanTag = rawTag.replace(/[<>]/g, "");
    const key = tagToKey(cleanTag);
    const label = tagToLabel(cleanTag);

    let category: "prefix" | "root" | "suffix" = "suffix";
    if (cleanTag.toLowerCase() === "root") {
      category = "root";
    } else if (rootIndex !== -1) {
      category = idx < rootIndex ? "prefix" : "suffix";
    } else if (slotRoleMap.has(cleanTag)) {
      category = slotRoleMap.get(cleanTag)!;
    }

    return {
      key,
      label,
      category,
      tag: cleanTag,
    };
  });
}

function getPrefixBundleValue(bundle: PrefixBundle, key: string, tag?: string): string {
  if (key === "prepronominal") {
    return bundle.prepronominal_prefixes && bundle.prepronominal_prefixes.length > 0
      ? bundle.prepronominal_prefixes.join(",")
      : "(none)";
  }
  if (key === "prefix_class") {
    return bundle.prefix_class || "";
  }
  if (key === "pronominal") {
    return bundle.pronominal || "";
  }
  if (key === "h_metathesis") {
    return bundle.h_metathesis_tag || bundle.slot_values?.["H_metathesis"] || bundle.slot_values?.["H_METATHESIS"] || "";
  }
  if (key === "h_alt") {
    return bundle.h_alt_tag || bundle.slot_values?.["H_alt"] || bundle.slot_values?.["H_ALT"] || "";
  }
  if (bundle.slot_values) {
    if (bundle.slot_values[key] !== undefined) return bundle.slot_values[key];
    if (tag && bundle.slot_values[tag] !== undefined) return bundle.slot_values[tag];
  }
  return "";
}

function getSuffixBundleValue(bundle: SuffixBundle, key: string, tag?: string): string {
  if (key === "aspect_class") {
    return bundle.aspect_class || "";
  }
  if (key === "variant") {
    return String(bundle.variant);
  }
  if (key === "aspect") {
    return bundle.aspect || "";
  }
  if (key === "tense") {
    return bundle.tense || "";
  }
  if (bundle.slot_values) {
    if (bundle.slot_values[key] !== undefined) return bundle.slot_values[key];
    if (tag && bundle.slot_values[tag] !== undefined) return bundle.slot_values[tag];
  }
  return "";
}

export default function Home() {
  const [manifest, setManifest] = useState<SlotManifest>(FALLBACK_MANIFEST);
  const [inputText, setInputText] = useState<string>("katateka");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [parseResponse, setParseResponse] = useState<ParseApiResponse | null>(null);
  const [selectedWordIndex, setSelectedWordIndex] = useState<number | null>(null);

  // Selected morpheme slot values for the active word
  const [selectedSlots, setSelectedSlots] = useState<Record<string, string>>({});

  useEffect(() => {
    async function loadManifest() {
      try {
        const res = await fetch("/api/manifest");
        if (res.ok) {
          const data = (await res.json()) as SlotManifest;
          if (data && Array.isArray(data.template) && data.template.length > 0) {
            setManifest(data);
          }
        }
      } catch (err: unknown) {
        console.error("Failed to fetch /api/manifest:", err);
      }
    }
    loadManifest();
  }, []);

  const columns: ColumnDef[] = useMemo(() => {
    return buildColumnDefs(manifest);
  }, [manifest]);

  const prefixColumns = useMemo(() => columns.filter((c) => c.category === "prefix"), [columns]);
  const suffixColumns = useMemo(() => columns.filter((c) => c.category === "suffix"), [columns]);

  const handleParse = async () => {
    if (!inputText.trim()) return;
    setIsLoading(true);
    setErrorMessage(null);
    setSelectedWordIndex(null);
    setSelectedSlots({});

    try {
      const res = await fetch("/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || `HTTP error ${res.status}`);
      }

      const data: ParseApiResponse = await res.json();
      setParseResponse(data);

      const firstValidIdx = data.results.findIndex((w) => w.totalParses > 0);
      if (firstValidIdx !== -1) {
        setSelectedWordIndex(firstValidIdx);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to parse text");
    } finally {
      setIsLoading(false);
    }
  };

  const activeWord: WordParseResult | null = useMemo(() => {
    if (selectedWordIndex === null || !parseResponse) return null;
    return parseResponse.results[selectedWordIndex] || null;
  }, [selectedWordIndex, parseResponse]);

  const handleSelectWord = (idx: number) => {
    setSelectedWordIndex(idx);
    setSelectedSlots({});
  };

  const allCandidateRoots: RootParseOption[] = useMemo(() => {
    if (!activeWord) return [];
    return activeWord.parseOptions;
  }, [activeWord]);

  // Filter valid candidate roots based on suffix/prefix selections and root selection
  const filteredCandidateRoots = useMemo(() => {
    return allCandidateRoots.filter((r) => {
      if (selectedSlots["root"] && r.root !== selectedSlots["root"]) {
        return false;
      }

      // Check if root has at least one valid prefix bundle matching prefix selections
      const hasMatchingPrefix = r.prefix_bundles.some((bundle) => {
        return prefixColumns.every((col) => {
          const selectedVal = selectedSlots[col.key];
          if (!selectedVal) return true;
          const bundleVal = getPrefixBundleValue(bundle, col.key, col.tag);
          return bundleVal === selectedVal;
        });
      });

      if (!hasMatchingPrefix) return false;

      // Check if root has at least one valid suffix bundle matching suffix selections
      const hasMatchingSuffix = r.suffix_bundles.some((bundle) => {
        return suffixColumns.every((col) => {
          const selectedVal = selectedSlots[col.key];
          if (!selectedVal) return true;
          const bundleVal = getSuffixBundleValue(bundle, col.key, col.tag);
          return bundleVal === selectedVal;
        });
      });

      return hasMatchingSuffix;
    });
  }, [allCandidateRoots, selectedSlots, prefixColumns, suffixColumns]);

  // Aggregate available choices for every slot across all currently valid roots and bundles
  const slotOptionsMap = useMemo(() => {
    const optionsMap: Record<string, string[]> = {};

    for (const col of columns) {
      const optionsSet = new Set<string>();

      if (col.category === "root") {
        for (const r of filteredCandidateRoots) {
          if (r.root) optionsSet.add(r.root);
        }
      } else if (col.category === "prefix") {
        for (const r of filteredCandidateRoots) {
          for (const bundle of r.prefix_bundles) {
            const matchesOther = prefixColumns.every((otherCol) => {
              if (otherCol.key === col.key) return true;
              const selectedVal = selectedSlots[otherCol.key];
              if (!selectedVal) return true;
              const bundleVal = getPrefixBundleValue(bundle, otherCol.key, otherCol.tag);
              return bundleVal === selectedVal;
            });

            if (matchesOther) {
              const val = getPrefixBundleValue(bundle, col.key, col.tag);
              if (val) optionsSet.add(val);
            }
          }
        }
      } else if (col.category === "suffix") {
        for (const r of filteredCandidateRoots) {
          for (const bundle of r.suffix_bundles) {
            const matchesOther = suffixColumns.every((otherCol) => {
              if (otherCol.key === col.key) return true;
              const selectedVal = selectedSlots[otherCol.key];
              if (!selectedVal) return true;
              const bundleVal = getSuffixBundleValue(bundle, otherCol.key, otherCol.tag);
              return bundleVal === selectedVal;
            });

            if (matchesOther) {
              const val = getSuffixBundleValue(bundle, col.key, col.tag);
              if (val) optionsSet.add(val);
            }
          }
        }
      }

      optionsMap[col.key] = Array.from(optionsSet);
    }

    return optionsMap;
  }, [columns, prefixColumns, suffixColumns, filteredCandidateRoots, selectedSlots]);

  // Calculate total remaining combinations
  const totalRemainingCombinations = useMemo(() => {
    let count = 0;
    for (const r of filteredCandidateRoots) {
      const validPrefixes = r.prefix_bundles.filter((bundle) => {
        return prefixColumns.every((col) => {
          const selectedVal = selectedSlots[col.key];
          if (!selectedVal) return true;
          const bundleVal = getPrefixBundleValue(bundle, col.key, col.tag);
          return bundleVal === selectedVal;
        });
      });

      const validSuffixes = r.suffix_bundles.filter((bundle) => {
        return suffixColumns.every((col) => {
          const selectedVal = selectedSlots[col.key];
          if (!selectedVal) return true;
          const bundleVal = getSuffixBundleValue(bundle, col.key, col.tag);
          return bundleVal === selectedVal;
        });
      });

      count += validPrefixes.length * validSuffixes.length;
    }
    return count;
  }, [filteredCandidateRoots, selectedSlots, prefixColumns, suffixColumns]);

  const handleSlotSelect = (slotName: string, value: string) => {
    setSelectedSlots((prev) => {
      const next = { ...prev };
      if (next[slotName] === value) {
        delete next[slotName]; // Toggle off
      } else {
        next[slotName] = value;
      }
      return next;
    });
  };

  const handleResetSlots = () => {
    setSelectedSlots({});
  };

  // Filter columns: only show columns that have more than 1 option (or if currently selected)
  const visibleColumns = useMemo(() => {
    return columns.filter((col) => {
      const options = slotOptionsMap[col.key] || [];
      const hasSelection = Boolean(selectedSlots[col.key]);
      // Hide column if there is 1 or fewer options AND user hasn't explicitly set it
      return options.length > 1 || hasSelection;
    });
  }, [columns, slotOptionsMap, selectedSlots]);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-8 font-sans flex flex-col space-y-6">
      <div className="max-w-7xl w-full mx-auto space-y-6 flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b border-slate-800 pb-3 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
              <span>Cherokee Morphological Parser</span>
              <span className="text-xs font-mono uppercase bg-indigo-950 text-indigo-400 border border-indigo-800 px-2.5 py-0.5 rounded-full">
                FST Morpheme Selector
              </span>
            </h1>
          </div>
        </header>

        {/* Top: Input Text Area */}
        <section className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Paste Cherokee Phonetic Text:
            </label>
            <span className="text-[11px] text-slate-500">Punctuation stripped automatically</span>
          </div>
          <div className="flex gap-3">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={2}
              placeholder="e.g. katateka tsigoliyeha..."
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
            />
            <button
              onClick={handleParse}
              disabled={isLoading || !inputText.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-medium px-6 rounded-lg transition text-sm flex items-center justify-center gap-2 shadow self-stretch"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Parsing...</span>
                </>
              ) : (
                "Parse"
              )}
            </button>
          </div>
          {errorMessage && (
            <div className="p-2.5 bg-red-950/70 border border-red-800 text-red-300 text-xs rounded-lg">
              {errorMessage}
            </div>
          )}
        </section>

        {/* Middle: Tokenized Words List */}
        {parseResponse && (
          <section className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold uppercase tracking-wider text-slate-300">
                Words ({parseResponse.results.length})
              </span>
              <span>Click a word to inspect and build its morphemes</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {parseResponse.results.map((result, idx) => {
                const isSelected = selectedWordIndex === idx;
                const hasParses = result.totalParses > 0;

                return (
                  <button
                    key={`${result.word}-${idx}`}
                    onClick={() => handleSelectWord(idx)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-mono border transition ${
                      isSelected
                        ? "bg-indigo-600 border-indigo-400 text-white shadow-md ring-2 ring-indigo-400/30"
                        : hasParses
                        ? "bg-slate-900 border-slate-700 hover:border-slate-500 text-slate-200"
                        : "bg-slate-900/40 border-slate-800/80 text-slate-500 hover:border-slate-700"
                    }`}
                  >
                    <span className="font-semibold">{result.word}</span>
                    <span
                      className={`text-[11px] px-1.5 py-0.2 rounded-full ${
                        hasParses
                          ? isSelected
                            ? "bg-indigo-800 text-indigo-100"
                            : "bg-emerald-950 text-emerald-400 border border-emerald-800"
                          : "bg-slate-800 text-slate-500"
                      }`}
                    >
                      {hasParses ? `${result.totalParses}` : "0"}
                    </span>
                  </button>
                );
              })}
            </div>
          </section>
        )}

        {/* Bottom: Morpheme Linear Slot Stacks */}
        {activeWord && (
          <section className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4 flex-1 flex flex-col">
            {/* Top Bar with Status & Assembly */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                <span className="text-sm font-bold text-slate-300">Word:</span>
                <span className="font-mono text-base font-bold text-indigo-400 bg-indigo-950/80 px-2.5 py-0.5 rounded border border-indigo-800">
                  {activeWord.cleanWord || activeWord.word}
                </span>
                <span className="text-xs text-slate-400">
                  Remaining Valid Parses:{" "}
                  <span className="font-bold text-emerald-400">{totalRemainingCombinations}</span> / {activeWord.totalParses}
                </span>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleResetSlots}
                  className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-md transition border border-slate-700"
                >
                  Reset Filters
                </button>
              </div>
            </div>

            {/* Single Line Assembly Preview */}
            <div className="bg-slate-950 px-4 py-2.5 rounded-lg border border-slate-800 flex items-center gap-2 overflow-x-auto text-xs font-mono">
              <span className="text-slate-500 uppercase text-[10px] font-bold tracking-wider mr-2 shrink-0">
                Assembly:
              </span>
              {columns.map((col) => {
                const val = selectedSlots[col.key];
                const available = slotOptionsMap[col.key] || [];
                const displayVal = val || (available.length === 1 ? available[0] : "*");
                const isResolved = Boolean(val) || available.length === 1;

                return (
                  <div
                    key={col.key}
                    className={`flex items-center gap-1.5 px-2 py-1 rounded border shrink-0 ${
                      col.category === "root"
                        ? "bg-amber-950/80 border-amber-800 text-amber-300"
                        : col.category === "prefix"
                        ? "bg-indigo-950/80 border-indigo-800 text-indigo-300"
                        : "bg-purple-950/80 border-purple-800 text-purple-300"
                    } ${!isResolved ? "opacity-60" : "font-bold"}`}
                  >
                    <span className="text-[10px] text-slate-400">{col.label}:</span>
                    <span>{displayVal}</span>
                  </div>
                );
              })}
            </div>

            {/* Linear Columns Container with Horizontal Scroll */}
            {activeWord.totalParses === 0 ? (
              <div className="p-8 text-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
                No valid FST parses found for surface form &quot;{activeWord.cleanWord}&quot;.
              </div>
            ) : (
              <div className="flex-1 overflow-x-auto pb-4">
                <div className="inline-flex gap-4 min-w-full items-stretch">
                  {visibleColumns.map((col) => {
                    const options = slotOptionsMap[col.key] || [];
                    const selectedVal = selectedSlots[col.key];

                    return (
                      <div
                        key={col.key}
                        className="w-56 shrink-0 flex flex-col bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow"
                      >
                        {/* Column Header */}
                        <div
                          className={`p-3 border-b border-slate-800 flex items-center justify-between ${
                            col.category === "root"
                              ? "bg-amber-950/30"
                              : col.category === "prefix"
                              ? "bg-indigo-950/30"
                              : "bg-purple-950/30"
                          }`}
                        >
                          <div>
                            <span className="text-xs font-bold text-slate-200 uppercase tracking-wide block">
                              {col.label}
                            </span>
                            <span className="text-[10px] text-slate-500">
                              {options.length} option{options.length !== 1 ? "s" : ""}
                            </span>
                          </div>
                          {selectedVal && (
                            <button
                              onClick={() => handleSlotSelect(col.key, selectedVal)}
                              className="text-[10px] bg-indigo-900 hover:bg-indigo-800 text-indigo-200 px-1.5 py-0.5 rounded border border-indigo-700"
                              title="Click to clear selection"
                            >
                              Clear
                            </button>
                          )}
                        </div>

                        {/* Tall Vertical Stack List */}
                        <div className="p-2 flex-1 overflow-y-auto max-h-[520px] space-y-1.5">
                          {options.map((val) => {
                            const isSelected = selectedVal === val;
                            return (
                              <button
                                key={val}
                                onClick={() => handleSlotSelect(col.key, val)}
                                className={`w-full text-left px-3 py-2 rounded-lg text-xs font-mono border transition ${
                                  isSelected
                                    ? col.category === "root"
                                      ? "bg-amber-600 border-amber-400 text-white font-bold shadow"
                                      : "bg-indigo-600 border-indigo-400 text-white font-bold shadow"
                                    : "bg-slate-900/90 border-slate-800/80 hover:border-slate-600 text-slate-300 hover:bg-slate-850"
                                }`}
                              >
                                <div className="truncate" title={val}>
                                  {col.key === "variant" ? `Variant ${val}` : val}
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
