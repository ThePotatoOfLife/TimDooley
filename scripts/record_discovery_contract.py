from __future__ import annotations

from pathlib import Path

GENERATED_RECORD_OUTPUTS = frozenset(
    {
        "canonical-record-registry.json",
        "repository-index.json",
        "depth-audit-live.json",
        "source-of-truth-audit.json",
    }
)


def iter_discovery_json(data_root: Path):
    """Yield source JSON files eligible for record discovery in stable order."""
    for path in sorted(data_root.rglob("*.json")):
        if path.name in GENERATED_RECORD_OUTPUTS:
            continue
        yield path
