#!/usr/bin/env python3
"""Validate centralized World Map style-generation ownership."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE = ROOT / "world-map" / "3d-style-lifecycle.js"
RENDER_STACK = ROOT / "world-map" / "3d-render-stack.js"
TEST = ROOT / "scripts" / "test_world_map_style_lifecycle.mjs"
PHYSICAL = {
    "physical-deserts": ROOT / "world-map" / "3d-physical-deserts.js",
    "physical-water": ROOT / "world-map" / "3d-physical-water.js",
    "physical-land-cover": ROOT / "world-map" / "3d-physical-land-cover.js",
    "physical-hydrology": ROOT / "world-map" / "3d-physical-hydrology.js",
}
GEOGRAPHY = {
    "places": ROOT / "world-map" / "3d-places.js",
    "subdivisions": ROOT / "world-map" / "3d-subdivisions.js",
}


def main() -> int:
    errors: list[str] = []
    for path in (LIFECYCLE, RENDER_STACK, TEST, *PHYSICAL.values(), *GEOGRAPHY.values()):
        if not path.exists():
            errors.append(f"missing style-lifecycle file: {path.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP STYLE LIFECYCLE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    lifecycle = LIFECYCLE.read_text(encoding="utf-8", errors="replace")
    render_stack = RENDER_STACK.read_text(encoding="utf-8", errors="replace")
    for token in (
        "function createStyleLifecycle",
        "function register",
        "function unregister",
        "function schedule",
        "function state",
        "map.on('styledata'",
        "potato-atlas-style-generation",
        "window.__potatoAtlasStyleLifecycle",
    ):
        if token not in lifecycle:
            errors.append(f"style lifecycle missing interface marker: {token}")
    if lifecycle.count("map.on('styledata'") != 1:
        errors.append("style lifecycle must own exactly one styledata listener")

    for token in (
        "const styleLifecycle = window.__potatoAtlasStyleLifecycle",
        "styleLifecycle.register('render-stack'",
        "restore:() => schedule('style-generation')",
    ):
        if token not in render_stack:
            errors.append(f"Render Stack style-lifecycle migration missing marker: {token}")
    if "map.on('styledata'" in render_stack:
        errors.append("Render Stack must not own a direct styledata listener after migration")
    if "window.__potatoAtlasStyleLifecycle =" in render_stack:
        errors.append("Render Stack must consume, not publish, the Style Lifecycle singleton")

    for owner, path in PHYSICAL.items():
        source = path.read_text(encoding="utf-8", errors="replace")
        for token in (
            "const styleLifecycle = window.__potatoAtlasStyleLifecycle",
            f"styleLifecycle.register('{owner}'",
            "if (!enabled || restoring) return",
        ):
            if token not in source:
                errors.append(f"{path.relative_to(ROOT)} style-lifecycle migration missing marker: {token}")
        if "map.on('styledata'" in source:
            errors.append(f"{path.relative_to(ROOT)} must not own a direct styledata listener")
        if "window.__potatoAtlasStyleLifecycle =" in source:
            errors.append(f"{path.relative_to(ROOT)} must consume, not publish, the Style Lifecycle singleton")

    for owner, path in GEOGRAPHY.items():
        source = path.read_text(encoding="utf-8", errors="replace")
        for token in (
            "if (!window.__potatoAtlasStyleLifecycle) await import('./3d-style-lifecycle.js')",
            f"styleLifecycle?.register?.('{owner}'",
            "async function restoreAfterStyleGeneration()",
        ):
            if token not in source:
                errors.append(f"{path.relative_to(ROOT)} style-generation recovery missing marker: {token}")
        if "map.on('styledata'" in source:
            errors.append(f"{path.relative_to(ROOT)} must restore through Style Lifecycle, not own styledata directly")

    active_style_listeners = []
    for path in sorted((ROOT / "world-map").glob("3d-*.js")):
        source = path.read_text(encoding="utf-8", errors="replace")
        if "map.on('styledata'" in source and path != LIFECYCLE:
            active_style_listeners.append(str(path.relative_to(ROOT)))
    if active_style_listeners:
        errors.append("direct styledata ownership remains outside Style Lifecycle: " + ", ".join(active_style_listeners))

    node = shutil.which("node")
    if not node:
        errors.append("node executable unavailable; cannot verify style lifecycle")
    else:
        for path in (LIFECYCLE, RENDER_STACK, *PHYSICAL.values(), *GEOGRAPHY.values()):
            result = subprocess.run([node, "--check", str(path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {path.relative_to(ROOT)}: " + (result.stderr.strip() or result.stdout.strip()))
        result = subprocess.run([node, str(TEST)], cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append("style lifecycle regression failed: " + (result.stderr.strip() or result.stdout.strip()))

    print("World Map style lifecycle:")
    print("- one style-generation owner")
    print("- deterministic priority-ordered restoration")
    print("- serializable generation/registration diagnostics")
    print("- Render Stack restoration migrated")
    print("- Deserts, Water, Land Cover and Hydrology restoration migrated")
    print("- Places and Subdivisions restore sources, layers and interaction ownership after style generations")
    print(f"Errors: {len(errors)}")
    if errors:
        print("WORLD MAP STYLE LIFECYCLE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP STYLE LIFECYCLE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
