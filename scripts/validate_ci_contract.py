#!/usr/bin/env python3
"""Validate that repository quality checks actually gate the revision deployed to Pages."""
from __future__ import annotations
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
QUALITY=ROOT/".github/workflows/quality-checks.yml"
PAGES=ROOT/".github/workflows/pages.yml"

def main()->int:
    errors=[]
    for p in (QUALITY,PAGES):
        if not p.is_file(): errors.append(f"missing workflow: {p.relative_to(ROOT)}")
    if errors:
        for e in errors: print("ERROR",e)
        return 1
    quality=QUALITY.read_text(encoding="utf-8",errors="replace")
    pages=PAGES.read_text(encoding="utf-8",errors="replace")

    for marker in (
        "name: Repository quality checks",
        "needs: [core, world_map, content, build]",
        "CORE_RESULT:",
        "WORLD_MAP_RESULT:",
        "CONTENT_RESULT:",
        "BUILD_RESULT:",
        "cancel-in-progress: true",
        "python scripts/validate_reader_richness.py",
        "python scripts/validate_seo_pipeline.py",
        "python scripts/validate_repo_hygiene.py",
    ):
        if marker not in quality:
            errors.append(f"quality workflow missing contract marker: {marker}")

    if re.search(r"(?m)^\s*push:\s*$", pages):
        errors.append("Pages workflow must not deploy directly from push; deploy only validated workflow_run revisions or explicit manual dispatch")
    for marker in (
        'workflows: ["Repository quality checks"]',
        "types: [completed]",
        "github.event.workflow_run.conclusion == 'success'",
        "github.event.workflow_run.head_branch == 'main'",
        "github.event.workflow_run.head_sha",
        "actions: read",
        "Download exact validated site artifact",
        "actions/download-artifact@v5",
        "name: validated-pages-site",
        "run-id:",
        "Verify validated artifact provenance",
        "_site/build-provenance.json",
        "Upload exact validated Pages artifact",
    ):
        if marker not in pages:
            errors.append(f"Pages workflow missing validated-revision marker: {marker}")
    if "github.event_name == 'push'" in pages:
        errors.append("Pages deploy condition still contains direct-push bypass")
    for forbidden in ("python scripts/build_site.py", "python scripts/optimize_seo.py", "python scripts/build_discovery.py", "curl -fsSL", "actions/checkout@"):
        if forbidden in pages:
            errors.append(f"Pages workflow must deploy the validated artifact without rebuilding or refetching: {forbidden}")
    for marker in ("Upload exact validated Pages artifact", "actions/upload-pages-artifact@v5", "actions/deploy-pages@v5"):
        if marker not in pages:
            errors.append(f"Pages workflow missing deploy-only marker: {marker}")
    for marker in ("Upload exact validated Pages artifact", "name: validated-pages-site", "Stamp validated artifact provenance"):
        if marker not in quality:
            errors.append(f"quality workflow must produce deploy artifact: {marker}")

    if errors:
        print("CI CONTRACT VALIDATION FAILED")
        for e in errors: print("-",e)
        return 1
    print("CI CONTRACT VALIDATION PASSED")
    print("- quality summary depends on core, world_map, content and build")
    print("- stale quality runs cancel during rapid pushes")
    print("- quality build uploads the exact validated-pages-site artifact")
    print("- Pages downloads and verifies that artifact instead of rebuilding")
    print("- manual dispatch remains an explicit operator escape hatch")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
