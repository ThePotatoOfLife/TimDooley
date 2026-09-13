#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from atlas_model import build_model, by_id

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"


def require(text: str, marker: str, owner: str) -> None:
    if marker not in text:
        raise SystemExit(f"ATLAS PAGE FAILED: {owner} missing {marker}")


def forbid(text: str, marker: str, owner: str) -> None:
    if marker in text:
        raise SystemExit(f"ATLAS PAGE FAILED: {owner} contains forbidden {marker}")


def main() -> int:
    model = build_model()
    nodes = by_id(model)
    root_id = model["root_id"]

    css = OUT / "app" / "design-system.css"
    if not css.exists():
        raise SystemExit("ATLAS PAGE FAILED: shared design-system.css missing")

    landing = OUT / "atlas" / "index.html"
    if not landing.exists():
        raise SystemExit("ATLAS PAGE FAILED: atlas landing missing")
    landing_text = landing.read_text(encoding="utf-8")
    require(landing_text, '<main id="main" class="site-main">', "atlas landing")
    require(landing_text, 'class="page-atlas"', "atlas landing")
    require(landing_text, 'class="site-skip-link"', "atlas landing")

    for node_id, node in nodes.items():
        path = OUT / "atlas" / node_id / "index.html"
        if not path.exists():
            raise SystemExit(f"ATLAS PAGE FAILED: missing page for {node_id}")
        text = path.read_text(encoding="utf-8")
        require(text, '<main id="main" class="site-main">', node_id)
        require(text, 'class="record-page"', node_id)
        require(text, 'class="record-breadcrumbs"', node_id)
        require(text, 'class="record-archive"', node_id)
        require(text, '../../app/design-system.css', node_id)
        forbid(text, '../../archive/', node_id)
        forbid(text, '>Five doors<', node_id)

        north_count = text.count('class="record-north"')
        if node_id == root_id:
            if north_count != 0:
                raise SystemExit("ATLAS PAGE FAILED: root must not have North Gate")
        else:
            if north_count != 1:
                raise SystemExit(f"ATLAS PAGE FAILED: {node_id} must have exactly one North Gate")
            parent = nodes[node["north_parent"]]
            require(text, f'↑ {parent["title"]}', node_id)

        for child_id in node.get("children", []):
            child_path = OUT / "atlas" / child_id / "index.html"
            if not child_path.exists():
                raise SystemExit(f"ATLAS PAGE FAILED: generated child page missing {child_id}")

    print(f"ATLAS PAGE VALIDATION PASSED: {len(nodes)} node pages + landing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
