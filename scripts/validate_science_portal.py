#!/usr/bin/env python3
"""Protect the Science hub and generated paper library from structural and semantic collapse."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from audit_science_quality import audit_tree

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = ROOT / "science" / "index.html"
LIBRARY_CSS = ROOT / "science" / "science-library.css"
BUILDER = ROOT / "scripts" / "build_science_catalog.py"
SITE = ROOT / "_site"
BUILT_PAGE = SITE / "science" / "index.html"
CATALOG = SITE / "science" / "catalog.json"

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
COMPACT_CSS_MARKERS = (
    ".science-abstract{display:none}",
    ".science-equation-preview{display:none}",
    ".science-record-tags{display:none}",
    ".science-record-actions.science-source{display:none}",
)


def require_markers(text: str, markers: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{owner}: missing {marker!r}")


def github_error(path: str, title: str, message: str) -> None:
    """Emit a GitHub Actions annotation while remaining harmless outside CI."""
    safe_path = str(path).replace("\r", " ").replace("\n", " ")
    safe_title = str(title).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    safe_message = str(message).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::error file={safe_path},title={safe_title}::{safe_message}")


def main() -> int:
    errors: list[str] = []

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

    for path in (SOURCE_PAGE, LIBRARY_CSS, BUILDER):
        if not path.exists():
            errors.append(f"missing required Science component: {path.relative_to(ROOT)}")

    source = SOURCE_PAGE.read_text(encoding="utf-8", errors="replace") if SOURCE_PAGE.exists() else ""
    css = LIBRARY_CSS.read_text(encoding="utf-8", errors="replace") if LIBRARY_CSS.exists() else ""
    builder = BUILDER.read_text(encoding="utf-8", errors="replace") if BUILDER.exists() else ""
    require_markers(source, SOURCE_MARKERS, "science/index.html", errors)
    require_markers(builder, BUILDER_MARKERS, "scripts/build_science_catalog.py", errors)
    compact_css = "".join(css.split())
    require_markers(compact_css, COMPACT_CSS_MARKERS, "science/science-library.css", errors)

    if SITE.exists():
        if not BUILT_PAGE.exists():
            errors.append("built Science page missing: _site/science/index.html")
        else:
            built = BUILT_PAGE.read_text(encoding="utf-8", errors="replace")
            require_markers(built, BUILT_MARKERS, "_site/science/index.html", errors)

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

                first = next((p for p in papers if isinstance(p, dict) and p.get("slug")), None)
                if first:
                    paper_page = SITE / "science" / "papers" / str(first["slug"]) / "index.html"
                    if paper_page.exists():
                        text = paper_page.read_text(encoding="utf-8", errors="replace")
                        require_markers(
                            text,
                            ("Abstract", "Download source JSON", "View source on GitHub", "knowledge/science/"),
                            f"science/papers/{first['slug']}/index.html",
                            errors,
                        )
        else:
            errors.append("built science catalog missing: _site/science/catalog.json")

    if errors:
        print("SCIENCE PORTAL VALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print(f"SCIENCE PORTAL VALIDATION PASSED ({semantic.get('advisory_count', 0)} semantic advisories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
