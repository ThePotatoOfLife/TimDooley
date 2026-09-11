#!/usr/bin/env python3
"""Validate the semantic navigation integration for the 3D Atlas."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "world-map" / "3d-capability-registry.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"


def check_js_syntax(path: Path, errors: list[str], warnings: list[str]) -> None:
    node = shutil.which("node")
    if not node:
        warnings.append(f"node unavailable; skipped syntax check for {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    try:
        result = subprocess.run([node, "--check", str(temp)], capture_output=True, text=True)
        if result.returncode:
            errors.append(
                f"{path.relative_to(ROOT)} JavaScript syntax check failed: "
                + (result.stderr.strip() or result.stdout.strip())
            )
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not REGISTRY.exists():
        errors.append("missing world-map/3d-capability-registry.js")
    else:
        text = REGISTRY.read_text(encoding="utf-8")
        for marker in (
            "window.__potatoAtlasCapabilities",
            "function register",
            "function activate",
            "function deactivate",
            "potato-atlas-capability-change",
            "potato-atlas-capability-registry-change",
            "baseSurface",
            "worldOverlays",
            "relationModes",
            "axisLens",
        ):
            if marker not in text:
                errors.append(f"capability registry missing marker: {marker}")
        check_js_syntax(REGISTRY, errors, warnings)

    if not BOOTSTRAP.exists():
        errors.append("missing world-map/3d-bootstrap.js")
    else:
        bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
        if "3d-capability-registry.js" not in bootstrap:
            errors.append("bootstrap does not load semantic capability registry")
        if "window.__potatoAtlasLoadModule = loadAfterPaint" not in bootstrap:
            errors.append("semantic navigation must preserve the shared lazy-module loader")

    for warning in warnings:
        print("WARNING:", warning)
    for error in errors:
        print("ERROR:", error)

    if errors:
        print(f"Spatial navigation validation failed with {len(errors)} error(s).")
        return 1
    print("Spatial navigation registry contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
