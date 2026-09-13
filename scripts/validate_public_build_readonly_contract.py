#!/usr/bin/env python3
"""Require canonical, composed public build output before validation.

Validators may write diagnostic reports but must not repair the deploy artifact.
Pages and repository quality checks must build the same composed public artifact:
legacy reader surfaces plus the additive Atlas projection.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_site_shell.py"
PATCHER = ROOT / "scripts" / "patch_home_discovery.py"
PAGES = ROOT / ".github" / "workflows" / "pages.yml"
QUALITY = ROOT / ".github" / "workflows" / "quality-checks.yml"


def fail(message: str) -> None:
    raise SystemExit(f"PUBLIC BUILD READONLY FAILED: {message}")


def require_composed_builder(text: str, owner: str) -> None:
    if "run: python scripts/build_public_site.py" not in text:
        fail(f"{owner} must use build_public_site.py for the public artifact")
    if "run: python scripts/build_site.py" in text:
        fail(f"{owner} still uses legacy-only build_site.py as a workflow build step")


def main() -> int:
    validator = VALIDATOR.read_text(encoding="utf-8")
    patcher = PATCHER.read_text(encoding="utf-8")
    pages = PAGES.read_text(encoding="utf-8")
    quality = QUALITY.read_text(encoding="utf-8")

    if "restore_canonical_world_route" in validator:
        fail("site-shell validator still repairs the World route")
    if "path.write_text(" in validator:
        fail("site-shell validator still writes to a built-site path")
    if "GITHUB_WORKFLOW" in patcher:
        fail("home discovery patcher still has environment-specific route mutation")
    if "href=\"world-map/\"><strong>World</strong>" in patcher:
        fail("home discovery patcher still knows the obsolete homepage rewrite")

    require_composed_builder(pages, "Pages")
    require_composed_builder(quality, "Quality CI")

    smoke_marker = "expected = ['tim-dooley/','religion/','philosophy/','science/','world/']"
    if smoke_marker not in pages:
        fail("Pages smoke test does not require canonical /world/ homepage entrance")

    for marker in (
        "run: python scripts/validate_public_atlas_coexistence.py",
        "run: python scripts/validate_atlas_pages.py",
        "run: python scripts/validate_atlas_public_index.py",
    ):
        if marker not in quality:
            fail(f"Quality CI does not validate composed Atlas output: {marker}")

    print("PUBLIC BUILD READONLY PASSED: Pages and Quality build and validate one composed public artifact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
