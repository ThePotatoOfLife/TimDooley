#!/usr/bin/env python3
"""Contract test for deterministic Atlas registry generation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        from build_atlas_registry import build_registry
    except ModuleNotFoundError as exc:
        print(f"FAIL: Atlas registry builder is missing: {exc}")
        return 1

    seeds = load(ROOT / "data/atlas-owner-seeds.json")
    committed = load(ROOT / "data/atlas-registry.json")
    generated_a = build_registry()
    generated_b = build_registry()

    if generated_a != generated_b:
        print("FAIL: Atlas registry builder is not deterministic")
        return 1
    if generated_a != committed:
        print("FAIL: committed atlas-registry.json is not reproducible from owner seeds")
        return 1

    seed_ids = {
        row.get("id")
        for row in seeds.get("owners", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    generated_ids = {
        row.get("id")
        for row in generated_a.get("nodes", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    if seed_ids != generated_ids:
        missing = sorted(seed_ids - generated_ids)
        extra = sorted(generated_ids - seed_ids)
        print(f"FAIL: registry membership drift; missing={missing} extra={extra}")
        return 1

    research_id = "house-atlas-systems-theory-index"
    if research_id in generated_ids:
        print("FAIL: unseeded exploratory House research was auto-promoted into Atlas")
        return 1

    print(f"ATLAS REGISTRY BUILDER PASS: {len(generated_ids)} explicit Nodes reproduced deterministically")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
