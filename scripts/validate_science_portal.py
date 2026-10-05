#!/usr/bin/env python3
"""Protect the Science hub and generated paper library from structural and semantic collapse."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from audit_science_quality import audit_tree

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = ROOT / "science" / "index.html"
LIBRARY_CSS = ROOT / "science" / "science-library.css"
PAPER_CSS = ROOT / "science" / "science-paper.css"
PAPERS_READER_CSS = ROOT / "science" / "science-papers.css"
PAPERS_READER_JS = ROOT / "science" / "science-papers.js"
BUILDER = ROOT / "scripts" / "build_science_catalog.py"
SITE = ROOT / "_site"
BUILT_PAGE = SITE / "science" / "index.html"
CATALOG = SITE / "science" / "catalog.json"
REPORT = ROOT / "science-portal-report.json"

SOURCE_MARKERS = (
    'id="science-search"',
    'id="science-field"',
    'id="science-type"',
    'id="science-results"',
    '<!-- SCIENCE_CATALOG_STATIC -->',
    'science-library.css',
    'science-library.js',
)

BUILDER_MARKERS = (
    "classify_fields",
    "classify_document_type",
    "qualifies_for_library",
    "render_paper_page",
    "render_paper_figures",
    "PAPERS_DIR",
    "Download source JSON",
    "View source on GitHub",
)

BUILT_MARKERS = (
    'id="science-search"',
    'id="science-field"',
    'id="science-type"',
    'id="science-results"',
    'class="science-record"',
)

# These markers are checked against a whitespace-free CSS representation below.
LIBRARY_CSS_MARKERS = (
    ".science-abstract{display:-webkit-box;",
    ".science-equation-preview{display:block;",
    ".science-featured-grid{display:grid;",
    ".science-record-actions.science-source{display:block;",
)


def require_markers(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{owner}: missing {marker!r}")


def validate_major_science_contract(errors: list[str]) -> None:
    """The project guide's major science families must remain reader-complete."""
    guide_path = ROOT / "knowledge" / "science" / "science-project-meaning-and-equation-guide-2026-09-12.json"
    if not guide_path.is_file():
        errors.append("missing major Science guide: knowledge/science/science-project-meaning-and-equation-guide-2026-09-12.json")
        return
    try:
        guide = json.loads(guide_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"could not parse major Science guide: {exc}")
        return
    guides = guide.get("project_guides")
    if not isinstance(guides, list) or not guides:
        errors.append("major Science guide has no project_guides")
        return
    seen = 0
    for item in guides:
        if not isinstance(item, dict):
            continue
        project = str(item.get("project") or "Unnamed project")
        owner = str(item.get("owner") or "").strip()
        if not owner:
            errors.append(f"{project}: project guide missing owner")
            continue
        path = ROOT / owner
        if not path.is_file():
            errors.append(f"{project}: missing owner record {owner}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{project}: could not parse {owner}: {exc}")
            continue
        seen += 1
        if not isinstance(data.get("equation_context"), dict) or not data["equation_context"]:
            errors.append(f"{project}: missing equation_context")
        if not isinstance(data.get("term_map"), dict) or not data["term_map"]:
            errors.append(f"{project}: missing term_map")
        if not isinstance(data.get("paper_figures"), list) or not data["paper_figures"]:
            errors.append(f"{project}: missing paper_figures")
        has_failure = any(data.get(key) not in (None, "", [], {}) for key in (
            "failure_conditions",
            "falsification_and_failure_conditions",
            "hard_boundaries",
            "limitations",
        ))
        if not has_failure:
            errors.append(f"{project}: missing failure/boundary conditions")
        context = data.get("equation_context") if isinstance(data.get("equation_context"), dict) else {}
        has_observable = any(data.get(key) not in (None, "", [], {}) for key in (
            "observables",
            "observable_program",
            "testing_program",
            "experimental_ladder",
        )) or bool(context.get("observable_consequence"))
        if not has_observable:
            errors.append(f"{project}: missing observable consequence/testing path")
    if seen < 17:
        errors.append(f"major Science contract covered only {seen} project records; expected at least 17")


def validate_science_svg_assets(errors: list[str]) -> None:
    """Ensure paper diagrams remain accessible, scalable publication figures."""
    seen: set[str] = set()
    science_dir = ROOT / "knowledge" / "science"
    for source in science_dir.rglob("*.json"):
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
        except Exception:
            continue
        for figure in data.get("paper_figures") or []:
            if not isinstance(figure, dict):
                continue
            asset = str(figure.get("asset") or "").strip().lstrip("/")
            if not asset.endswith(".svg") or asset in seen:
                continue
            seen.add(asset)
            path = ROOT / asset
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            compact = "".join(text.split())
            try:
                root = ET.fromstring(text)
            except ET.ParseError as exc:
                errors.append(f"{asset}: malformed SVG XML: {exc}")
                continue
            view_box = root.attrib.get("viewBox") or root.attrib.get("viewbox")
            if not view_box:
                errors.append(f"{asset}: SVG paper figure missing scalable viewBox")
            else:
                try:
                    parts = [float(part) for part in view_box.replace(",", " ").split()]
                    if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0:
                        raise ValueError
                except ValueError:
                    errors.append(f"{asset}: invalid SVG viewBox {view_box!r}")
            if "<title" not in text or "</title>" not in text:
                errors.append(f"{asset}: SVG paper figure missing <title>")
            if "<desc" not in text or "</desc>" not in text:
                errors.append(f"{asset}: SVG paper figure missing <desc>")
            if 'role="img"' not in compact and "role='img'" not in compact:
                errors.append(f"{asset}: SVG paper figure missing role=img")


def validate_paper_figure_assets(errors: list[str]) -> None:
    science_dir = ROOT / "knowledge" / "science"
    for source in science_dir.rglob("*.json"):
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
        except Exception:
            continue
        figures = data.get("paper_figures")
        if not isinstance(figures, list):
            continue
        for index, figure in enumerate(figures, 1):
            if not isinstance(figure, dict):
                errors.append(f"{source.relative_to(ROOT)}: paper_figures[{index}] must be an object")
                continue
            asset = str(figure.get("asset") or "").strip().lstrip("/")
            if not asset:
                errors.append(f"{source.relative_to(ROOT)}: paper_figures[{index}] missing asset")
                continue
            asset_path = ROOT / asset
            if not asset_path.is_file():
                errors.append(f"{source.relative_to(ROOT)}: missing paper figure asset {asset}")
            if not str(figure.get("alt") or "").strip():
                errors.append(f"{source.relative_to(ROOT)}: paper figure {asset} missing alt text")
            if not str(figure.get("caption") or "").strip():
                errors.append(f"{source.relative_to(ROOT)}: paper figure {asset} missing caption")


def github_error(path: str, title: str, message: str) -> None:
    """Emit a GitHub Actions annotation while remaining harmless outside CI."""
    safe_path = str(path).replace("\r", " ").replace("\n", " ")
    safe_title = str(title).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    safe_message = str(message).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::error file={safe_path},title={safe_title}::{safe_message}")


def write_report(errors: list[str], semantic: dict, payload: dict | None) -> None:
    REPORT.write_text(
        json.dumps(
            {
                "schema": "science-portal-report/v1",
                "ok": not errors,
                "errors": errors,
                "semantic_hard_failure_count": semantic.get("hard_failure_count", 0),
                "semantic_advisory_count": semantic.get("advisory_count", 0),
                "catalog_record_count": payload.get("record_count") if isinstance(payload, dict) else None,
                "catalog_qualifying_count": payload.get("qualifying_count") if isinstance(payload, dict) else None,
                "catalog_paper_count": len(payload.get("papers", [])) if isinstance(payload, dict) and isinstance(payload.get("papers"), list) else None,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    errors: list[str] = []
    payload: dict | None = None

    validate_paper_figure_assets(errors)
    validate_science_svg_assets(errors)
    validate_major_science_contract(errors)

    semantic = audit_tree()
    if semantic.get("hard_failure_count"):
        errors.append(f"semantic Science audit has {semantic['hard_failure_count']} hard failure(s)")
        for failure in semantic.get("parse_failures", []):
            message = str(failure.get("message") or "Science JSON parse failure")
            errors.append(f"semantic audit {failure.get('code')}: {message}")
            github_error("knowledge/science", f"Science quality: {failure.get('code')}", message)
        for record in semantic.get("hard_failures", []):
            for failure in record.get("hard_failures", []):
                message = str(failure.get("message") or "Science semantic quality failure")
                errors.append(
                    f"semantic audit {record.get('file')}: {failure.get('code')} - {message}"
                )
                github_error(
                    f"knowledge/science/{record.get('file')}",
                    f"Science quality: {failure.get('code')}",
                    message,
                )

    for path in (SOURCE_PAGE, LIBRARY_CSS, PAPER_CSS, PAPERS_READER_CSS, PAPERS_READER_JS, BUILDER):
        if not path.exists():
            errors.append(f"missing required Science component: {path.relative_to(ROOT)}")

    source = SOURCE_PAGE.read_text(encoding="utf-8", errors="replace") if SOURCE_PAGE.exists() else ""
    css = LIBRARY_CSS.read_text(encoding="utf-8", errors="replace") if LIBRARY_CSS.exists() else ""
    builder = BUILDER.read_text(encoding="utf-8", errors="replace") if BUILDER.exists() else ""
    if re.search(r"science-(?:paper|papers)\.(?:css|js)\?v=20\d{6}", builder):
        errors.append("scripts/build_science_catalog.py: hard-coded Science reader cache versions must use content hashes")
    require_markers(
        builder,
        (
            "def asset_version(",
            'ROOT / "_site" / relative_path',
            'asset_version("science/science-paper.css")',
            'asset_version("science/science-papers.css")',
            'asset_version("science/science-papers.js")',
            '"Scientific Atlas"',
            '"Methods / Validation"',
            '"Mathematical Research Note"',
        ),
        "scripts/build_science_catalog.py",
        errors,
    )
    if re.search(r"science-library\.(?:css|js)\?v=20\d{6}", source):
        errors.append("science/index.html: Science homepage assets must use build fingerprints, not dated cache keys")
    build_site_path = ROOT / "scripts" / "build_site.py"
    build_site_text = build_site_path.read_text(encoding="utf-8", errors="replace") if build_site_path.exists() else ""
    require_markers(
        build_site_text,
        ('"science/science-library.css"', '"science/science-library.js"'),
        "scripts/build_site.py",
        errors,
    )
    require_markers(source, SOURCE_MARKERS, "science/index.html", errors)
    require_markers(builder, BUILDER_MARKERS, "scripts/build_science_catalog.py", errors)
    compact_css = "".join(css.split())
    require_markers(compact_css, LIBRARY_CSS_MARKERS, "science/science-library.css", errors)
    paper_css = PAPER_CSS.read_text(encoding="utf-8", errors="replace") if PAPER_CSS.exists() else ""
    require_markers(
        "".join(paper_css.split()),
        (".paper-page{", ".paper-subtitle{", ".paper-toc{", ".paper-figure{", ".paper-equation-block{", ".paper-table{", ".paper-figure-open{", "@mediaprint{"),
        "science/science-paper.css",
        errors,
    )
    papers_reader_css = PAPERS_READER_CSS.read_text(encoding="utf-8", errors="replace") if PAPERS_READER_CSS.exists() else ""
    require_markers(
        "".join(papers_reader_css.split()),
        (".papers-reader{", ".core-list{", ".paper-entry{", ".papers-shelf{", ".papers-index{", ".papers-find{"),
        "science/science-papers.css",
        errors,
    )

    papers_reader_js = PAPERS_READER_JS.read_text(encoding="utf-8", errors="replace") if PAPERS_READER_JS.exists() else ""
    require_markers(
        papers_reader_js,
        ('papers-find', 'data-paper-entry', 'matching papers'),
        "science/science-papers.js",
        errors,
    )

    if SITE.exists():
        if not BUILT_PAGE.exists():
            errors.append("built Science page missing: _site/science/index.html")
        else:
            built = BUILT_PAGE.read_text(encoding="utf-8", errors="replace")
            require_markers(built, BUILT_MARKERS, "_site/science/index.html", errors)

        papers_reader = SITE / "science" / "papers" / "index.html"
        if not papers_reader.exists():
            errors.append("built Science Papers reader missing: _site/science/papers/index.html")
        else:
            reader_text = papers_reader.read_text(encoding="utf-8", errors="replace")
            if "?v=missing" in reader_text:
                errors.append("_site/science/papers/index.html: generated Science asset hash resolved to missing")
            require_markers(
                reader_text,
                (
                    "RESEARCH PAPERS",
                    "Core paper series",
                    "Complete reading library",
                    "Core paper series",
                    "<details class=\"papers-shelf\"",
                    "science-papers.css",
                    "science-papers.js",
                    'id="papers-find"',
                    'class="page-nav papers-nav"',
                    "advanced-retarded-door-handshake-recovery",
                    "unified-potato-theory-2025-recovery",
                    "eleven-dimensional-axis-door-dual-spiral-recovery",
                ),
                "_site/science/papers/index.html",
                errors,
            )

        if CATALOG.exists():
            try:
                payload = json.loads(CATALOG.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"science catalog JSON parse failure: {exc}")
                payload = {}

            papers = payload.get("papers", [])
            qualifying_count = payload.get("qualifying_count")
            if not isinstance(qualifying_count, int) or qualifying_count < 10:
                errors.append(f"science catalog qualifying_count unexpectedly small: {qualifying_count!r}")
            if not isinstance(papers, list) or not papers:
                errors.append("science catalog missing public papers list")
            else:
                valid_paper_slugs = {
                    str(paper.get("slug"))
                    for paper in papers
                    if isinstance(paper, dict) and paper.get("slug")
                }
                for paper in papers:
                    if not isinstance(paper, dict):
                        errors.append("science catalog paper metadata must be an object")
                        continue
                    for key in ("slug", "title", "abstract", "fields", "document_type", "file"):
                        if not paper.get(key):
                            errors.append(f"science catalog paper missing {key}: {paper!r}")
                    abstract = str(paper.get("abstract") or "").strip()
                    if abstract.startswith("Canonical science record for "):
                        errors.append(f"science catalog contains generated fallback abstract: {paper.get('file')}")
                    slug = paper.get("slug")
                    if slug:
                        paper_page = SITE / "science" / "papers" / str(slug) / "index.html"
                        if not paper_page.exists():
                            errors.append(f"generated Science document missing: science/papers/{slug}/index.html")
                        else:
                            paper_text = paper_page.read_text(encoding="utf-8", errors="replace")
                            if "?v=missing" in paper_text:
                                errors.append(f"science/papers/{slug}/index.html: generated Science asset hash resolved to missing")
                            if "science-paper.css?v=" not in paper_text:
                                errors.append(f"science/papers/{slug}/index.html: missing content-versioned paper stylesheet")
                            for related_slug in re.findall(r'href="\.\./([^"/]+)/"', paper_text):
                                if related_slug not in valid_paper_slugs:
                                    errors.append(
                                        f"science/papers/{slug}/index.html: related paper target does not exist: {related_slug}"
                                    )

                featured_slug = "advanced-retarded-door-handshake-recovery"
                featured_page = SITE / "science" / "papers" / featured_slug / "index.html"
                if not featured_page.exists():
                    errors.append(f"featured Science paper missing: science/papers/{featured_slug}/index.html")
                else:
                    featured_text = featured_page.read_text(encoding="utf-8", errors="replace")
                    require_markers(
                        featured_text,
                        (
                            "science-time-door-handshake.svg",
                            "science-advanced-retarded-lightcone.svg",
                            "science-time-symmetry-neighbors.svg",
                            "Wheeler-Feynman absorber theory",
                        ),
                        f"science/papers/{featured_slug}/index.html",
                        errors,
                    )

                first = next((p for p in papers if isinstance(p, dict) and p.get("slug")), None)
                if first:
                    paper_page = SITE / "science" / "papers" / str(first["slug"]) / "index.html"
                    if paper_page.exists():
                        text = paper_page.read_text(encoding="utf-8", errors="replace")
                        require_markers(
                            text,
                            ("Abstract", 'class="page-nav paper-nav"', 'class="paper-toc"', 'class="paper-related"', "Download source JSON", "View source on GitHub", "knowledge/science/"),
                            f"science/papers/{first['slug']}/index.html",
                            errors,
                        )
        else:
            errors.append("built science catalog missing: _site/science/catalog.json")

    write_report(errors, semantic, payload)

    if errors:
        print("SCIENCE PORTAL VALIDATION FAILED")
        for error in errors:
            print(" -", error)
            github_error("scripts/validate_science_portal.py", "Science portal validation", error)
        return 1

    print(f"SCIENCE PORTAL VALIDATION PASSED ({semantic.get('advisory_count', 0)} semantic advisories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
