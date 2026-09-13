#!/usr/bin/env python3
"""Validate the official-site SEO authority and discovery contract.

This validator is intentionally narrow. It does not replace the existing SEO
pipeline validator; it locks the first-party authority signals that prevent the
project's own canonical site from becoming ambiguous to crawlers or AI search.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_SITE = "https://thepotatooflife.github.io/TimDooley/"
OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"


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


def validate_manifest(text: str, errors: list[str]) -> None:
    try:
        data = json.loads(text)
    except Exception as exc:
        errors.append(f"site-authority.json is invalid JSON: {exc}")
        return

    project = data.get("project", {})
    subject = data.get("primary_subject", {})
    routes = data.get("primary_routes", {})
    if project.get("official_site") != OFFICIAL_SITE:
        errors.append("site-authority.json official_site does not match canonical Pages URL")
    if project.get("official_repository") != OFFICIAL_REPOSITORY:
        errors.append("site-authority.json official_repository does not match canonical GitHub repository")
    if subject.get("name") != "Tim Dooley":
        errors.append("site-authority.json primary subject must be Tim Dooley")
    if subject.get("relationship_to_project") != "primary subject and project self-description":
        errors.append("site-authority.json must preserve the project self-description boundary")
    expected_routes = {"tim", "religion", "philosophy", "science", "world"}
    if set(routes) != expected_routes:
        errors.append(f"site-authority.json primary routes must be exactly {sorted(expected_routes)}")
    for key, value in routes.items():
        if not isinstance(value, str) or not value.startswith(OFFICIAL_SITE):
            errors.append(f"site-authority.json route {key} is not an official-site URL")


def main() -> int:
    errors: list[str] = []

    builder = read("scripts/build_site_authority.py", errors)
    manifest = read("site-authority.json", errors)
    readme = read("README.md", errors)
    home = read("index.html", errors)
    tim = read("tim-dooley/index.html", errors)

    if builder:
        try:
            ast.parse(builder)
        except SyntaxError as exc:
            errors.append(f"scripts/build_site_authority.py syntax error: {exc}")

    require(
        builder,
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

    if manifest:
        validate_manifest(manifest, errors)

    require(
        readme,
        (
            "Official project repository",
            OFFICIAL_SITE,
        ),
        "README.md",
        errors,
    )

    require(
        home,
        (
            "site-authority.json",
            OFFICIAL_REPOSITORY,
            '"@type":"Project"',
            "Tim Dooley & The Potato of Life",
        ),
        "index.html",
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
