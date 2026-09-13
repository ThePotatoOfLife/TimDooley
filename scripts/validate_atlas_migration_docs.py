#!/usr/bin/env python3
"""Require a durable human/machine migration map for Atlas compatibility layers."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "knowledge/indexes/atlas-deprecation-ledger.json"
DOC = ROOT / "docs/ATLAS-MIGRATION.md"
README = ROOT / "README.md"
RUNTIME = ROOT / "data/atlas-deprecations.json"


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in (INDEX, DOC, RUNTIME) if not path.exists()]
    if missing:
        raise SystemExit(f"ATLAS MIGRATION DOCS FAILED: missing {missing}")

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    if index.get("runtime_ledger") != "data/atlas-deprecations.json":
        raise SystemExit("ATLAS MIGRATION DOCS FAILED: knowledge index must point to runtime ledger")
    if index.get("migration_guide") != "docs/ATLAS-MIGRATION.md":
        raise SystemExit("ATLAS MIGRATION DOCS FAILED: knowledge index must point to migration guide")
    if index.get("entry_owner") != "runtime_ledger":
        raise SystemExit("ATLAS MIGRATION DOCS FAILED: deprecation entries need one declared owner")

    states = set(runtime.get("states", []))
    if not {"live_legacy", "compatibility_only", "retire_when_covered", "retired"}.issubset(states):
        raise SystemExit("ATLAS MIGRATION DOCS FAILED: runtime lifecycle states incomplete")

    doc = DOC.read_text(encoding="utf-8")
    for marker in ("Node", "Relation", "Artifact", "View", "compatibility", "removal preconditions", "Atlas summit"):
        if marker.lower() not in doc.lower():
            raise SystemExit(f"ATLAS MIGRATION DOCS FAILED: guide missing {marker}")

    readme = README.read_text(encoding="utf-8")
    if "docs/ATLAS-MIGRATION.md" not in readme:
        raise SystemExit("ATLAS MIGRATION DOCS FAILED: README does not link migration guide")

    print("ATLAS MIGRATION DOCS PASS: one runtime ledger with durable index and migration guide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
