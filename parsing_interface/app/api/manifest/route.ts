import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { FALLBACK_MANIFEST, SlotManifest } from "@/types/parser";
import { getRepoRoot } from "@/lib/repo";

export async function GET() {
  try {
    const yamlDir = process.env.YAML_DIR;
    let manifestPath = yamlDir ? path.join(yamlDir, "slots.json") : "";
    if (!manifestPath || !fs.existsSync(manifestPath)) {
      const repoRoot = getRepoRoot();
      manifestPath = path.join(repoRoot, "chr-generated", "slots.json");
    }

    if (fs.existsSync(manifestPath)) {
      const content = fs.readFileSync(manifestPath, "utf-8");
      const parsed = JSON.parse(content) as SlotManifest;
      return NextResponse.json(parsed);
    }

    return NextResponse.json(FALLBACK_MANIFEST);
  } catch (err: unknown) {
    console.error("Error reading slots.json manifest:", err);
    return NextResponse.json(FALLBACK_MANIFEST);
  }
}
