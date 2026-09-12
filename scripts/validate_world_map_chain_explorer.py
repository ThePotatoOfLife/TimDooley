#!/usr/bin/env python3
"""Validate contextual functional-chain exploration in the canonical World Map."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "world-map" / "3d-country-card.js"
EXPLORER = ROOT / "world-map" / "3d-chain-explorer.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    try:
        card = read(CARD)
        explorer = read(EXPLORER)
        bootstrap = read(BOOTSTRAP)
        world_bar = read(WORLD_BAR)
        assert "data-chain-id" in card, "country-card chain tags must expose stable chain IDs"
        for token in ("atlasChainMatch", "atlas-chain-outline", "runtime.chain", "searchParams.get('chain')", "searchParams.set('chain'", "__potatoAtlasChainExplorer", "feature-state"):
            assert token in explorer, f"chain explorer missing marker: {token}"
        assert "./3d-chain-explorer.js" in bootstrap, "bootstrap must load chain explorer"
        assert "Chain" not in world_bar or "atlas-world-menu" not in explorer, "chain explorer must not add a top-level menu"
    except AssertionError as exc:
        print(f"World Map chain explorer validation failed: {exc}", file=sys.stderr)
        return 1
    print("World Map chain explorer validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
