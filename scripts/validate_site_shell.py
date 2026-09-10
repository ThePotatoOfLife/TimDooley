#!/usr/bin/env python3
"""Verify the built Pages artifact for the current manifest-driven archive.

The validator writes ``site-shell-report.txt`` as a CI diagnostic artifact so a
failed deployment can be inspected without weakening the deployment gate.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
REPORT = ROOT / "site-shell-report.txt"


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON: {path.relative_to(SITE)} — {exc}")
        return {}


def require_text(text: str, required: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in required:
        if marker not in text:
            errors.append(f"{owner} missing current feature: {marker}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SITE.exists():
        errors.append("_site does not exist; build_site.py must run first")
        pages: list[Path] = []
    else:
        pages = sorted(SITE.rglob("*.html"))
        required_files = (
            "index.html",
            "manifest.json",
            "app/app.js",
            "app/style.css",
            "knowledge/indexes/context-graph.json",
            "knowledge/indexes/core-index.json",
            "world-map/index.html",
            "world-map/3d.html",
            "world-map/3d-app.js",
            "world-map/3d-hover.js",
            "world-map/3d-pathfinder.js",
            "world-map/3d-demography.js",
            "world-map/3d-evidence.js",
            "world-map/3d-axis.js",
            "world-map/3d-axis-depth.js",
            "world-map/3d-axis-operators.js",
            "data/world-map-3d-runtime.json",
            "data/world-relational-map.json",
            "data/atlas-projection-contract.json",
            "data/atlas-time-contract.json",
            "data/world-country-demography.json",
            "data/world-country-facts.json",
            "sitemap.xml",
            "llms.txt",
        )
        for rel in required_files:
            if not (SITE / rel).exists():
                errors.append(f"missing required site file: {rel}")

        manifest = load_json(SITE / "manifest.json", errors) if (SITE / "manifest.json").exists() else {}
        branches = {b.get("id") for b in manifest.get("branches", []) if b.get("id")}
        expected = {
            "tim", "son", "spirit", "transformation", "cosmology", "body",
            "traditions", "north", "world", "chronology", "works", "sources",
        }
        missing = sorted(expected - branches)
        if missing:
            errors.append(f"built manifest missing branches: {missing}")

        index = SITE / "index.html"
        if index.exists():
            text = index.read_text(encoding="utf-8", errors="replace")
            require_text(
                text,
                (
                    'id="reader"', 'id="branches"', "app/app.js", "app/style.css",
                    "application/ld+json", "llms.txt", "sitemap.xml", "POTATO",
                ),
                "index.html",
                errors,
            )
            for retired in ('id="root-tree"', 'id="center-frame"', 'id="frame-content"', "./root.js"):
                if retired in text:
                    warnings.append(f"index.html still contains retired reader marker: {retired}")
            if "<iframe" in text:
                errors.append("index.html contains retired iframe dependency")

        app = (SITE / "app/app.js").read_text(encoding="utf-8", errors="replace") if (SITE / "app/app.js").exists() else ""
        require_text(app, ("manifest.json", "context-graph.json", "showContext", "showRecord", "renderMarkdown"), "app/app.js", errors)

        # The World Relational Atlas is a first-class public surface and must survive every build.
        atlas_files = {
            "shell": SITE / "world-map/3d.html",
            "app": SITE / "world-map/3d-app.js",
            "hover": SITE / "world-map/3d-hover.js",
            "path": SITE / "world-map/3d-pathfinder.js",
            "demography": SITE / "world-map/3d-demography.js",
            "evidence": SITE / "world-map/3d-evidence.js",
        }
        atlas_text = {
            key: path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
            for key, path in atlas_files.items()
        }

        require_text(
            atlas_text["shell"],
            (
                "World Relational Atlas", 'id="map"', 'id="compare"', 'id="relationType"',
                'id="traceDepth"', 'src="./3d-hover.js"', 'src="./3d-pathfinder.js"',
                'src="./3d-demography.js"', 'src="./3d-evidence.js"', 'src="./3d-axis.js"',
                "Trace · 3 hops", "navigation handles rather than fake geographic locations",
            ),
            "world-map/3d.html",
            errors,
        )
        require_text(
            atlas_text["app"],
            (
                "semantic-hubs", "trace-hubs", "compare-hubs", "window.goCountry",
                "window.fitTrace", "function fitCodes", "function traceGraph", "Trace outward",
                "fitBounds", "searchParams.set('depth'", "visited.has(other)",
            ),
            "world-map/3d-app.js",
            errors,
        )
        require_text(
            atlas_text["hover"],
            (
                "GEO_LOCAL", "REST_LOCAL", "fallbackRestCountries", "capital-cities",
                "capital-city-labels", "countryHtml", "capitalHtml", "await import('./3d-app.js')",
                "return bestGeometryResponse()", "fetchJsonResponse(REST_LOCAL",
            ),
            "world-map/3d-hover.js",
            errors,
        )
        require_text(
            atlas_text["path"],
            (
                "function shortestPath", "world-country-facts.json", "searchParams.set('path'",
                "not necessarily the shortest or strongest relationship in the real world",
            ),
            "world-map/3d-pathfinder.js",
            errors,
        )
        require_text(
            atlas_text["demography"],
            ("Religious composition", "country-population-labels", "world-country-demography.json"),
            "world-map/3d-demography.js",
            errors,
        )
        require_text(
            atlas_text["evidence"],
            (
                "Eye · Evidence", "world-country-facts.json", "world-country-demography.json",
                "world-relational-map.json", "Missing coverage", "project interpretation is not empirical evidence",
            ),
            "world-map/3d-evidence.js",
            errors,
        )

        runtime = load_json(SITE / "data/world-map-3d-runtime.json", errors) if (SITE / "data/world-map-3d-runtime.json").exists() else {}
        if runtime and runtime.get("status") != "active renderer contract":
            errors.append("built world-map-3d-runtime must use current active renderer contract status")
        if runtime and runtime.get("compare_mode", {}).get("status") not in {"implemented", "implemented-basic"}:
            errors.append("built world-map runtime does not preserve implemented Compare status")
        if runtime and runtime.get("trace_mode", {}).get("status") not in {"implemented", "implemented-recursive-country", "implemented-basic"}:
            errors.append("built world-map runtime does not preserve recursive Trace status")
        if runtime and runtime.get("trace_mode", {}).get("maximum_depth") != 3:
            errors.append("built world-map runtime does not preserve Trace depth contract")
        if runtime:
            if runtime.get("projection_contract") != "data/atlas-projection-contract.json":
                errors.append("built world-map runtime does not point to the canonical projection contract")
            if runtime.get("time_contract") != "data/atlas-time-contract.json":
                errors.append("built world-map runtime does not point to the canonical time contract")
            if "experimental" in str(runtime.get("status", "")).lower():
                errors.append("built world-map runtime reintroduced retired experimental status wording")

        facts_path = SITE / "data/world-country-facts.json"
        if facts_path.exists():
            facts = load_json(facts_path, errors)
            if len(facts.get("countries", {})) != 195:
                errors.append("built country-facts snapshot must contain 195 canonical countries")
            if facts.get("capital_coverage", 0) < 190:
                errors.append("built country-facts capital coverage fell below 190")
            if facts.get("area_coverage", 0) < 190:
                errors.append("built country-facts area coverage fell below 190")

        demography_path = SITE / "data/world-country-demography.json"
        if demography_path.exists():
            demography = load_json(demography_path, errors)
            if len(demography.get("countries", {})) != 195:
                errors.append("built demography snapshot must contain 195 canonical countries")
            if demography.get("population_coverage", 0) < 190:
                errors.append("built population coverage fell below 190")
            if demography.get("religion_coverage", 0) < 150:
                errors.append("built religion coverage fell below 150")

        # Generated SEO surfaces must actually exist and contain real pages.
        topic_pages = list((SITE / "topics").glob("*/index.html")) if (SITE / "topics").exists() else []
        context_pages = list((SITE / "context").glob("*/index.html")) if (SITE / "context").exists() else []
        record_pages = list((SITE / "records").glob("*/index.html")) if (SITE / "records").exists() else []
        if len(topic_pages) < len(expected):
            errors.append(f"expected at least {len(expected)} topic pages; found {len(topic_pages)}")
        if not context_pages:
            errors.append("no generated context pages found")
        if not record_pages:
            errors.append("no generated record pages found")

        sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8", errors="replace") if (SITE / "sitemap.xml").exists() else ""
        for fragment in ("/topics/tim/", "/topics/son/", "/records/tim-dooley/", "/context/"):
            if fragment not in sitemap:
                errors.append(f"sitemap.xml missing expected route fragment: {fragment}")

        llms = (SITE / "llms.txt").read_text(encoding="utf-8", errors="replace") if (SITE / "llms.txt").exists() else ""
        llms_lower = llms.lower()
        for term in ("tim dooley", "potato of life", "generated canonical topics", "generated contextual constellations"):
            if term not in llms_lower:
                errors.append(f"llms.txt missing discovery term/section: {term}")

        # Validate local references inside generated HTML, resolving relative to each page.
        ref = re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''', re.I)
        bad: list[str] = []
        for html in pages:
            for raw in ref.findall(html.read_text(encoding="utf-8", errors="replace")):
                if raw.startswith(("http:", "https:", "mailto:", "javascript:", "data:")):
                    continue
                target = (html.parent / raw).resolve()
                try:
                    target.relative_to(SITE.resolve())
                except ValueError:
                    continue
                if not target.exists():
                    bad.append(f"{html.relative_to(SITE)} -> {raw}")
        if bad:
            errors.append(f"broken local references in built site: {len(bad)}; examples: {bad[:8]}")
        if not pages:
            errors.append("Pages artifact contains no HTML documents")

    lines = [
        f"Built HTML pages checked: {len(pages)}",
        f"Errors: {len(errors)} · Warnings: {len(warnings)}",
    ]
    lines.extend(f"WARNING: {warning}" for warning in warnings[:50])
    if errors:
        lines.append("SITE SHELL VALIDATION FAILED")
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("SITE SHELL VALIDATION PASSED")

    report = "\n".join(lines) + "\n"
    REPORT.write_text(report, encoding="utf-8")
    print(report, end="")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
