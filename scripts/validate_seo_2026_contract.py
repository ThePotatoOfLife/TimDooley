#!/usr/bin/env python3
"""Regression checks for current search-engine structured-data contracts.

These checks exercise the final projection and deploy-normalization helpers so
SEO regressions fail before the public artifact is published.
"""
from __future__ import annotations

import json
from pathlib import Path

import apply_entity_intent_seo as semantic
import optimize_seo as optimize
import validate_site_shell as site_shell

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://thepotatooflife.github.io/TimDooley"
OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"
SOURCE_AUTHORITY = BASE_URL + "/context/source-authority/"
AUTHORITY_MANIFEST = BASE_URL + "/site-authority.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def test_breadcrumb_contract() -> None:
    raw = optimize.site_graph_schema(optimize.OUT / "index.html", "Home")
    html = f'<script id="site-discovery-schema" type="application/ld+json">{raw}</script>'
    normalized = site_shell.normalize_home_structured_data(html)
    payload_text = normalized.split(">", 1)[1].rsplit("</script>", 1)[0]
    payload = json.loads(payload_text.replace("<\\/", "</"))
    home_types = [node.get("@type") for node in payload.get("@graph", [])]
    if "BreadcrumbList" in home_types:
        fail("final homepage artifact must not contain a one-item BreadcrumbList")

    internal_payload = json.loads(optimize.site_graph_schema(optimize.OUT / "science" / "index.html", "Science"))
    breadcrumbs = [node for node in internal_payload.get("@graph", []) if node.get("@type") == "BreadcrumbList"]
    if len(breadcrumbs) != 1:
        fail("internal pages must emit exactly one BreadcrumbList")
    items = breadcrumbs[0].get("itemListElement", [])
    if len(items) < 2:
        fail("internal BreadcrumbList must contain at least two ListItems")


def test_primary_schema_contract() -> None:
    paper_url = semantic.page_url("science/papers/demo")
    paper = semantic.primary_schema("science/papers/demo", "Demo research paper", "A sufficiently descriptive research summary.", paper_url)
    if paper.get("@type") != "ScholarlyArticle":
        fail("science paper must remain ScholarlyArticle")
    if paper.get("headline") != "Demo research paper":
        fail("Article and ScholarlyArticle schema must expose headline")
    if paper.get("isPartOf") != {"@id": semantic.BASE_URL + "/#website"}:
        fail("internal primary schema must reference the canonical WebSite node instead of redefining it")

    profile_url = semantic.page_url("tim-dooley")
    profile = semantic.primary_schema("tim-dooley", "Tim Dooley", "A sufficiently descriptive Tim Dooley profile.", profile_url)
    person = profile.get("mainEntity", {})
    if person.get("@type") != "Person" or person.get("@id") != profile_url + "#person" or person.get("url") != profile_url:
        fail("ProfilePage mainEntity must have a stable Person @id and canonical profile URL")


def test_authored_question_schema_contract() -> None:
    legacy = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[]}</script>'
    cleaned = semantic.strip_legacy_question_rich_result_schema(legacy)
    if "FAQPage" in cleaned or "QAPage" in cleaned:
        fail("site-authored answer pages must not retain FAQPage/QAPage rich-result markup")

    url = semantic.page_url("questions/what-is-the-potato-of-life")
    schema = semantic.primary_schema(
        "questions/what-is-the-potato-of-life",
        "What is the Potato of Life?",
        "A source-aware archive answer about the Potato of Life.",
        url,
    )
    if schema.get("@type") != "WebPage":
        fail("site-authored single-answer question pages must use WebPage")
    question = schema.get("mainEntity", {})
    if question.get("@type") != "Question" or question.get("name") != "What is the Potato of Life?":
        fail("question WebPage must expose its authored Question as mainEntity")


def test_repository_robots_contract() -> None:
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8", errors="replace")
    expected = "Sitemap: https://thepotatooflife.github.io/TimDooley/sitemap-index.xml"
    if expected not in robots:
        fail("checked-in robots.txt must advertise the same sitemap index as the deployed artifact")
    for agent in ("Googlebot", "Google-Extended", "bingbot", "OAI-SearchBot", "*"):
        if f"User-agent: {agent}" not in robots:
            fail(f"checked-in robots.txt must explicitly allow documented search/retrieval crawler: {agent}")
    if robots.count(expected) != 1:
        fail("checked-in robots.txt must advertise the canonical sitemap index exactly once")


def test_discovery_owner_contract() -> None:
    source = (ROOT / "scripts" / "build_discovery.py").read_text(encoding="utf-8", errors="replace")
    required = (
        'OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"',
        'SOURCE_AUTHORITY = BASE_URL + "/context/source-authority/"',
        'AUTHORITY_MANIFEST = BASE_URL + "/site-authority.json"',
        "def robots_text()",
        '"official_repository": OFFICIAL_REPOSITORY',
        '"source_authority": SOURCE_AUTHORITY',
        '"authority_manifest": AUTHORITY_MANIFEST',
    )
    for marker in required:
        if marker not in source:
            fail(f"build_discovery.py must own machine-discovery authority marker: {marker}")


def test_homepage_authority_contract() -> None:
    home = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
    sitemap = f'<link rel="sitemap" type="application/xml" href="{BASE_URL}/sitemap-index.xml">'
    if sitemap not in home:
        fail("homepage must advertise the canonical sitemap index, not a child sitemap")
    visible = home.split("<body", 1)[-1]
    for phrase in ("official project-owned public archive", "Potatoism", "Potatoverse"):
        if phrase not in visible:
            fail(f"homepage visible answer surface missing authority phrase: {phrase}")
    for url in (OFFICIAL_REPOSITORY, SOURCE_AUTHORITY):
        if url not in home:
            fail(f"homepage must expose official authority link: {url}")
    if AUTHORITY_MANIFEST not in home:
        fail("homepage must expose the authority manifest")


def main() -> int:
    checks = (
        test_breadcrumb_contract,
        test_primary_schema_contract,
        test_authored_question_schema_contract,
        test_repository_robots_contract,
        test_discovery_owner_contract,
        test_homepage_authority_contract,
    )
    failures: list[str] = []
    for check in checks:
        try:
            check()
        except Exception as exc:
            failures.append(f"{check.__name__}: {exc}")
    if failures:
        print("SEO 2026 CONTRACT VALIDATION FAILED")
        for message in failures:
            print("-", message)
        return 1
    print("SEO 2026 CONTRACT VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())