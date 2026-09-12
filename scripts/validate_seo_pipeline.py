#!/usr/bin/env python3
"""Validate the site-wide SEO and machine-discovery build contract.

SEO remains a projection concern: curated reader copy and the five-door public
hierarchy stay authoritative, while the build derives canonical crawler,
search, social and LLM surfaces from the final deployable artifact.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str, errors: list[str]) -> str:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing SEO pipeline file: {rel}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def require(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{owner} missing SEO contract marker: {marker}")


def main() -> int:
    errors: list[str] = []
    optimize = read("scripts/optimize_seo.py", errors)
    discovery = read("scripts/build_discovery.py", errors)
    machine_audit = read("scripts/check_machine_discoverability.py", errors)
    enrich = read("scripts/enrich_weak_descriptions.py", errors)
    quality = read(".github/workflows/quality-checks.yml", errors)
    pages = read(".github/workflows/pages.yml", errors)

    for rel, text in (
        ("scripts/optimize_seo.py", optimize),
        ("scripts/build_discovery.py", discovery),
        ("scripts/check_machine_discoverability.py", machine_audit),
        ("scripts/enrich_weak_descriptions.py", enrich),
    ):
        if text:
            try:
                ast.parse(text)
            except SyntaxError as exc:
                errors.append(f"{rel} syntax error: {exc}")

    require(
        optimize,
        (
            "fills only missing crawl/share metadata",
            'if not find_meta(text, name="description")',
            'if not find_link(text, "canonical")',
            "PUBLIC_BASE_URL",
            "canonical_is_internal",
            "urlparse",
            "core_record_routes",
            "link_known_record_paths",
            "git_lastmod_map",
            "site-index.json",
            "build_site_index",
            "rebuild_sitemaps",
            "BreadcrumbList",
            '"@type": "WebSite"',
            "is_noindex",
            "canonical_self_matches",
            'rel="alternate" type="application/json"',
            'rel="alternate" type="text/plain"',
            '"error_messages": errors',
            '"warning_messages": warnings',
            "seo-report.json",
        ),
        "optimize_seo.py",
        errors,
    )
    if "canonical.startswith(BASE_URL" in optimize:
        errors.append("SEO artifact audit still relies on brittle canonical string-prefix matching")

    require(
        discovery,
        (
            "PRIMARY_DOORS",
            '("tim", "Tim Dooley", "/tim-dooley/")',
            '("religion", "Religion", "/religion/")',
            '("philosophy", "Philosophy", "/philosophy/")',
            '("science", "Science", "/science/")',
            '("world_map", "World Map", "/world-map/")',
            "datetime.now(timezone.utc).date().isoformat()",
            'write("llms.txt"',
            '"site_index": BASE_URL + "/site-index.json"',
            '"sitemap_index": BASE_URL + "/sitemap-index.xml"',
            '"religion": BASE_URL + "/religion/"',
            '"philosophy": BASE_URL + "/philosophy/"',
            '"science": BASE_URL + "/science/"',
            '"world_map": BASE_URL + "/world-map/"',
            "User-agent: OAI-SearchBot",
            "Sitemap: {BASE_URL}/sitemap-index.xml",
        ),
        "build_discovery.py",
        errors,
    )
    if '"updated": "2026-09-09"' in discovery:
        errors.append("build_discovery.py still hard-codes a stale discovery updated date")

    require(
        machine_audit,
        (
            '"site-index.json"',
            '"sitemap-index.xml"',
            '"religion/index.html"',
            '"philosophy/index.html"',
            '"world-map/index.html"',
            "OAI-SearchBot",
            "noindex URLs must not appear in sitemaps",
            "canonical URL must match the page for indexable pages",
        ),
        "check_machine_discoverability.py",
        errors,
    )

    require(
        enrich,
        (
            "only touches descriptions shorter than 40 characters",
            "if len(current) >= 40",
            "first substantial paragraph",
        ),
        "enrich_weak_descriptions.py",
        errors,
    )

    for owner, text in (("quality-checks.yml", quality), ("pages.yml", pages)):
        require(
            text,
            (
                "python scripts/enrich_weak_descriptions.py",
                "python scripts/optimize_seo.py",
                "fetch-depth: 0",
                "seo-report.json",
            ),
            owner,
            errors,
        )

    # Quality CI must preserve exact SEO artifact diagnostics even when the gate
    # fails, then fail the job rather than silently continuing.
    require(
        quality,
        (
            "id: seo",
            "continue-on-error: true",
            "quality-seo-report",
            "Enforce SEO gate",
            "steps.seo.outcome == 'failure'",
        ),
        "quality-checks.yml",
        errors,
    )

    # The deployment audit must inspect exactly the artifact that will ship.
    prune = pages.find("Remove internal archive from Pages artifact")
    enrich_step = pages.find("Enrich weak page descriptions")
    optimize_step = pages.find("Optimize crawl, sharing and sitemap SEO")
    if prune < 0 or enrich_step < 0 or optimize_step < 0 or not (prune < enrich_step < optimize_step):
        errors.append("pages.yml must prune the internal archive before SEO normalization")

    # SEO/machine discovery must remain subordinate to reader architecture.
    home = read("index.html", errors)
    if 'href="seo/' in home or '>SEO<' in home:
        errors.append("SEO pipeline leaked into public navigation")
    if home.count('class="door"') and 'class="sections"' not in home:
        errors.append("homepage reader hierarchy marker is missing")

    if errors:
        print("SEO PIPELINE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("SEO PIPELINE VALIDATION PASSED")
    print(
        "SEO projection: five-door discovery · canonical-only crawl graph · "
        "source-backed freshness · structured data · social metadata · LLM indexes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
