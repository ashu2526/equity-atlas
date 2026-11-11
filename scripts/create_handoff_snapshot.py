#!/usr/bin/env python3
"""Build an auditable, sanitized Equity Atlas repository asset snapshot.

Includes public project code, scheduled workflows, research JSON and maintainer docs.
Intentionally excludes .git, untracked conversation attachments, local secrets and private
Google Sheets exports. For a private owner ZIP, add external files after export.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_DIRS = [".github", ".agents", "docs", "scripts", "data", "assets"]
INCLUDE_ROOT = [
    "README.md", "AGENTS.md", "DESIGN.md",
    "index.html", "sector.html", "sector-intelligence.html",
    "market-desk.html", "news-radar.html", "signals.html", "company-signals.html",
]
FORBIDDEN_NAMES = {".env", ".env.local", "credentials.json", "secrets.json", ".git"}
FORBIDDEN_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv", "node_modules"}

def safe(path: Path) -> bool:
    if path.name in FORBIDDEN_NAMES or path.suffix in {".pyc", ".pyo", ".key", ".pem"}:
        return False
    if any(part in FORBIDDEN_PARTS for part in path.parts):
        return False
    # Bundle code/data/docs only; prevent surprise release of credentials or personal attachments.
    return path.suffix.lower() in {".md", ".py", ".yml", ".yaml", ".json", ".html", ".csv", ".txt"}

def source_sha() -> str:
    if os.getenv("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown-offline-snapshot"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/tmp/equity-atlas-source")
    args = parser.parse_args()
    target = Path(args.output).resolve()
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    copied = []
    for name in INCLUDE_ROOT:
        source = ROOT / name
        if not source.exists():
            print("Warning: expected source missing:", name, file=sys.stderr)
            continue
        if source.is_file() and safe(source):
            out = target / name
            shutil.copy2(source, out)
            copied.append(out)

    for name in INCLUDE_DIRS:
        parent = ROOT / name
        if not parent.exists():
            continue
        for path in parent.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(ROOT)
            if not safe(relative):
                print("Excluded:", relative)
                continue
            dest = target / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            copied.append(dest)

    source_commit = source_sha()
    info = {
        "repository": "https://github.com/ashu2526/equity-atlas",
        "publicSite": "https://ashu2526.github.io/equity-atlas/",
        "sourceCommit": source_commit,
        "exportCreatedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "purpose": "Complete public source/data/documentation snapshot for development handoff",
        "externalNotIncluded": [
            "private Google Sheet exported workbook",
            "external ChatGPT automation settings or account state",
            "Git history (.git)",
            "API tokens, accounts, secrets or passwords",
            "live NSE/Polymarket/RSS endpoints",
        ],
    }
    (target / "SOURCE_COMMIT.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    copied.append(target / "SOURCE_COMMIT.json")

    entries = []
    for file in sorted(set(copied), key=lambda x: x.as_posix()):
        data = file.read_bytes()
        entries.append({
            "path": file.relative_to(target).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    (target / "FILE_SHA256_MANIFEST.json").write_text(
        json.dumps({"files": entries, "fileCount": len(entries)}, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "SHA256SUMS.txt").write_text(
        "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in entries),
        encoding="utf-8",
    )
    zip_path = target.parent / f"Equity_Atlas_Source_{dt.date.today().isoformat()}_{source_commit[:10]}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for file in sorted(target.rglob("*")):
            if file.is_file():
                z.write(file, file.relative_to(target).as_posix())

    print(json.dumps({
        "sourceCommit": source_commit,
        "fileCount": len(entries),
        "zipPath": str(zip_path),
        "zipBytes": zip_path.stat().st_size,
        "contains": [entry["path"] for entry in entries],
    }, indent=2))

if __name__ == "__main__":
    main()
