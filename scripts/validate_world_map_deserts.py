#!/usr/bin/env python3
"""Validate the lazy ecological deserts/xeric physical layer."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "world-map-physical-layers.json"
DESERTS = ROOT / "world-map" / "3d-physical-deserts.js"
RUNTIME = ROOT / "world-map" / "3d-physical-layers.js"


def main() -> int:
    errors: list[str] = []
    manifest = {}
    if not MANIFEST.exists():
        errors.append("missing physical layer manifest")
    else:
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid physical layer manifest: {exc}")

    entries = {row.get("id"): row for row in manifest.get("entries", []) if isinstance(row, dict)}
    row = entries.get("physical.aridity") or {}
    if row.get("availability") != "current": errors.append("physical.aridity must be current")
    if row.get("load_policy") != "on_demand": errors.append("physical.aridity must remain on_demand")
    if row.get("kind") != "module": errors.append("physical.aridity must be module-backed")
    if row.get("module") != "./3d-physical-deserts.js": errors.append("physical.aridity must point to ./3d-physical-deserts.js")
    if row.get("controller") != "__potatoAtlasDeserts": errors.append("physical.aridity controller is not pinned")
    source = row.get("source") or {}
    if "Nature Conservancy" not in str(source.get("provider", "")): errors.append("desert source must name The Nature Conservancy")
    if "2009" not in str(source.get("version", "")): errors.append("desert source must expose its 2009 snapshot date")
    if "ecoregion" not in str(source.get("dataset", "")).lower(): errors.append("desert source must be described as ecoregions")
    note = str(row.get("status_note") or "").lower()
    if "not a continuous aridity index" not in note: errors.append("desert layer must disclose that it is not a continuous aridity index")

    if not DESERTS.exists():
        errors.append("missing world-map/3d-physical-deserts.js")
    else:
        text = DESERTS.read_text(encoding="utf-8", errors="replace")
        for token in (
            "TerrestrialEcoRegions/FeatureServer/0/query",
            "WWF_MHTNAM",
            "Deserts and Xeric Shrublands",
            "f=geojson",
            "countries-fill",
            "__potatoAtlasDeserts",
            "enable",
            "disable",
        ):
            if token not in text:
                errors.append(f"deserts module missing {token}")
        if "new MutationObserver(" in text or "setInterval(" in text:
            errors.append("deserts module must not poll or observe the DOM")
        node = shutil.which("node")
        if node:
            result = subprocess.run([node, "--check", str(DESERTS)], capture_output=True, text=True)
            if result.returncode:
                errors.append("deserts JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))

    if RUNTIME.exists() and "__potatoAtlasDeserts" not in RUNTIME.read_text(encoding="utf-8", errors="replace"):
        errors.append("physical runtime missing deserts controller compatibility marker")

    if errors:
        print("WORLD MAP DESERTS VALIDATION FAILED")
        for error in errors: print("-", error)
        return 1

    print("WORLD MAP DESERTS VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
