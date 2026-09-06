import argparse
import os
import sys
from pathlib import Path
from typing import Any

# Ensure YAML_DIR defaults to chr-generated
if "YAML_DIR" not in os.environ:
    repo_root = Path(__file__).parent.parent.resolve()
    gen_dir = repo_root / "chr-generated"
    if gen_dir.exists():
        os.environ["YAML_DIR"] = str(gen_dir)
        try:
            from parC.constants import set_yaml_dir
            set_yaml_dir(str(gen_dir))
        except ImportError:
            pass

import pynini

from parse_chr_dict.parse import get_just_root, get_parse_graph, parse


def get_arc_alignment(fst: pynini.Fst, surface_str: str) -> list[tuple[str, str]] | None:
    """
    Traverses the shortest path and maps input symbols to output symbols.
    Supports parC symbol tables and word FSAs as well as standard Pynini acceptors.
    """
    syms = fst.input_symbols()
    if syms is None:
        try:
            from parC.grammar.paradigm_compilation import get_symbol_table
            syms = get_symbol_table()
        except Exception:
            syms = None

    input_fst = None
    if syms is not None:
        try:
            from parC.grammar.paradigm_compilation import word_fsa
            input_fst = word_fsa(surface_str)
            input_fst.set_input_symbols(syms)
            input_fst.set_output_symbols(syms)
            if not fst.input_symbols():
                fst.set_input_symbols(syms)
        except Exception:
            pass

    if input_fst is None:
        input_fst = pynini.accep(surface_str)

    best_path = pynini.shortestpath(pynini.compose(input_fst, fst))

    if best_path.num_states() == 0:
        # Fallback to standard accep if word_fsa composition yielded no states
        if syms is not None:
            input_fst = pynini.accep(surface_str)
            best_path = pynini.shortestpath(pynini.compose(input_fst, fst))
            if best_path.num_states() == 0:
                return None
        else:
            return None

    # Topological traversal of the single best path
    alignment: list[tuple[str, str]] = []
    state = best_path.start()

    # Pre-fetch symbol tables if available, else use byte decodings
    isyms = best_path.input_symbols() or syms
    osyms = best_path.output_symbols() or syms

    while best_path.final(state) == pynini.Weight.zero(best_path.weight_type()):
        found = False
        for arc in best_path.arcs(state):
            in_char = isyms.find(arc.ilabel) if isyms and arc.ilabel != 0 else (chr(arc.ilabel) if arc.ilabel != 0 else "ε")
            out_char = osyms.find(arc.olabel) if osyms and arc.olabel != 0 else (chr(arc.olabel) if arc.olabel != 0 else "ε")

            alignment.append((in_char, out_char))
            state = arc.nextstate
            found = True
            break
        if not found:
            break

    return alignment


def _categorize_arc(in_char: str, out_char: str, current_stage: str) -> str:
    """Classifies an alignment arc into a morphological slot/stage."""
    if out_char.startswith("[AspectClass="):
        return "AspectClass"
    elif out_char.startswith("[Aspect="):
        return "Aspect"
    elif out_char.startswith("[Tense="):
        return "Tense"
    elif (
        out_char.startswith("[PrefixClass=")
        or out_char.startswith("[Pro=")
        or out_char.startswith("[H_alt=")
        or out_char in ("[WI]", "[DIST]", "[DIST=de]", "[DIST=di]")
        or out_char.startswith("[DIST=")
    ):
        return "Prefix"
    elif current_stage in ("Prefix", "Initial"):
        # Non-bracketed output symbol marks transition to root
        if not (out_char.startswith("[") and out_char.endswith("]")):
            return "Root"
        return "Prefix"
    elif current_stage == "Root":
        if not (out_char.startswith("[") and out_char.endswith("]")):
            return "Root"
        return current_stage
    else:
        # Suffix stages: retain current stage for untagged / epsilon suffix chars
        return current_stage


def segment_alignment(alignment: list[tuple[str, str]]) -> list[dict[str, Any]]:
    """
    Groups arc alignments into segmented morpheme units.
    Filters out boundary tags ([BOW], [EOW]) and associates each segment with its
    surface string and morphological tags or root text.
    """
    clean = [
        (i, o)
        for i, o in alignment
        if i not in ("[BOW]", "[EOW]") and o not in ("[BOW]", "[EOW]")
    ]

    current_stage = "Initial"
    segments: list[tuple[str, list[str], list[str]]] = []

    for in_char, out_char in clean:
        new_stage = _categorize_arc(in_char, out_char, current_stage)
        if not segments or segments[-1][0] != new_stage:
            segments.append((new_stage, [], []))
        current_stage = new_stage

        if in_char != "ε":
            segments[-1][1].append(in_char)
        if out_char != "ε" and (out_char.startswith("[") and out_char.endswith("]")):
            segments[-1][2].append(out_char)
        elif out_char != "ε" and new_stage == "Root":
            segments[-1][2].append(out_char)

    result = []
    for stage, chars, tags in segments:
        surface_part = "".join(chars)
        tag_info = "".join(tags) if stage == "Root" else tags
        result.append({
            "stage": stage,
            "surface": surface_part,
            "info": tag_info,
        })
    return result


def format_segmentation(segments: list[dict[str, Any]]) -> str:
    """Formats segmented morphemes into hyphenated surface form e.g. k-atat-e-k-a."""
    parts = [s["surface"] for s in segments if s["surface"]]
    return "-".join(parts)


def process_word(surface: str, fst: pynini.Fst | None = None, print_parses: bool = True) -> None:
    """Processes a single surface word: displays segmentation, arc alignment, and parses."""
    if fst is None:
        fst = get_parse_graph()

    alignment = get_arc_alignment(fst, surface)

    print("\n" + "=" * 60)
    print(f"WORD: {surface}")
    print("=" * 60)

    if alignment is None:
        print(f"No valid FST alignment / shortest path found for '{surface}'.")
    else:
        # 1. Automatic Segmentation
        segments = segment_alignment(alignment)
        hyphenated = format_segmentation(segments)
        print(f"\nSegmentation: {hyphenated}\n")
        print("Morpheme Breakdown:")
        for seg in segments:
            stage = seg["stage"]
            surf = seg["surface"] or "ε"
            info = seg["info"]
            print(f"  {stage:<14} : surface = {surf:<8} | {info}")

        # 2. Arc Alignment Table
        print("\nArc Alignment:")
        clean_alignment = [
            (i, o)
            for i, o in alignment
            if i not in ("[BOW]", "[EOW]") and o not in ("[BOW]", "[EOW]")
        ]
        for in_sym, out_sym in clean_alignment:
            print(f"  {in_sym:>4}  -->  {out_sym}")

    # 3. Full Parses (grouped by root, matching parse.py)
    if print_parses:
        parses = parse(surface)
        print(f"\nParses (total: {len(parses)}):")
        if not parses:
            print("  (no parses found)")
        else:
            groups: dict[str, list[str]] = {}
            for p in parses:
                if "[EOW]" in p:
                    parsed_word, _ = p.split("[EOW]", 1)
                else:
                    parsed_word = p
                if parsed_word.startswith("[BOW]"):
                    parsed_word = parsed_word[5:]
                root = get_just_root(parsed_word)
                if root not in groups:
                    groups[root] = []
                groups[root].append(parsed_word)

            root_list = sorted(groups.keys(), key=lambda x: (len(x), x))
            for root in root_list[:10]:
                print(f"  Root: {root}")
                for parsed_word in groups[root][:10]:
                    print(f"    {parsed_word}")
                if len(groups[root]) > 10:
                    print(f"    ... and {len(groups[root]) - 10} more for root '{root}'")
            if len(root_list) > 10:
                print(f"  ... and {len(root_list) - 10} more distinct roots")
            print(f"\nSummary: {len(parses)} parses found across {len(groups)} distinct roots.")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive segmentation and parsing tool for Cherokee verbs."
    )
    parser.add_argument(
        "words",
        nargs="*",
        help="Optional surface form(s) to segment and parse. If omitted, runs in interactive mode.",
    )
    args = parser.parse_args()

    fst = get_parse_graph()

    if args.words:
        for word in args.words:
            process_word(word.strip(), fst=fst)
        return

    # Interactive REPL mode (modeled after parse_chr_dict/parse.py)
    try:
        import readline  # noqa: F401
    except ImportError:
        pass

    print("Interactive segmentation & parsing - empty line or Ctrl-C/D to quit.")
    while True:
        try:
            surface = input("SEGMENT: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not surface:
            break
        process_word(surface, fst=fst)


if __name__ == "__main__":
    main()
