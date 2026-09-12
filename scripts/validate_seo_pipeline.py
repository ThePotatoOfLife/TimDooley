#!/usr/bin/env python3
"""Validate the conservative build-wide SEO normalization pipeline.

SEO is a projection concern: it may fill missing crawl/share metadata and make
existing canonical owners easier to discover, but it must not create another
reader hierarchy or rewrite curated five-door navigation.
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


def main() -> int:
    errors: list[str] = []
    optimize = read("scripts/optimize_seo.py", errors)
    enrich = read("scripts/enrich_weak_descriptions.py", errors)
    quality = read(".github/workflows/quality-checks.yml", errors)
    pages = read(".github/workflows/pages.yml", errors)

    for rel, text in (
        ("scripts/optimize_seo.py", optimize),
        ("scripts/enrich_weak_descriptions.py", enrich),
    ):
        if text:
            try:
                ast.parse(text)
            except SyntaxError as exc:
                errors.append(f"{rel} syntax error: {exc}")

    for marker in (
        "fills only missing crawl/share metadata",
        "if not find_meta(text, name=\"description\")",
        "if not find_link(text, \"canonical\")",
        "if not SCRIPT_LD_RE.search(text)",
        "core_record_routes",
        "link_known_record_paths",
        "git_lastmod_map",
        "optimize_sitemaps",
        "seo-report.json",
        '"errors": len(errors)',
    ):
        if marker not in optimize:
            errors.append(f"optimize_seo.py missing conservative SEO marker: {marker}")

    for marker in (
        "only touches descriptions shorter than 40 characters",
        "if len(current) >= 40",
        "first substantial paragraph",
    ):
        if marker not in enrich:
            errors.append(f"enrich_weak_descriptions.py missing preservation marker: {marker}")

    for owner, text in (("quality-checks.yml", quality), ("pages.yml", pages)):
        if "python scripts/enrich_weak_descriptions.py" not in text:
            errors.append(f"{owner} does not enrich weak descriptions")
        if "python scripts/optimize_seo.py" not in text:
            errors.append(f"{owner} does not run SEO normalization")

    if "fetch-depth: 0" not in pages:
        errors.append("pages.yml must fetch full history so sitemap lastmod can use source history")
    if "fetch-depth: 0" not in quality:
        errors.append("quality-checks.yml must fetch full history so SEO is tested like deployment")

    # The deployment audit must inspect exactly the artifact that will ship.
    prune = pages.find("Remove internal archive from Pages artifact")
    enrich_step = pages.find("Enrich weak page descriptions")
    optimize_step = pages.find("Optimize crawl, sharing and sitemap SEO")
    if prune < 0 or enrich_step < 0 or optimize_step < 0 or not (prune < enrich_step < optimize_step):
        errors.append("pages.yml must prune the internal archive before SEO normalization")

    # SEO must remain a build concern, not a sixth public door.
    home = read("index.html", errors)
    if 'href="seo/' in home or '>SEO<' in home:
        errors.append("SEO pipeline leaked into public navigation")

    if errors:
        print("SEO PIPELINE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("SEO PIPELINE VALIDATION PASSED")
    print("SEO projection: preserve curated copy · fill missing metadata · dedupe sitemaps · source-backed lastmod")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
