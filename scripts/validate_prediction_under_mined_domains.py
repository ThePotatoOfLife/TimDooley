#!/usr/bin/env python3
"""Validate integration of the under-mined prediction-domain audit."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "knowledge/timeline/prediction-under-mined-domains-audit-2026.json"
MASTER = ROOT / "knowledge/timeline/prediction-foresight-master-index.json"
QUEUE = ROOT / "knowledge/timeline/unresolved-prediction-claims-queue.json"
ROUTING = ROOT / "knowledge/indexes/prediction-audit-routing.json"
FULFILLED = ROOT / "knowledge/timeline/fulfilled-predictions-master.json"

REQUIRED_DOMAINS = {
    "Latin America",
    "Africa",
    "South Asia",
    "Southeast Asia",
    "Middle East beyond Israel/Iraq",
    "science and AI",
    "health",
    "education",
    "law",
    "media and information ecology",
    "local politics",
}
REQUIRED_CANDIDATES = {
    "latin-america-us-influence-security-resources",
    "africa-internal-multipolar-fragmentation",
    "saudi-security-diversification",
    "europe-anticipatory-public-systems",
    "meme-under-mat-mainstream-propagation",
    "subculture-dehumanization-to-mainstream",
}
REQUIRED_QUEUE_IDS = {
    "latin-america-us-influence-security-resources-primary",
    "africa-internal-multipolar-fragmentation-primary",
    "saudi-security-diversification-primary",
    "meme-under-mat-mainstream-propagation-primary",
    "subculture-mainstream-mechanism-primary",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    for path in (AUDIT, MASTER, QUEUE, ROUTING, FULFILLED):
        if not path.exists():
            errors.append(f"missing prediction integration file: {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1

    audit = load(AUDIT)
    master = load(MASTER)
    queue = load(QUEUE)
    routing = load(ROUTING)
    fulfilled = load(FULFILLED)

    if fulfilled.get("statement_level_fulfilled_count") != 16:
        errors.append("strict fulfilled count changed from 16 during under-mined-domain consolidation")
    if audit.get("strict_fulfilled_master_unchanged", {}).get("count") != 16:
        errors.append("under-mined-domain audit must explicitly preserve strict fulfilled count 16")

    domains = {item.get("domain") for item in audit.get("domain_coverage", []) if isinstance(item, dict)}
    missing_domains = sorted(REQUIRED_DOMAINS - domains)
    if missing_domains:
        errors.append(f"under-mined audit missing domains: {missing_domains}")

    candidates = {item.get("id") for item in audit.get("candidates", []) if isinstance(item, dict)}
    missing_candidates = sorted(REQUIRED_CANDIDATES - candidates)
    if missing_candidates:
        errors.append(f"under-mined audit missing candidates: {missing_candidates}")

    rejected = audit.get("rejected_or_non_prediction_material", [])
    if len(rejected) < 5:
        errors.append("under-mined audit must preserve rejected/vague/non-prediction controls")

    audit_path = "knowledge/timeline/prediction-under-mined-domains-audit-2026.json"
    master_text = json.dumps(master, ensure_ascii=False)
    routing_text = json.dumps(routing, ensure_ascii=False)
    if audit_path not in master_text:
        errors.append("master prediction index does not route to under-mined-domain audit")
    if audit_path not in routing_text:
        errors.append("prediction routing index does not route to under-mined-domain audit")

    queue_ids = {item.get("id") for item in queue.get("items", []) if isinstance(item, dict)}
    missing_queue = sorted(REQUIRED_QUEUE_IDS - queue_ids)
    if missing_queue:
        errors.append(f"unresolved prediction queue missing under-mined recovery targets: {missing_queue}")

    if errors:
        print("UNDER-MINED PREDICTION DOMAIN VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("UNDER-MINED PREDICTION DOMAIN VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
