#!/usr/bin/env python3
"""Run the established renderer, UI-shell, terrain, subdivision, search, and browse-performance contracts."""
from __future__ import annotations

from pathlib import Path

import validate_world_map_3d as validator
import validate_world_map_ui_shell as ui_shell
import validate_world_map_terrain as terrain
import validate_world_map_subdivisions as subdivisions
import validate_world_map_search_race as search_race
import validate_world_map_browse_performance as browse_performance

validator.HTML = Path(__file__).resolve().parents[1] / "world-map" / "index.html"

if __name__ == "__main__":
    status = validator.main()
    if status:
        raise SystemExit(status)
    status = ui_shell.main()
    if status:
        raise SystemExit(status)
    status = terrain.main()
    if status:
        raise SystemExit(status)
    status = subdivisions.main()
    if status:
        raise SystemExit(status)
    status = search_race.main()
    if status:
        raise SystemExit(status)
    raise SystemExit(browse_performance.main())
