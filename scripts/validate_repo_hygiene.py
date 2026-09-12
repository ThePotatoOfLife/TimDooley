#!/usr/bin/env python3
"""Guard the repository against CI and migration debris accumulating again."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
EXPECTED_WORKFLOWS = {
    "country-refresh.yml",
    "import-edda-texts.yml",
    "pages.yml",
    "quality-checks.yml",
}
FORBIDDEN_TEMPORARY = {
    ".github/workflows/timeline-naming-migration.yml",
    "scripts/migrate_timeline_to_timeline.py",
}


def main() -> int:
    errors: list[str] = []

    actual = {p.name for p in WORKFLOWS.glob("*.yml")} | {p.name for p in WORKFLOWS.glob("*.yaml")}
    missing = sorted(EXPECTED_WORKFLOWS - actual)
    extra = sorted(actual - EXPECTED_WORKFLOWS)
    if missing:
        errors.append("missing expected workflows: " + ", ".join(missing))
    if extra:
        errors.append("unexpected workflow sprawl: " + ", ".join(extra))

    for rel in sorted(FORBIDDEN_TEMPORARY):
        if (ROOT / rel).exists():
            errors.append(f"temporary migration debris remains: {rel}")

    legacy = ROOT / "timeline" / "index.html"
    if not legacy.exists():
        errors.append("legacy timeline compatibility redirect is missing")
    else:
        text = legacy.read_text(encoding="utf-8", errors="replace")
        if "noindex" not in text or "../timeline/" not in text:
            errors.append("timeline compatibility route is no longer redirect-only")

    if errors:
        print("REPOSITORY HYGIENE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository hygiene: PASS")
    print("Active workflows: " + ", ".join(sorted(actual)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
