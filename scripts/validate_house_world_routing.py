#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PEER_NAV_FILES = (
    "tim-dooley/index.html",
    "religion/index.html",
    "philosophy/index.html",
    "science/index.html",
)


def first_nav(text: str) -> str:
    match = re.search(r"<nav\b[^>]*>(.*?)</nav>", text, flags=re.I | re.S)
    return match.group(1) if match else ""


def main() -> int:
    errors: list[str] = []
    for rel in PEER_NAV_FILES:
        nav = first_nav((ROOT / rel).read_text(encoding="utf-8"))
        if 'href="../world-map/"' in nav:
            errors.append(f"{rel}: primary peer nav must not use World Map as fifth peer")

    access = json.loads((ROOT / "data/house/site-access.json").read_text(encoding="utf-8"))
    world_entries = [row for row in access.get("entries", []) if row.get("id") == "world"]
    if len(world_entries) != 1 or world_entries[0].get("route") != "/world/":
        errors.append("site-access.json: World must remain a unique name-first route at /world/")

    patch = (ROOT / "scripts/patch_home_discovery.py").read_text(encoding="utf-8")
    if "GITHUB_WORKFLOW" in patch and 'href="world-map/' in patch:
        errors.append("patch_home_discovery.py: deploy must not rewrite canonical World to World Map")

    shell = (ROOT / "scripts/validate_site_shell.py").read_text(encoding="utf-8")
    if "Pure validation entrypoint" not in shell:
        errors.append("validate_site_shell.py: public entrypoint must be validation-only")
    if 'href="world-map/"><strong>World</strong>' in shell:
        errors.append("validate_site_shell.py: validator entrypoint must not repair World routing")

    pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    expected = "['tim-dooley/','religion/','philosophy/','science/','world/']"
    if expected not in pages:
        errors.append("pages.yml: deploy smoke test must expect World as fifth primary route")
    if "test -f _site/world/index.html" not in pages:
        errors.append("pages.yml: deploy smoke test must assert _site/world/index.html exists")

    if errors:
        print("HOUSE WORLD ROUTING VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("HOUSE WORLD ROUTING VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
