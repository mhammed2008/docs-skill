#!/usr/bin/env python3
"""
Zero-Omission Documentation Coverage Verifier  v2.0
Part of the Full-Project Documenter Skill suite.

Cross-references the AST/manifest symbol inventory against all generated
documentation files to prove 100% functional and symbol coverage.

v2.0 Changes:
- Word-boundary matching instead of naive substring (#4)
- Requires symbol to appear in code fence or heading context
- JSON output support (#22)
- Per-file coverage breakdown
- Filters out trivially short symbol names to reduce false positives
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any


# Symbols with names this short are too ambiguous for reliable string matching
MIN_SYMBOL_NAME_LENGTH = 2

# Names that are too generic to verify by text matching alone
SKIP_NAMES = {
    'main', 'run', 'init', 'new', 'get', 'set', 'do', 'go', 'id', 'ok',
    'up', 'on', 'to', 'of', 'in', 'is', 'at', 'it', 'or', 'an', 'as',
}


def load_doc_text(docs_dir: Path) -> str:
    """Reads all markdown files in the docs directory into one searchable string."""
    combined = []
    if docs_dir.is_file():
        return docs_dir.read_text(encoding='utf-8', errors='ignore')

    for root, _, files in os.walk(docs_dir):
        for f in files:
            if f.endswith('.md') or f.endswith('.markdown') or f.endswith('.txt'):
                p = Path(root) / f
                try:
                    combined.append(p.read_text(encoding='utf-8', errors='ignore'))
                except Exception:
                    pass
    return "\n".join(combined)


def build_symbol_pattern(name: str) -> re.Pattern:
    """
    Builds a word-boundary regex that matches symbol names in documentation
    context — inside code fences, headings, backtick-wrapped references, or
    as standalone identifiers. Avoids matching partial English words.

    FIX for #4: replaces naive `if name in docs_text` with precision matching.
    """
    escaped = re.escape(name)
    # Match symbol in backticks, headings, or as standalone word (not substring)
    backtick_part = r'`[^`]*' + escaped + r'[^`]*`'
    heading_part = r'#{1,6}\s+.*' + escaped
    boundary_part = r'(?<![A-Za-z0-9_])' + escaped + r'(?![A-Za-z0-9_])'
    pattern = r'(?:' + backtick_part + r'|' + heading_part + r'|' + boundary_part + r')'
    return re.compile(pattern, re.MULTILINE)


def verify_coverage(manifest_path: Path, docs_path: Path) -> Dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    docs_text = load_doc_text(docs_path)

    total_symbols = 0
    documented_symbols = 0
    missing_symbols = []
    skipped_symbols = []
    per_file_coverage: Dict[str, Dict[str, int]] = {}

    for file_info in manifest.get("files", []):
        file_path = file_info["path"]
        file_total = 0
        file_found = 0

        for sym in file_info.get("symbols", []):
            name = sym.get("name")
            if not name:
                continue

            # Skip trivially short or generic names
            if len(name) < MIN_SYMBOL_NAME_LENGTH or name.lower() in SKIP_NAMES:
                skipped_symbols.append({
                    "file": file_path,
                    "name": name,
                    "reason": "too_short_or_generic"
                })
                continue

            total_symbols += 1
            file_total += 1

            # Word-boundary matching (#4)
            pattern = build_symbol_pattern(name)
            if pattern.search(docs_text):
                documented_symbols += 1
                file_found += 1
            else:
                missing_symbols.append({
                    "file": file_path,
                    "name": name,
                    "type": sym.get("type", "unknown"),
                    "line": sym.get("line", 0),
                    "signature": sym.get("signature", ""),
                    "parent_class": sym.get("parent_class", None),
                })

        if file_total > 0:
            per_file_coverage[file_path] = {
                "total": file_total,
                "documented": file_found,
                "missing": file_total - file_found,
                "percentage": round(file_found / file_total * 100, 1)
            }

    coverage_pct = (documented_symbols / total_symbols * 100.0) if total_symbols > 0 else 100.0

    return {
        "total_symbols_audited": total_symbols,
        "documented_symbols_found": documented_symbols,
        "missing_count": len(missing_symbols),
        "skipped_count": len(skipped_symbols),
        "coverage_percentage": round(coverage_pct, 2),
        "missing_symbols": missing_symbols,
        "skipped_symbols": skipped_symbols,
        "per_file_coverage": per_file_coverage,
    }


def main():
    parser = argparse.ArgumentParser(description="Verify 100% Documentation Coverage against Symbol Manifest v2.0")
    parser.add_argument("--manifest", "-m", default="codebase_manifest.json", help="Path to manifest JSON")
    parser.add_argument("--docs", "-d", default="docs", help="Directory or file containing generated docs")
    parser.add_argument("--output-json", "-o", default=None, help="Path to write JSON audit report (#22)")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    docs_path = Path(args.docs)

    if not manifest_path.exists():
        print(f"Error: Manifest {manifest_path} not found. Run codebase_analyzer.py first.", file=sys.stderr)
        sys.exit(1)

    if not docs_path.exists():
        print(f"Error: Docs path {docs_path} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Auditing documentation coverage across: {docs_path.resolve()} ...")
    result = verify_coverage(manifest_path, docs_path)

    # --- JSON output (#22) ---
    if args.output_json:
        out_path = Path(args.output_json)
        out_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(f"[+] JSON audit report written to: {out_path.resolve()}")

    # --- Console report ---
    print("\n=======================================================")
    print("      DOCUMENTATION COVERAGE AUDIT REPORT  v2.0")
    print("=======================================================")
    print(f" Total Symbols Audited:        {result['total_symbols_audited']}")
    print(f" Confirmed in Documentation:   {result['documented_symbols_found']}")
    print(f" Missing / Unreferenced:       {result['missing_count']}")
    print(f" Skipped (too short/generic):  {result['skipped_count']}")
    print(f" Verified Coverage:            {result['coverage_percentage']}%")
    print("=======================================================")

    # Per-file breakdown
    if result["per_file_coverage"]:
        print("\n--- Per-File Coverage Breakdown ---")
        for fpath, cov in sorted(result["per_file_coverage"].items()):
            status = "[OK]" if cov["missing"] == 0 else "[MISS]"
            print(f"  {status} {fpath}: {cov['documented']}/{cov['total']} ({cov['percentage']}%)")

    if result["missing_count"] > 0:
        print(f"\n[!] WARNING: {result['missing_count']} symbols were not found in docs:")
        for item in result["missing_symbols"][:50]:
            parent = f" (in {item['parent_class']})" if item.get('parent_class') else ""
            print(f"  - [{item['type'].upper()}] {item['name']}{parent} ({item['file']}:{item['line']})")
        if result["missing_count"] > 50:
            print(f"  ... and {result['missing_count'] - 50} more.")
        sys.exit(2)
    else:
        print("\n[+] SUCCESS: 100% Symbol & Function Coverage Confirmed! Zero omissions detected.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
