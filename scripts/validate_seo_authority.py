#!/usr/bin/env python3
"""Validate the official-site SEO authority and discovery contract.

This validator is intentionally narrow. It does not replace the existing SEO
pipeline validator; it locks the first-party authority signals that prevent the
project's own canonical site from becoming ambiguous to crawlers or AI search.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str, errors: list[str]) -> str:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing SEO authority file: {rel}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def require(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{owner} missing SEO authority marker: {marker}")


def main() -> int:
    errors: list[str] = []

    authority = read("scripts/build_site_authority.py", errors)
    readme = read("README.md", errors)
    tim = read("tim-dooley/index.html", errors)
    pages = read(".github/workflows/pages.yml", errors)

    if authority:
        try:
            ast.parse(authority)
        except SyntaxError as exc:
            errors.append(f"scripts/build_site_authority.py syntax error: {exc}")

    require(
        authority,
        (
            'AUTHORITY_FILE = "site-authority.json"',
            'OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"',
            '"relationship_to_project": "primary subject and project self-description"',
            "def validate_robots_sitemaps(",
            "def patch_llms(",
            "def patch_html_discovery(",
            'rel="alternate" type="application/json"',
        ),
        "build_site_authority.py",
        errors,
    )

    require(
        readme,
        (
            "Official project repository",
            "https://thepotatooflife.github.io/TimDooley/",
        ),
        "README.md",
        errors,
    )

    require(
        tim,
        (
            "Who is Tim Dooley?",
            "official project-owned archive",
            "project self-description",
            "documentary",
        ),
        "tim-dooley/index.html",
        errors,
    )

    require(
        pages,
        (
            "python scripts/validate_seo_authority.py",
            "python scripts/build_site_authority.py",
            "_site/site-authority.json",
            "site-authority.json' _site/llms.txt",
        ),
        "pages.yml",
        errors,
    )

    if errors:
        print("SEO AUTHORITY VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("SEO AUTHORITY VALIDATION PASSED")
    print("Official site · official repository · Tim subject route · crawler authority · machine discovery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
