import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { ParseApiResponse, RootParseOption, WordParseResult } from "@/types/parser";

function stripPunctuation(word: string): string {
  return word.replace(/^[\p{P}\p{S}\s]+|[\p{P}\p{S}\s]+$/gu, "").trim();
}

interface WordParseOptionsJson {
  surface: string;
  total_parses: number;
  distinct_roots_count: number;
  roots: RootParseOption[];
}

function parseWordOptionsCli(word: string): Promise<WordParseOptionsJson | null> {
  return new Promise((resolve, reject) => {
    if (!word) {
      resolve(null);
      return;
    }

    const repoRoot = path.resolve(process.cwd(), "..");
    const pythonBin = process.env.PYTHON_BIN || "python";

    const args = ["-m", "parse_chr_dict.parse_options", "--json", word];
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

    proc.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    proc.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    proc.on("error", (err) => {
      reject(err);
    });

    proc.on("close", (code) => {
      if (code !== 0) {
        console.error(`parse_options failed for word "${word}":`, stderr);
        // Try parsing stdout anyway in case partial JSON was written
        try {
          const parsed = JSON.parse(stdout) as WordParseOptionsJson;
          resolve(parsed);
          return;
        } catch {
          resolve(null);
          return;
        }
      }

      try {
        const parsed = JSON.parse(stdout || "{}") as WordParseOptionsJson;
        resolve(parsed);
      } catch (err) {
        console.error(`Failed to parse CLI JSON for "${word}":`, err, stdout);
        resolve(null);
      }
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

    // Parse unique non-empty words concurrently
    const uniqueCleanWords = Array.from(new Set(wordMap.map((w) => w.clean).filter((w) => w.length > 0)));

    const parsedEntries = await Promise.all(
      uniqueCleanWords.map(async (word) => {
        const data = await parseWordOptionsCli(word);
        return [word, data] as const;
      })
    );

    const cliResultsMap = new Map<string, WordParseOptionsJson | null>(parsedEntries);

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
