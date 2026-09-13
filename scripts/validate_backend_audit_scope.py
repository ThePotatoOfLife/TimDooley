#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts/audit_backend_coverage.py"


def fail(message: str) -> None:
    raise SystemExit(f"BACKEND AUDIT SCOPE FAILED: {message}")


def main() -> int:
    text = AUDIT.read_text(encoding="utf-8")
    for marker in (
        'KNOWLEDGE=ROOT/"knowledge"',
        'ATLAS_REGISTRY=DATA/"atlas-registry.json"',
        'ATLAS_ARTIFACTS=DATA/"atlas-artifacts.json"',
        '"unmapped_knowledge_files"',
        '"atlas_canonical_owner_files"',
        '"atlas_artifact_source_files"',
        '"knowledge_duplicate_ids"',
        '"knowledge_index_mirror_ids"',
        '"knowledge_peer_duplicate_ids"',
        '"candidate_unresolved_machine_ids"',
        '"external_reference_ids"',
        '"human_label_endpoints"',
        '"date_like_endpoints"',
    ):
        if marker not in text:
            fail(f"audit missing full-repository scope/signal marker {marker}")
    if 'return sorted(DATA.rglob("*.json"))' in text:
        fail("audit still scans only data/**/*.json")
    print("BACKEND AUDIT SCOPE PASSED: data + knowledge + Atlas ownership/depth + duplicate classes + endpoint signal classes are audited together")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
