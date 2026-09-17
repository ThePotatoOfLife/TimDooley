#!/usr/bin/env python3
"""Validate that generated and curated public pages return readers through the shared House."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from house_public_surfaces import surface_by_id
from house_shell import relative_href

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

REPRESENTATIVE_BRANCHES = {
    "tim": "tim",
    "traditions": "religion",
    "science": "science",
    "world": "world",
}

CURATED_HOUSE_REPRESENTATIVES = {
    "tim-dooley/index.html": "tim",
    "religion/index.html": "religion",
    "philosophy/index.html": "philosophy",
    "science/index.html": "science",
    "world/index.html": "world",
    "rooms/index.html": "rooms",
}


def require_href(text: str, href: str, label: str, errors: list[str]) -> None:
    if f'href="{href}"' not in text and f"href='{href}'" not in text:
        errors.append(label)


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

        for rel, surface_id in CURATED_HOUSE_REPRESENTATIVES.items():
            page = OUT / rel
            if not page.exists():
                errors.append(f"missing curated House representative: {rel}")
                continue
            text = page.read_text(encoding="utf-8", errors="replace")
            if 'class="site-housebar' not in text:
                errors.append(f"{rel} missing projected shared House bar")
            if 'class="site-breadcrumbs' not in text:
                errors.append(f"{rel} missing projected House breadcrumb")
            if 'class="page-nav"' in text:
                errors.append(f"{rel} still contains duplicate authored page-nav after House projection")
            surface = surface_by_id(ROOT, surface_id)
            if f'data-house-surface="{surface["id"]}"' not in text:
                errors.append(f"{rel} House projection does not identify surface {surface_id}")

        for branch_id, parent_surface_id in REPRESENTATIVE_BRANCHES.items():
            page = OUT / "topics" / branch_id / "index.html"
            if not page.exists():
                errors.append(f"missing generated topic page: {page.relative_to(ROOT)}")
                continue
            text = page.read_text(encoding="utf-8", errors="replace")
            parent = surface_by_id(ROOT, parent_surface_id)
            expected = relative_href(f"/topics/{branch_id}/", parent["canonical_route"])
            require_href(
                text,
                expected,
                f"topics/{branch_id}/ does not link back to {parent['canonical_route']} through the House route resolver",
                errors,
            )
            if "site-housebar" not in text:
                errors.append(f"topics/{branch_id}/ missing shared House bar")

        contexts = json.loads((ROOT / "knowledge" / "indexes" / "context-graph.json").read_text(encoding="utf-8"))
        clusters = contexts.get("clusters", [])
        if clusters:
            cid = str(clusters[0].get("id", "")).strip()
            if cid:
                page = OUT / "context" / cid / "index.html"
                if page.exists():
                    text = page.read_text(encoding="utf-8", errors="replace")
                    route = f"/context/{cid}/"
                    context_surface = surface_by_id(ROOT, "context")
                    explore_surface = surface_by_id(ROOT, "explore")
                    context_href = relative_href(route, context_surface["canonical_route"])
                    explore_href = relative_href(route, explore_surface["canonical_route"])
                    require_href(
                        text,
                        context_href,
                        f"context/{cid}/ does not route up to {context_surface['canonical_route']}",
                        errors,
                    )
                    require_href(
                        text,
                        explore_href,
                        f"context/{cid}/ does not retain Explore in shared House navigation",
                        errors,
                    )
                    if "site-housebar" not in text or "site-breadcrumbs" not in text:
                        errors.append(f"context/{cid}/ missing shared House orientation")

        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        record_branch = next((b for b in manifest.get("branches", []) if b.get("records")), None)
        if record_branch:
            page = OUT / "topics" / str(record_branch["id"]) / "index.html"
            text = page.read_text(encoding="utf-8", errors="replace") if page.exists() else ""
            if "/records/" not in text:
                errors.append(f"topics/{record_branch['id']}/ still renders canonical records as path-only text")

        if errors:
            print("Generated navigation validation FAILED")
            for error in errors:
                print(f" - {error}")
            return 1

        print("Generated navigation validation passed: curated gateways plus topic, record and context pages use shared House orientation.")
        return 0
    finally:
        if OUT.exists():
            shutil.rmtree(OUT)


if __name__ == "__main__":
    raise SystemExit(main())
