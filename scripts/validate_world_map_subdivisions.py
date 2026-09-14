#!/usr/bin/env python3
"""Validate the first generic subdivision integration surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_world_subdivisions.py"
MODULE = ROOT / "world-map" / "3d-subdivisions.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
PAGES = ROOT / ".github" / "workflows" / "pages.yml"


def main() -> int:
    errors = []
    required = (BUILDER, MODULE, BOOTSTRAP, PAGES)
    for path in required:
        if not path.exists():
            errors.append(f"missing subdivision integration file: {path.relative_to(ROOT)}")
    if not errors:
        builder = BUILDER.read_text(encoding="utf-8")
        module = MODULE.read_text(encoding="utf-8")
        bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
        pages = PAGES.read_text(encoding="utf-8")
        for token in ("TIGERweb", "NST-EST2025-ALLDATA.csv", "EXPECTED_US_UNITS = 51", "US-", "federal district"):
            if token not in builder:
                errors.append(f"subdivision builder missing marker: {token}")
        for token in ("world-subdivisions/index.json", "USA.geo.json", "atlas-subdivision", "subdivision=", "potato-atlas-subdivision-select"):
            if token not in module:
                errors.append(f"subdivision module missing marker: {token}")
        if "3d-subdivisions.js" not in bootstrap:
            errors.append("bootstrap does not expose lazy subdivision loading")
        if "build_world_subdivisions.py" not in pages:
            errors.append("Pages deploy does not build the subdivision snapshot")
    if errors:
        print("WORLD MAP SUBDIVISION VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("WORLD MAP SUBDIVISION VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
