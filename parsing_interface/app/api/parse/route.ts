import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import fs from "fs";
import path from "path";
import { ParseApiResponse, RootParseOption, WordParseResult } from "@/types/parser";

import { getRepoRoot } from "@/lib/repo";

function stripPunctuation(word: string): string {
  return word.replace(/^[\p{P}\p{S}\s]+|[\p{P}\p{S}\s]+$/gu, "").trim();
}

interface WordParseOptionsJson {
  surface: string;
  total_parses: number;
  distinct_roots_count: number;
  roots: RootParseOption[];
}

interface BatchParseResponseJson {
  results?: WordParseOptionsJson[];
}

const TIMEOUT_MS = 30000;

function parseBatchWordsCli(words: string[]): Promise<Map<string, WordParseOptionsJson>> {
  return new Promise((resolve, reject) => {
    if (words.length === 0) {
      resolve(new Map());
      return;
    }

    const repoRoot = getRepoRoot();
    const pythonBin = process.env.PYTHON_BIN || "python";

    const args = ["-m", "parse_chr_dict.parse_options", "--json", "--", ...words];
    const proc = spawn(pythonBin, args, {
      cwd: repoRoot,
      env: {
        ...process.env,
        PYTHONPATH: repoRoot,
        YAML_DIR: path.join(repoRoot, "chr-generated"),
      },
    });

    let stdout = "";
    let stderr = "";
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      proc.kill("SIGTERM");
      setTimeout(() => {
        try {
          proc.kill("SIGKILL");
        } catch {
          // ignore
        }
      }, 1000);
      reject(new Error(`parse_options subprocess timed out after ${TIMEOUT_MS}ms`));
    }, TIMEOUT_MS);

    proc.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    proc.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    proc.on("error", (err) => {
      if (timedOut) return;
      clearTimeout(timer);
      reject(err);
    });

    proc.on("close", (code) => {
      if (timedOut) return;
      clearTimeout(timer);

      const resultMap = new Map<string, WordParseOptionsJson>();

      if (code !== 0) {
        console.error(`parse_options batch execution failed (exit code ${code}):`, stderr);
      }

      try {
        if (stdout.trim()) {
          const parsed = JSON.parse(stdout) as BatchParseResponseJson | WordParseOptionsJson;
          if (parsed && "results" in parsed && Array.isArray(parsed.results)) {
            for (const item of parsed.results) {
              if (item && item.surface) {
                resultMap.set(item.surface, item);
              }
            }
          } else if (parsed && "surface" in parsed && (parsed as WordParseOptionsJson).surface) {
            const singleItem = parsed as WordParseOptionsJson;
            resultMap.set(singleItem.surface, singleItem);
          }
        }
      } catch (err) {
        console.error("Failed to parse CLI batch JSON output:", err, stdout);
      }

      resolve(resultMap);
    });
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const rawText: string = body.text || "";

    if (!rawText.trim()) {
      return NextResponse.json({ results: [], rawTokens: [] } satisfies ParseApiResponse);
    }

    // Split text by whitespace into tokens
    const rawTokens = rawText.trim().split(/\s+/);

    // Clean each word
    const wordMap = rawTokens.map((t) => ({
      raw: t,
      clean: stripPunctuation(t),
    }));

    // Parse unique non-empty words in a single batch CLI subprocess
    const uniqueCleanWords = Array.from(new Set(wordMap.map((w) => w.clean).filter((w) => w.length > 0)));

    const cliResultsMap = await parseBatchWordsCli(uniqueCleanWords);

    const results: WordParseResult[] = wordMap.map((w) => {
      if (!w.clean) {
        return {
          word: w.raw,
          cleanWord: w.clean,
          parseOptions: [],
          totalParses: 0,
        };
      }

      const wordData = cliResultsMap.get(w.clean);
      const roots = wordData?.roots || [];
      const totalParses = wordData?.total_parses ?? roots.reduce((sum, opt) => sum + (opt.total_parses || 0), 0);

      return {
        word: w.raw,
        cleanWord: w.clean,
        parseOptions: roots,
        totalParses,
      };
    });

    return NextResponse.json({
      results,
      rawTokens,
    } satisfies ParseApiResponse);
  } catch (error: unknown) {
    console.error("Error in /api/parse:", error);
    const message = error instanceof Error ? error.message : "Internal Server Error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
