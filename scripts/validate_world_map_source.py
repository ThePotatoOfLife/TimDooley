#!/usr/bin/env python3
"""Run the established renderer, UI-shell, terrain, control-plane, subdivision, search, and browse-performance contracts."""
from __future__ import annotations

from pathlib import Path

import validate_world_map_3d as validator
import validate_world_map_ui_shell as ui_shell
import validate_world_map_terrain as terrain
import validate_world_map_geo_kernel as geo_kernel
import validate_world_map_scale_contract as scale_contract
import validate_world_map_interaction_router as interaction_router
import validate_world_map_spatial_interaction as spatial_interaction
import validate_world_map_places_ownership as places_ownership
import validate_world_map_inspector_router as inspector_router
import validate_world_map_tooltip as tooltip
import validate_world_map_style_lifecycle as style_lifecycle
import validate_world_map_physical_water as physical_water
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
    status = geo_kernel.main()
    if status:
        raise SystemExit(status)
    status = scale_contract.main()
    if status:
        raise SystemExit(status)
    status = interaction_router.main()
    if status:
        raise SystemExit(status)
    status = spatial_interaction.main()
    if status:
        raise SystemExit(status)
    status = places_ownership.main()
    if status:
        raise SystemExit(status)
    status = inspector_router.main()
    if status:
        raise SystemExit(status)
    status = tooltip.main()
    if status:
        raise SystemExit(status)
    status = style_lifecycle.main()
    if status:
        raise SystemExit(status)
    status = physical_water.main()
    if status:
        raise SystemExit(status)
    status = subdivisions.main()
    if status:
        raise SystemExit(status)
    status = search_race.main()
    if status:
        raise SystemExit(status)
    raise SystemExit(browse_performance.main())