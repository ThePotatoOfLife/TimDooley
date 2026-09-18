#!/usr/bin/env python3
"""Validate the site-wide SEO and machine-discovery build contract.

SEO remains a projection concern: curated reader copy and the five-door public
hierarchy stay authoritative, while the build derives canonical crawler,
search, social, semantic and LLM surfaces from the final deployable artifact.
"""
from __future__ import annotations

import ast
from pathlib import Path

from validate_seo_2026_contract import main as validate_current_seo_contract
from validate_seo_authority import main as validate_seo_authority

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
    authority_builder = read("scripts/build_site_authority.py", errors)
    surface_resolver = read("scripts/house_public_surfaces.py", errors)
    machine_audit = read("scripts/check_machine_discoverability.py", errors)
    enrich = read("scripts/enrich_weak_descriptions.py", errors)
    strategy = read("scripts/seo_strategy.py", errors)
    semantic = read("scripts/apply_entity_intent_seo.py", errors)
    strategy_validator = read("scripts/validate_seo_strategy.py", errors)
    dedupe = read("scripts/dedupe_question_intents.py", errors)
    dedupe_validator = read("scripts/validate_question_intent_dedup.py", errors)
    current_contract = read("scripts/validate_seo_2026_contract.py", errors)
    quality = read(".github/workflows/quality-checks.yml", errors)
    pages = read(".github/workflows/pages.yml", errors)

    for rel, text in (
        ("scripts/optimize_seo.py", optimize),
        ("scripts/build_discovery.py", discovery),
        ("scripts/build_site_authority.py", authority_builder),
        ("scripts/house_public_surfaces.py", surface_resolver),
        ("scripts/check_machine_discoverability.py", machine_audit),
        ("scripts/enrich_weak_descriptions.py", enrich),
        ("scripts/seo_strategy.py", strategy),
        ("scripts/apply_entity_intent_seo.py", semantic),
        ("scripts/validate_seo_strategy.py", strategy_validator),
        ("scripts/dedupe_question_intents.py", dedupe),
        ("scripts/validate_question_intent_dedup.py", dedupe_validator),
        ("scripts/validate_seo_2026_contract.py", current_contract),
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
            "from house_public_surfaces import primary_gateway_rows",
            "parent_chain",
            "surface_by_route",
            "surface_rows",
            "surfaces_by_id",
            "build_house_index",
            "house_page_schema",
            "house_context",
            "house-index.json",
            'id="house-seo-schema"',
            '"room_authority": "data/house/rooms.json"',
            "PRIMARY_DOORS = tuple(",
            "primary_gateway_rows(ROOT)",
        ),
        "optimize_seo.py",
        errors,
    )
    if "canonical.startswith(BASE_URL" in optimize:
        errors.append("SEO artifact audit still relies on brittle canonical string-prefix matching")
    if '("world-map", "World Map")' in optimize:
        errors.append("optimize_seo.py still maintains stale World Map-as-fifth-Door taxonomy")

    require(
        strategy,
        (
            "class Strategy", "ROUTE_STRATEGIES", "RELATED", "def classify_route(", "def metadata_for(",
            "def schema_profile(", "def related_routes(", '"ProfilePage"', '"ScholarlyArticle"',
            '"CollectionPage"', '"Article"',
        ),
        "seo_strategy.py", errors,
    )
    for forbidden in ("sameAs", "divine identity"):
        if forbidden in strategy:
            errors.append(f"seo_strategy.py contains unsupported entity-schema marker: {forbidden}")

    require(
        semantic,
        (
            "classify_route", "metadata_for", "schema_profile", "related_routes", "entity-intent-schema",
            "related-context", "seo-intent-report.json", "summary_large_image", "No stable site-owned social image found",
            "strip_legacy_question_rich_result_schema", 'schema["headline"] = title',
            'entity.setdefault("@id", canonical_url + "#person")',
        ),
        "apply_entity_intent_seo.py", errors,
    )
    require(strategy_validator,("SEMANTIC SEO STRATEGY VALIDATION","seo_strategy.py","apply_entity_intent_seo.py","ProfilePage","ScholarlyArticle"),"validate_seo_strategy.py",errors)
    require(dedupe,("normalize_question","content_score","noindex,follow",'rel="canonical"',"location.replace","question-alias-report.json"),"dedupe_question_intents.py",errors)
    require(dedupe_validator,("QUESTION INTENT DEDUP VALIDATION","dedupe_question_intents.py","noindex,follow","question-alias-report.json"),"validate_question_intent_dedup.py",errors)
    require(current_contract,("SEO 2026 CONTRACT VALIDATION","test_breadcrumb_contract","test_primary_schema_contract","test_authored_question_schema_contract","test_repository_robots_contract"),"validate_seo_2026_contract.py",errors)

    require(
        surface_resolver,
        (
            'EXPECTED_PRIMARY_GATEWAY_IDS = ("tim", "religion", "philosophy", "science", "world")',
            'data" / "house" / "public-surfaces.json',
            "def primary_gateway_rows(",
        ),
        "house_public_surfaces.py", errors,
    )
    require(
        discovery,
        (
            "from house_public_surfaces import primary_gateway_rows",
            "PRIMARY_DOORS = tuple(",
            "primary_gateway_rows(ROOT)",
            "datetime.now(timezone.utc).date().isoformat()",
            'write("llms.txt"',
            '"site_index": BASE_URL + "/site-index.json"',
            '"house_index": BASE_URL + "/house-index.json"',
            "House topology index",
            '"sitemap_index": BASE_URL + "/sitemap-index.xml"',
            '"religion": BASE_URL + "/religion/"',
            '"philosophy": BASE_URL + "/philosophy/"',
            '"science": BASE_URL + "/science/"',
            '"world": BASE_URL + "/world/"',
            '"world_map": BASE_URL + "/world-map/"',
            "User-agent: OAI-SearchBot",
            "Sitemap: {BASE_URL}/sitemap-index.xml",
        ),
        "build_discovery.py", errors,
    )
    if '("tim", "Tim Dooley", "/tim-dooley/")' in discovery:
        errors.append("build_discovery.py still maintains an independent primary-door literal table")
    if '"updated": "2026-09-09"' in discovery:
        errors.append("build_discovery.py still hard-codes a stale discovery updated date")

    require(
        authority_builder,
        (
            "from house_public_surfaces import primary_gateway_rows",
            "primary_gateway_rows(ROOT)",
            'PRIMARY_ROUTES = {row["id"]: row["canonical_route"]',
        ),
        "build_site_authority.py", errors,
    )

    require(machine_audit,('"site-index.json"','"house-index.json"','"sitemap-index.xml"','"religion/index.html"','"philosophy/index.html"','"world-map/index.html"',"house-seo-schema","data/house/public-surfaces.json","data/house/rooms.json","OAI-SearchBot","noindex URLs must not appear in sitemaps","canonical URL must match the page for indexable pages"),"check_machine_discoverability.py",errors)
    require(enrich,("only touches descriptions shorter than 40 characters","if len(current) >= 40","first substantial paragraph","dedupe_question_intents","dedupe_result = dedupe_question_intents()","apply_entity_intent_seo","result = apply_entity_intent_seo()"),"enrich_weak_descriptions.py",errors)

    for owner, text in (("quality-checks.yml", quality), ("pages.yml", pages)):
        require(text,("python scripts/enrich_weak_descriptions.py","python scripts/optimize_seo.py","fetch-depth: 0","seo-report.json"),owner,errors)
    require(quality,("id: seo","continue-on-error: true","quality-seo-report","Enforce SEO gate","steps.seo.outcome == 'failure'"),"quality-checks.yml",errors)

    prune = pages.find("Remove internal archive from Pages artifact")
    enrich_step = pages.find("Enrich weak page descriptions")
    optimize_step = pages.find("Optimize crawl, sharing and sitemap SEO")
    if prune < 0 or enrich_step < 0 or optimize_step < 0 or not (prune < enrich_step < optimize_step):
        errors.append("pages.yml must prune the internal archive before SEO normalization")

    home = read("index.html", errors)
    if 'href="seo/' in home or '>SEO<' in home:
        errors.append("SEO pipeline leaked into public navigation")
    if home.count('class="door"') and 'class="sections"' not in home:
        errors.append("homepage reader hierarchy marker is missing")

    if not errors and validate_current_seo_contract():
        errors.append("current SEO structured-data/crawl contract failed")
    if not errors and validate_seo_authority():
        errors.append("SEO first-party authority/discovery contract failed")

    if errors:
        print("SEO PIPELINE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("SEO PIPELINE VALIDATION PASSED")
    print("SEO projection: House-derived five-door discovery · canonical-only crawl graph · deduplicated question intents · intent-aware metadata · typed structured data · House topology metadata · source-backed freshness · social metadata · related canonical context · LLM indexes · first-party authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
