#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
patcher = (ROOT / "scripts" / "patch_home_discovery.py").read_text(encoding="utf-8")
shell = (ROOT / "scripts" / "validate_site_shell.py").read_text(encoding="utf-8")

required_patcher = ("world-systems/", "machine-index.json", "North Axis — The Potato of Life")
required_shell = ("restore_canonical_world_route", "WORLD_MACHINE_ROUTES", "world-systems/")

missing = [f"patcher:{x}" for x in required_patcher if x not in patcher]
missing += [f"shell:{x}" for x in required_shell if x not in shell]

if missing:
    print("WORLD ARTIFACT PROJECTION VALIDATION FAILED")
    for item in missing:
        print(" -", item)
    raise SystemExit(1)

print("WORLD ARTIFACT PROJECTION VALIDATION PASSED")
