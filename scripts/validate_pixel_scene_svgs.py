#!/usr/bin/env python3
"""Validate canonical pixel-scene SVGs as strict XML plus required scene markers."""
from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

SCENES = {
    "app/site-tree-perspective.svg": (
        "purple starlit crown-space",
        "peach-gold descent",
        "huge blocky crown",
    ),
    "app/site-plane-organic-field.svg": (
        "stepped, pixel-art-like mountain silhouette",
        "first village",
        "second village",
    ),
    "app/site-below-root-field.svg": (
        "touchable surface / grass",
        "swamp pockets",
        "fire vents / forge pressure",
    ),
}


def main() -> int:
    errors: list[str] = []
    for rel, markers in SCENES.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing canonical pixel scene: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            errors.append(f"{rel}: invalid SVG/XML: {exc}")
            continue
        if not root.tag.endswith("svg"):
            errors.append(f"{rel}: document root is not <svg>")
        if root.get("viewBox") is None:
            errors.append(f"{rel}: missing viewBox")
        if 'shape-rendering="crispEdges"' not in text:
            errors.append(f"{rel}: missing crisp pixel rendering contract")
        for marker in markers:
            if marker not in text:
                errors.append(f"{rel}: missing scene marker {marker!r}")

    if errors:
        print(f"PIXEL SCENE SVG VALIDATION FAILED: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PIXEL SCENE SVG VALIDATION PASSED")
    print(f"{len(SCENES)} canonical scene plates parse as strict XML")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
