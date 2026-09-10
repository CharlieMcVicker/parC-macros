import fs from "fs";
import path from "path";

export function getRepoRoot(): string {
  if (process.env.REPO_ROOT && fs.existsSync(process.env.REPO_ROOT)) {
    return path.resolve(process.env.REPO_ROOT);
  }
  const cwd = process.cwd();
  if (fs.existsSync(path.join(cwd, "chr-generated")) || fs.existsSync(path.join(cwd, "parse_chr_dict"))) {
    return path.resolve(cwd);
  }
  const parent = path.resolve(cwd, "..");
  if (fs.existsSync(path.join(parent, "chr-generated")) || fs.existsSync(path.join(parent, "parse_chr_dict"))) {
    return parent;
  }
  return parent;
}
