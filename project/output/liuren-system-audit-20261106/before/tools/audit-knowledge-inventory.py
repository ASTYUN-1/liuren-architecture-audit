"""Read-only inventory of curated knowledge; never scans accounts/env/customer reports."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re

TREES = [".opencode/skills", "案例项目库", "经验日志", "书籍库", "books", "八字经验库", "website-skills", "排盘工具魔改/js"]
FIELDS = ["占类", "课体", "发用", "三传", "日干", "类神", "技法", "反馈"]

def meta(line):
    match = re.match(r"^<!-- META:(.*?)-->", line)
    return dict((k.strip(), v.strip()) for k, v in (part.split("=", 1) for part in match.group(1).split("|") if "=" in part)) if match else {}

def inventory(root, code):
    src = code.read_text(encoding="utf-8")
    required = re.findall(r'"([^"\n]+)"', re.search(r'REQUIRED_SKILLS\s*=\s*\[(.*?)\]', src, re.S).group(1))
    allowed = set(required + re.findall(r'"([^"\n]+)"', re.search(r'allowedSkills\s*=\s*new Set\(\[(.*?)\]\)', src, re.S).group(1)))
    result = {"root": str(root), "runtimeSource": str(code), "requiredSkills": required, "allowedSkills": sorted(allowed), "trees": {}, "files": {}, "indexEntries": {}}
    for tree in TREES:
        base = root / tree
        summary = {"exists": base.is_dir(), "files": 0, "bytes": 0, "extensions": {}, "readableDocuments": 0, "skippedSymlinks": [], "metaDocuments": 0, "categoryCounts": {}, "missingFields": {}}
        extensions = collections.Counter(); categories = collections.Counter(); missing = collections.Counter()
        for directory, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in ["node_modules", ".git", "__pycache__", "test-results", "test-prompts"] and not (Path(directory)/d).is_symlink())
            for name in sorted(files):
                p = Path(directory) / name; rel = p.relative_to(root).as_posix()
                if p.is_symlink() or not p.is_file(): summary["skippedSymlinks"].append(rel); continue
                data = p.read_bytes(); summary["files"] += 1; summary["bytes"] += len(data); extensions[p.suffix.lower()] += 1
                record = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "readable": False}
                if p.suffix.lower() == ".md":
                    text = data.decode("utf-8-sig", errors="replace")
                    # Hash normalized text as well to distinguish newline-only drift.
                    record["normalizedHash"] = hashlib.sha256(text.replace("\r\n", "\n").encode()).hexdigest()
                    m = meta(text); record["meta"] = m
                    if tree == ".opencode/skills":
                        record["readable"] = p.relative_to(base).parts[0] in allowed and not name.startswith("_") and not re.search(r"test-results|test-prompts", rel)
                    elif tree in ["案例项目库", "经验日志"]:
                        record["readable"] = not name.startswith("_") and text.startswith("<!-- META:")
                        if record["readable"]:
                            summary["metaDocuments"] += 1; categories[m.get("占类", "(missing)")] += 1
                            for field in FIELDS:
                                if not m.get(field): missing[field] += 1
                    if name == "_metadata_index.md":
                        entries = []
                        lines = text.splitlines()
                        for i, line in enumerate(lines):
                            if not line.startswith("<!-- META:"): continue
                            linked = " ".join(lines[i:i+3])
                            links = re.findall(r'\]\(([^)]+\.md)\)', linked)
                            entries.append({"meta": meta(line), "links": links})
                        result["indexEntries"][rel] = entries
                summary["readableDocuments"] += int(record["readable"])
                result["files"][rel] = record
        summary["extensions"] = dict(extensions); summary["categoryCounts"] = dict(categories); summary["missingFields"] = dict(missing)
        result["trees"][tree] = summary
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--root", required=True); parser.add_argument("--code", required=True); parser.add_argument("--output", required=True)
    args = parser.parse_args(); result = inventory(Path(args.root), Path(args.code))
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"trees": result["trees"], "indexEntryCounts": {p: len(v) for p,v in result["indexEntries"].items()}}, ensure_ascii=False))
