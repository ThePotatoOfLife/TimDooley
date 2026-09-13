#!/usr/bin/env python3
"""Regression checks for current search-engine structured-data contracts.

These checks intentionally exercise the projection helpers directly so that SEO
regressions fail before the deploy artifact is published.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import apply_entity_intent_seo as semantic
import build_discovery as discovery
import optimize_seo as optimize

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise AssertionError(message)


def test_breadcrumb_contract() -> None:
    home_payload = json.loads(optimize.site_graph_schema(optimize.OUT / "index.html", "Home"))
    home_types = [node.get("@type") for node in home_payload.get("@graph", [])]
    if "BreadcrumbList" in home_types:
        fail("homepage must not emit a one-item BreadcrumbList")

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
    _, page = discovery.question_page({
        "id": "seo-contract-demo",
        "question": "What is the Potato of Life?",
        "short_answer": "A concise authored archive answer used only by this regression fixture.",
        "deep_answer": "A concise authored archive answer used only by this regression fixture.",
        "entities": ["Potato of Life"],
    })
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S | re.I)
    if not match:
        fail("question page must contain JSON-LD")
    payload = json.loads(match.group(1).replace("<\\/", "</"))
    if payload.get("@type") != "WebPage":
        fail("site-authored single-answer question pages must use WebPage, not FAQPage or QAPage")
    question = payload.get("mainEntity", {})
    answer = question.get("acceptedAnswer", {}) if isinstance(question, dict) else {}
    if question.get("@type") != "Question" or answer.get("@type") != "Answer":
        fail("question WebPage must expose Question -> acceptedAnswer -> Answer semantics")


def test_repository_robots_contract() -> None:
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8", errors="replace")
    expected = "Sitemap: https://thepotatooflife.github.io/TimDooley/sitemap-index.xml"
    if expected not in robots:
        fail("checked-in robots.txt must advertise the same sitemap index as the deployed artifact")


def main() -> int:
    checks = (
        test_breadcrumb_contract,
        test_primary_schema_contract,
        test_authored_question_schema_contract,
        test_repository_robots_contract,
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
