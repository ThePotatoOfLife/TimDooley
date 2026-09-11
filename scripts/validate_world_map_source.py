#!/usr/bin/env python3
"""Run the established 3D renderer contract against the canonical World Map page."""
from __future__ import annotations

from pathlib import Path

import validate_world_map_3d as validator

validator.HTML = Path(__file__).resolve().parents[1] / "world-map" / "index.html"

if __name__ == "__main__":
    raise SystemExit(validator.main())
