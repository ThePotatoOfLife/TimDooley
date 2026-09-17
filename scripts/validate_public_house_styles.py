#!/usr/bin/env python3
"""Validate effective House style ownership in the generated public artifact."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from house_public_surfaces import surface_rows
from house_style_scope import has_legacy_global_theme
from patch_public_house_styles import convergence_family, output_path_for_route

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
INLINE_STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
FORBIDDEN = {
    ":root": re.compile(r"(?:^|})\s*:root\s*\{", re.I),
    "body": re.compile(r"(?:^|})\s*body\s*\{", re.I),
    "a": re.compile(r"(?:^|})\s*a\s*\{", re.I),
}


def owners(text: str) -> list[str]:
    css = "\n".join(INLINE_STYLE_RE.findall(text))
    return [name for name, pattern in FORBIDDEN.items() if pattern.search(css)]


def main() -> int:
    if not OUT.exists():
        print("Public House style validation FAILED")
        print(" - _site does not exist; run the public build and patch stages first")
        return 1

    errors: list[str] = []
    checked = 0
    scoped = 0
    for surface in surface_rows(ROOT):
        if surface.get("status") != "active" or surface.get("shell_type") not in {"editorial", "longform"}:
            continue
        family = convergence_family(surface["id"])
        if not family:
            continue

        page = output_path_for_route(OUT, surface["canonical_route"])
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        if "reader.css" in text or "layout-guard.css" in text:
            continue
        checked += 1

        remaining = owners(text)
        if remaining:
            errors.append(
                f"{page.relative_to(OUT)} ({family}) still owns global inline selectors in public output: {', '.join(remaining)}"
            )
        if has_legacy_global_theme(text):
            errors.append(f"{page.relative_to(OUT)} ({family}) still matches legacy global-theme detector after public patch")
        if "house-content-scope" not in text:
            errors.append(f"{page.relative_to(OUT)} ({family}) missing house-content-scope marker")
        else:
            scoped += 1
        if "site-system.css" not in text or 'class="site-housebar' not in text:
            errors.append(f"{page.relative_to(OUT)} ({family}) lost shared House shell while scoping legacy theme")

    if checked < 10:
        errors.append(f"expected at least 10 self-themed Tim/FAQ public readers, checked {checked}")
    if scoped != checked:
        errors.append(f"only {scoped}/{checked} self-themed Tim/FAQ readers carry the public scope marker")

    if errors:
        print("Public House style validation FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"Public House style validation passed: {scoped}/{checked} Tim/FAQ self-themed readers are locally scoped beneath the shared House.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
