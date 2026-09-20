#!/usr/bin/env python3
"""Validate that generated knowledge pages return readers to the right human surface."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = "https://thepotatooflife.github.io/TimDooley"

REPRESENTATIVE_BRANCHES = {
    "tim": "/tim-dooley/",
    "traditions": "/religion/",
    "science": "/science/",
    "world": "/world/",
}


def main() -> int:
    errors: list[str] = []
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_site.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr)
            print("Generated navigation validation FAILED")
            print(" - build_site.py failed")
            return 1

        for branch_id, parent_path in REPRESENTATIVE_BRANCHES.items():
            page = OUT / "topics" / branch_id / "index.html"
            if not page.exists():
                errors.append(f"missing generated topic page: {page.relative_to(ROOT)}")
                continue
            text = page.read_text(encoding="utf-8", errors="replace")
            expected = BASE_URL + parent_path
            if expected not in text:
                errors.append(f"topics/{branch_id}/ does not link back to {parent_path}")

        contexts = json.loads((ROOT / "knowledge" / "indexes" / "context-graph.json").read_text(encoding="utf-8"))
        clusters = contexts.get("clusters", [])
        if clusters:
            cid = str(clusters[0].get("id", "")).strip()
            if cid:
                page = OUT / "context" / cid / "index.html"
                if page.exists():
                    text = page.read_text(encoding="utf-8", errors="replace")
                    if BASE_URL + "/explore/" not in text:
                        errors.append(f"context/{cid}/ does not route back to Explore")

        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        record_branch = next((b for b in manifest.get("branches", []) if b.get("records")), None)
        if record_branch:
            page = OUT / "topics" / str(record_branch["id"]) / "index.html"
            text = page.read_text(encoding="utf-8", errors="replace") if page.exists() else ""
            if "/records/" not in text:
                errors.append(f"topics/{record_branch['id']}/ still renders canonical records as path-only text")

        inhabitants = json.loads((ROOT / "data" / "house" / "room-inhabitants.json").read_text(encoding="utf-8"))
        def walk(value):
            if isinstance(value, dict):
                yield value
                for child in value.values():
                    yield from walk(child)
            elif isinstance(value, list):
                for child in value:
                    yield from walk(child)
        record_routes = sorted({
            str(row.get("route")).strip()
            for row in walk(inhabitants)
            if isinstance(row, dict)
            and isinstance(row.get("route"), str)
            and str(row.get("route")).startswith("/records/")
        })
        for route in record_routes:
            rel = route.strip("/")
            page = OUT / rel / "index.html"
            if not page.exists():
                errors.append(f"registered House inhabitant record route missing after build_site.py: {route}")

        if errors:
            print("Generated navigation validation FAILED")
            for error in errors:
                print(f" - {error}")
            return 1

        print(f"Generated navigation validation passed: topic/context readers resolve correctly and {len(record_routes)} registered House record routes exist.")
        return 0
    finally:
        if OUT.exists():
            shutil.rmtree(OUT)


if __name__ == "__main__":
    raise SystemExit(main())
