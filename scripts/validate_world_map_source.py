#!/usr/bin/env python3
"""Run the established renderer, UI-shell, terrain, control-plane, subdivision, search, and browse-performance contracts."""
from __future__ import annotations

from pathlib import Path

import validate_world_map_3d as validator
import validate_world_map_ui_shell as ui_shell
import validate_world_map_terrain as terrain
import validate_world_map_layer_disclosure as layer_disclosure
import validate_world_map_geo_kernel as geo_kernel
import validate_world_map_scale_contract as scale_contract
import validate_world_map_interaction_router as interaction_router
import validate_world_map_spatial_interaction as spatial_interaction
import validate_world_map_places_ownership as places_ownership
import validate_world_map_inspector_router as inspector_router
import validate_world_map_tooltip as tooltip
import validate_world_map_style_lifecycle as style_lifecycle
import validate_world_map_runtime_telemetry as runtime_telemetry
import validate_world_map_behavioral_scenarios as behavioral_scenarios
import validate_world_map_physical_water as physical_water
import validate_world_map_hydrology as hydrology
import validate_world_map_subdivisions as subdivisions
import validate_world_map_search_race as search_race
import validate_world_map_browse_performance as browse_performance
import validate_world_map_map_state as map_state
import validate_world_map_reduced_motion as reduced_motion
import validate_world_map_url_state as url_state

validator.HTML = Path(__file__).resolve().parents[1] / "world-map" / "index.html"

# The current country-selection controller replaced the three fixed AUTO_EDGES_*
# constants with a bounded, runtime-adjustable relation budget. Preserve every
# other legacy renderer marker while treating the new budget API as the stronger
# compatibility contract for this one feature.
_legacy_fail_if_missing = validator.fail_if_missing
_LEGACY_RELATION_BUDGET_MARKERS = {
    "AUTO_EDGES_ACTIVE",
    "AUTO_EDGES_OTHER",
    "AUTO_EDGES_TOTAL",
}
_DYNAMIC_RELATION_BUDGET_MARKERS = (
    "DEFAULT_AUTO_RELATION_BUDGET",
    "automaticRelationBudget",
    "setAutomaticRelationBudget",
    "getAutomaticRelationBudget",
)


def _fail_if_missing_with_dynamic_relation_budget(
    text: str,
    tokens: tuple[str, ...],
    label: str,
    errors: list[str],
) -> None:
    if label != "world-map/3d-country-selection.js":
        _legacy_fail_if_missing(text, tokens, label, errors)
        return

    preserved_tokens = tuple(
        token for token in tokens if token not in _LEGACY_RELATION_BUDGET_MARKERS
    )
    _legacy_fail_if_missing(text, preserved_tokens, label, errors)
    _legacy_fail_if_missing(text, _DYNAMIC_RELATION_BUDGET_MARKERS, label, errors)


validator.fail_if_missing = _fail_if_missing_with_dynamic_relation_budget

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
    status = layer_disclosure.main()
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
    status = runtime_telemetry.main()
    if status:
        raise SystemExit(status)
    status = behavioral_scenarios.main()
    if status:
        raise SystemExit(status)
    status = physical_water.main()
    if status:
        raise SystemExit(status)
    status = hydrology.main()
    if status:
        raise SystemExit(status)
    status = subdivisions.main()
    if status:
        raise SystemExit(status)
    status = search_race.main()
    if status:
        raise SystemExit(status)
    status = map_state.main()
    if status:
        raise SystemExit(status)
    status = reduced_motion.main()
    if status:
        raise SystemExit(status)
    status = url_state.main()
    if status:
        raise SystemExit(status)
    raise SystemExit(browse_performance.main())
