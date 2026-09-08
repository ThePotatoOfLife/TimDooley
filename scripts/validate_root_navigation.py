#!/usr/bin/env python3
"""Validate the center/root navigation contract before the site is built."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/root-navigation.json"


def fail(message: str) -> None:
    raise SystemExit(f"root-navigation: ERROR: {message}")


def main() -> None:
    if not MANIFEST.exists():
        fail("missing data/root-navigation.json")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("root") != "potato-of-life":
        fail("root must be potato-of-life")

    branches = manifest.get("branches", [])
    branch_ids = [b.get("id") for b in branches]
    if branch_ids != ["world", "axis"]:
        fail(f"top-level branches must be exactly ['world', 'axis'], got {branch_ids!r}")

    if any(b.get("id") in {"core", "texts"} for b in branches):
        fail("CORE and TEXTS must not be top-level branches")

    center_ids = {r.get("id") for r in manifest.get("center", {}).get("records", [])}
    required = {"tim-dooley", "potatoism", "thought", "canon"}
    missing = required - center_ids
    if missing:
        fail(f"center is missing {sorted(missing)}")

    # Only stable navigation destinations are validated here. Dynamic records are
    # generated from the repository index and intentionally have no hand-written href.
    stable = []
    for record in manifest.get("center", {}).get("records", []):
        href = record.get("href")
        if href and not href.startswith(("http://", "https://", "#")):
            stable.append(href)
    for branch in (manifest.get("world", {}), manifest.get("axis", {})):
        for collection in branch.get("collections", []):
            href = collection.get("legacy")
            if href and not href.startswith(("http://", "https://", "#")):
                stable.append(href)

    missing_files = [href for href in stable if not (ROOT / href).exists()]
    if missing_files:
        fail("manifest contains missing local destinations: " + ", ".join(sorted(set(missing_files))))

    print(
        "root-navigation: OK — "
        f"center={len(center_ids)}, top-level branches={branch_ids}, "
        f"stable destinations={len(stable)}"
    )


if __name__ == "__main__":
    main()
