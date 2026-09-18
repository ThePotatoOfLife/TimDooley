#!/usr/bin/env python3
"""Scope legacy self-themed readers inside the generated public House artifact.

Historical source pages intentionally remain intact. This public-only pass gives the
shared House ownership of the document canvas while preserving each reader's local
cards, grids, FAQ families, evidence modules and semantic hooks.

Eligibility is policy-derived rather than filename-derived: any active registered
editorial/longform surface whose authored output still owns legacy global inline
`:root`, `body` or bare `a` styling is scoped, except pages already protected by the
shared reader/layout compatibility layer.
"""
from __future__ import annotations

from pathlib import Path

from house_public_surfaces import parent_chain, surface_rows
from house_style_scope import has_legacy_global_theme, scope_legacy_inline_theme

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"


def output_path_for_route(out: Path, route: str) -> Path:
    normalized = route if route.startswith("/") else "/" + route
    stripped = normalized.strip("/")
    if not stripped:
        return out / "index.html"
    if normalized.endswith("/"):
        return out / stripped / "index.html"
    return out / stripped


def convergence_family(surface_id: str) -> str:
    """Return a useful reporting family while keeping scoping policy generic."""
    chain_ids = {row["id"] for row in parent_chain(ROOT, surface_id)}
    if "faq" in chain_ids:
        return "FAQ"
    if "tim" in chain_ids and surface_id != "tim":
        return "Tim"
    return "House"


def is_scope_candidate(surface: dict, text: str) -> bool:
    """Return whether a registered public reader needs legacy global-theme scoping."""
    if surface.get("status") != "active" or surface.get("shell_type") not in {"editorial", "longform"}:
        return False
    if "reader.css" in text or "layout-guard.css" in text:
        return False
    return has_legacy_global_theme(text)


def patch_public_house_styles(out: Path = OUT) -> set[Path]:
    """Scope every registered legacy global inline theme in the generated artifact."""
    changed: set[Path] = set()
    for surface in surface_rows(ROOT):
        if surface.get("status") != "active" or surface.get("shell_type") not in {"editorial", "longform"}:
            continue

        page = output_path_for_route(out, surface["canonical_route"])
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        if not is_scope_candidate(surface, text):
            continue

        projected = scope_legacy_inline_theme(text)
        if projected == text:
            continue
        page.write_text(projected, encoding="utf-8")
        changed.add(page)
    return changed


def main() -> None:
    if not OUT.exists():
        raise SystemExit("_site does not exist; run scripts/build_site.py first")
    changed = patch_public_house_styles(OUT)
    print(f"Scoped legacy global themes on {len(changed)} registered House reader(s).")


if __name__ == "__main__":
    main()
