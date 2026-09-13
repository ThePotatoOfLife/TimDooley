#!/usr/bin/env python3
"""Require canonical build output before validation.

Validators may write diagnostic reports but must not repair the deploy artifact.
The home World entrance is /world/ in source, quality builds and deployment
builds alike.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_site_shell.py"
PATCHER = ROOT / "scripts" / "patch_home_discovery.py"
PAGES = ROOT / ".github" / "workflows" / "pages.yml"


def fail(message: str) -> None:
    raise SystemExit(f"PUBLIC BUILD READONLY FAILED: {message}")


def main() -> int:
    validator = VALIDATOR.read_text(encoding="utf-8")
    patcher = PATCHER.read_text(encoding="utf-8")
    pages = PAGES.read_text(encoding="utf-8")

    if "restore_canonical_world_route" in validator:
        fail("site-shell validator still repairs the World route")
    if "path.write_text(" in validator:
        fail("site-shell validator still writes to a built-site path")
    if "GITHUB_WORKFLOW" in patcher:
        fail("home discovery patcher still has environment-specific route mutation")
    if "href=\"world-map/\"><strong>World</strong>" in patcher:
        fail("home discovery patcher still knows the obsolete homepage rewrite")

    smoke_marker = "expected = ['tim-dooley/','religion/','philosophy/','science/','world/']"
    if smoke_marker not in pages:
        fail("Pages smoke test does not require canonical /world/ homepage entrance")

    print("PUBLIC BUILD READONLY PASSED: build output canonical before validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
