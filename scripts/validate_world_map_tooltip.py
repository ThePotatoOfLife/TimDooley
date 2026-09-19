#!/usr/bin/env python3
"""Validate shared transient World Map tooltip ownership and lifecycle."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TOOLTIP = ROOT / "world-map" / "3d-tooltip.js"
HOVER = ROOT / "world-map" / "3d-hover.js"
AXIS = ROOT / "world-map" / "3d-axis.js"
FIELDS = ROOT / "world-map" / "3d-fields.js"
NETWORKS = ROOT / "world-map" / "3d-networks.js"
TEST = ROOT / "scripts" / "test_world_map_tooltip_lifecycle.mjs"
HOVER_TEST = ROOT / "scripts" / "test_world_map_hover_artifacts.mjs"


def main() -> int:
    errors: list[str] = []
    for path in (TOOLTIP, HOVER, AXIS, FIELDS, NETWORKS, TEST, HOVER_TEST):
        if not path.exists():
            errors.append(f"missing tooltip file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP TOOLTIP VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    tooltip = TOOLTIP.read_text(encoding="utf-8", errors="replace")
    hover = HOVER.read_text(encoding="utf-8", errors="replace")
    axis = AXIS.read_text(encoding="utf-8", errors="replace")
    fields = FIELDS.read_text(encoding="utf-8", errors="replace")
    networks = NETWORKS.read_text(encoding="utf-8", errors="replace")

    for token in (
        "function createTooltipService",
        "const popup = new PopupClass",
        "function nextGeneration",
        "function show",
        "function invalidate",
        "function clear",
        "staleSuppressions",
        "invalidations",
        "dragstart", "zoomstart", "rotatestart", "pitchstart",
        "potato-atlas-projection-change",
        "potato-atlas-style-generation",
    ):
        if token not in tooltip:
            errors.append(f"tooltip service missing marker: {token}")
    if tooltip.count("new PopupClass") != 1:
        errors.append(f"tooltip service must construct exactly one transient popup; found {tooltip.count('new PopupClass')}")

    for token in (
        "await import(versionedModule('./3d-tooltip.js'))",
        "window.__potatoAtlasTooltip",
        "tooltip.nextGeneration('country')",
        "tooltip.show('country'",
        "tooltip.invalidate('country-leave')",
        "tooltip.nextGeneration('capital')",
        "tooltip.invalidate('capital-leave')",
    ):
        if token not in hover:
            errors.append(f"hover runtime does not consume shared tooltip: {token}")
    if "const popup = new maplibregl.Popup" in hover:
        errors.append("hover runtime still constructs its own transient MapLibre popup")

    for label, source, owner in (
        ("Axis", axis, "axis"),
        ("Fields", fields, "fields"),
        ("Networks", networks, "networks"),
    ):
        if "new maplibregl.Popup" in source:
            errors.append(f"{label} still constructs a private transient MapLibre popup")
        for token in ("window.__potatoAtlasTooltip", f"tooltip.nextGeneration('{owner}')", f"tooltip.show('{owner}'", f"tooltip.clear('{owner}')"):
            if token not in source:
                errors.append(f"{label} does not consume the shared tooltip correctly: {token}")

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot verify tooltip behavior")
    else:
        for path in (TOOLTIP, HOVER, AXIS, FIELDS, NETWORKS):
            result = subprocess.run([node, "--check", str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: " + (result.stderr.strip() or result.stdout.strip()))
        for path, label in ((TEST, "tooltip lifecycle"), (HOVER_TEST, "hover ownership/race")):
            result = subprocess.run([node, str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"{label} regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map transient tooltip:")
    print("- one shared transient popup owner")
    print("- generation-based stale async suppression")
    print("- drag / zoom / rotate / pitch / projection invalidation")
    print("- country and fallback-capital hover migrated")
    print("- Axis, Fields and Networks transient hover migrated")
    print("- persistent click-owned popups remain separate")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP TOOLTIP VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP TOOLTIP VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
