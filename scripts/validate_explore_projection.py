#!/usr/bin/env python3
"""Validate registry-backed Explore reachability without weakening path safety."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "app.js"
PAGES = ROOT / ".github" / "workflows" / "pages.yml"
QUALITY = ROOT / ".github" / "workflows" / "quality-checks.yml"


def main() -> int:
    app = APP.read_text(encoding="utf-8")
    pages = PAGES.read_text(encoding="utf-8")
    quality = QUALITY.read_text(encoding="utf-8")
    errors: list[str] = []

    if "canonical-record-registry.json" not in app:
        errors.append("Explore runtime does not load the canonical record registry")
    if "canonicalRecordRegistry" not in app:
        errors.append("Explore runtime has no canonical registry state")
    if "occurrence.source" not in app and "o.source" not in app:
        errors.append("Explore runtime does not merge registry occurrence source paths into its allowlist")

    show_record = app.find("async function showRecord(path)")
    known_guard = app.find("if(!isKnownRecord(path))", show_record)
    fetch_call = app.find("loadResource(path)", show_record)
    if show_record < 0 or known_guard < 0 or fetch_call < 0 or known_guard > fetch_call:
        errors.append("showRecord must reject unknown hash paths before fetching the requested resource")

    registry_build = quality.find("python scripts/build_canonical_record_registry.py")
    site_build = quality.find("python scripts/build_site.py")
    if registry_build < 0 or site_build < 0 or registry_build > site_build:
        errors.append("Quality workflow must generate the canonical record registry before build_site.py")
    if "validated-pages-site" not in quality or "validated-pages-site" not in pages:
        errors.append("Explore projection must travel inside the validated Pages artifact")

    if errors:
        print("Explore projection validation FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Explore projection validation passed: registry-backed reachability extends the existing fail-closed record allowlist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
