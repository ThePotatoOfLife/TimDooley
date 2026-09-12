#!/usr/bin/env python3
"""Validate World Map Axis, regional-system, chain, and projection contracts."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "build_world_map_runtime.py"

AXES = {"north", "west", "east", "south"}
ROLES = {"primary", "secondary", "bridge", "frontier", "external", "shared", "unresolved"}
CONFIDENCE = {"high", "medium", "low"}
BASIS = {"explicit-tim", "recovered-conversation", "project-inference", "project-synthesis", "empirical-correspondence"}
EXPECTED_EUROPEAN_NORTH = {
    "LVA": ("primary", "high"),
    "LTU": ("primary", "high"),
    "POL": ("primary", "high"),
    "ROU": ("secondary", "medium"),
    "CZE": ("secondary", "medium"),
    "SVK": ("secondary", "medium"),
    "CHE": ("bridge", "medium"),
    "AUT": ("secondary", "medium"),
    "SVN": ("secondary", "medium"),
    "HUN": ("bridge", "medium"),
    "HRV": ("secondary", "medium"),
    "SRB": ("bridge", "medium"),
    "MNE": ("secondary", "medium"),
    "ALB": ("secondary", "medium"),
    "BGR": ("secondary", "medium"),
    "MKD": ("secondary", "medium"),
    "MDA": ("secondary", "medium"),
    "BIH": ("secondary", "medium"),
}
REQUIRED_GROUP_COUNTS = {
    "asean": (11, 11), "african-union": (55, 54), "sadc": (16, 16),
    "pacific-islands-forum": (18, 14), "sco": (10, 10), "usmca": (3, 3),
    "mercosur": (5, 5), "gcc": (6, 6), "arctic-council": (8, 8),
}
BANNED_BROWSER_PHRASES = {"subordinate", "rules the bloc", "commands the bloc", "owns the bloc"}


def load_json(path: str) -> dict:
    target = ROOT / path
    if not target.exists(): raise AssertionError(f"missing required file: {path}")
    return json.loads(target.read_text(encoding="utf-8"))


def read_text(path: str) -> str:
    target = ROOT / path
    if not target.exists(): raise AssertionError(f"missing required file: {path}")
    return target.read_text(encoding="utf-8")


def canonical_codes() -> set[str]:
    raw = load_json("data/countries/index.json")
    rows = raw if isinstance(raw, list) else raw.get("countries") or raw.get("items") or []
    codes = {str(row.get("iso3") or row.get("cca3") or row.get("code") or "").upper() for row in rows}; codes.discard("")
    assert len(codes) == 195, f"canonical country index must contain 195 ISO3 codes, got {len(codes)}"
    assert all(re.fullmatch(r"[A-Z]{3}", code) for code in codes), "canonical country index contains invalid ISO3"
    return codes


def registered_entity_codes() -> set[str]:
    data = load_json("data/world-map-entities.json")
    entities = data.get("entities") or {}
    codes = set(entities)
    assert all(re.fullmatch(r"[A-Z]{3}", code) for code in codes), "map entity registry contains invalid ISO3-like code"
    assert not (codes & canonical_codes()), "map entity registry must not duplicate sovereign-country identities"
    return codes


def generated_runtime() -> dict:
    assert GENERATOR.is_file(), "missing scripts/build_world_map_runtime.py"
    spec = importlib.util.spec_from_file_location("build_world_map_runtime_axis_validation", GENERATOR)
    assert spec and spec.loader, "could not load World Map runtime generator"
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assert hasattr(module, "build_runtime"), "runtime generator must expose build_runtime()"
    return module.build_runtime()


def validate_axis_source(codes: set[str]) -> dict:
    source = load_json("data/world-axis-profiles.json")
    assert source.get("epistemic_type") == "project_interpretive"
    default = source.get("default_profile") or {}
    assert default.get("status") == "unresolved" and default.get("orientations") == []
    assert set((source.get("axes") or {}).keys()) == AXES
    profiles = source.get("profiles") or {}
    unknown_codes = set(profiles) - codes
    assert not unknown_codes, f"axis profiles contain non-canonical ISO3 codes: {sorted(unknown_codes)}"
    for code, profile in profiles.items():
        orientations = profile.get("orientations") or []
        assert isinstance(orientations, list), f"{code}: orientations must be a list"
        for item in orientations:
            assert item.get("axis") in AXES, f"{code}: invalid axis {item.get('axis')!r}"
            assert item.get("role") in ROLES, f"{code}: invalid role {item.get('role')!r}"
            assert item.get("confidence") in CONFIDENCE, f"{code}: invalid confidence {item.get('confidence')!r}"
            assert item.get("basis") in BASIS, f"{code}: invalid basis"
            assert str(item.get("note") or "").strip(), f"{code}: orientation note required"
    for code, (role, confidence) in EXPECTED_EUROPEAN_NORTH.items():
        north = [item for item in (profiles.get(code, {}).get("orientations") or []) if item.get("axis") == "north"]
        assert north, f"{code}: missing required North orientation"
        assert north[0].get("role") == role, f"{code}: expected North role {role}"
        assert north[0].get("confidence") == confidence, f"{code}: expected North confidence {confidence}"
        assert north[0].get("basis") == "project-synthesis", f"{code}: expected project-synthesis basis"
        assert str(north[0].get("note") or "").strip(), f"{code}: North note required"
    aus = profiles.get("AUS", {}).get("orientations") or []
    assert any(item.get("axis") == "south" and item.get("role") == "primary" for item in aus), "Australia must remain South-primary"
    assert not any(item.get("axis") == "north" for item in aus), "Australia must no longer be selected in North"
    figures = source.get("reference_figures") or []
    assert figures, "reference_figures must not be empty"
    for figure in figures:
        assert figure.get("axis") in AXES and str(figure.get("person") or "").strip() and str(figure.get("real_office") or "").strip()
        assert str(figure.get("country_or_institution") or "").strip() and str(figure.get("axis_role") or "").strip()
        assert figure.get("epistemic_type") == "project_interpretive"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(figure.get("as_of") or "")), f"bad as_of for {figure.get('person')}"
        assert str(figure.get("source_url") or "").startswith("https://"), f"source_url required for {figure.get('person')}"
    assert source.get("center_junction"), "center_junction metadata required"
    return source


def validate_groups() -> dict:
    data = load_json("data/world-institution-memberships.json"); groups = data.get("groups") or {}
    for group_id, (official_count, polygon_count) in REQUIRED_GROUP_COUNTS.items():
        assert group_id in groups, f"missing institutional group {group_id}"
        group = groups[group_id]
        assert group.get("official_member_count") == official_count, f"{group_id}: official count drift"
        members = group.get("members") or []
        assert len(members) == polygon_count, f"{group_id}: expected {polygon_count} renderable country members, got {len(members)}"
        assert len(set(members)) == len(members), f"{group_id}: duplicate member"
        assert all(re.fullmatch(r"[A-Z]{3}", code) for code in members), f"{group_id}: invalid ISO3 member"
        for key in ("as_of", "source", "source_url"): assert str(group.get(key) or "").strip(), f"{group_id}: {key} required"
        assert str(group.get("source_url") or "").startswith("https://"), f"{group_id}: source_url must be https"
    return data


def validate_chains(codes: set[str], entity_codes: set[str]) -> dict:
    data = load_json("data/world-system-chains.json"); chains = data.get("chains") or {}
    required = {"arctic","north-atlantic","baltic","northern-energy","european-industrial","eastern-security","european-strategic-autonomy","eurasian-interface","blue-pacific","southern-african"}
    assert required.issubset(chains), f"missing chains: {sorted(required - set(chains))}"
    allowed = codes | entity_codes
    for chain_id, chain in chains.items():
        assert str(chain.get("label") or "").strip(), f"{chain_id}: label required"
        assert chain.get("epistemic_type") in {"observed", "derived", "mixed"}, f"{chain_id}: bad epistemic_type"
        assert isinstance(chain.get("systems"), list) and chain["systems"], f"{chain_id}: systems required"
        assert str(chain.get("description") or "").strip() and str(chain.get("source_note") or "").strip()
        unknown = set(chain.get("members") or []) - allowed
        assert not unknown, f"{chain_id}: unknown country/entity members {sorted(unknown)}"
    return data


def validate_runtime(codes: set[str], entity_codes: set[str]) -> None:
    runtime = generated_runtime()
    assert runtime.get("country_count") == 195
    assert set((runtime.get("countries") or {})) == codes, "sovereign runtime coverage must remain exactly 195 countries"
    entities = runtime.get("entities") or {}
    assert set((entities.get("territories") or {})) == entity_codes, "runtime territory registry drift"
    axis = runtime.get("axis") or {}
    assert set((axis.get("memberships") or {}).keys()) == AXES
    runtime_profiles = axis.get("countries") or {}
    expected_profiles = codes | entity_codes
    assert set(runtime_profiles) == expected_profiles, f"runtime axis coverage must resolve countries + registered entities, got {len(runtime_profiles)}"
    allowed = expected_profiles
    for axis_id, members in (axis.get("memberships") or {}).items():
        assert axis_id in AXES
        assert not (set(members) - allowed), f"{axis_id}: unknown runtime members {sorted(set(members)-allowed)}"
    north_members = set((axis.get("memberships") or {}).get("north") or [])
    for code in {"EST", "UKR", "TUR", "XKX", *EXPECTED_EUROPEAN_NORTH.keys()}:
        assert code in north_members, f"runtime North membership missing {code}; N overlay would omit it"
    assert "AUS" not in north_members, "runtime North membership must not include Australia"
    kosovo = (entities.get("territories") or {}).get("XKX") or {}
    assert kosovo.get("canonical_country") is False, "Kosovo must remain outside the canonical 195-country sovereign index"
    assert kosovo.get("render_status") == "current", "Kosovo must be renderable from the existing geometry"
    assert kosovo.get("geometry_alias") == "CS-KM", "Kosovo must bind the source geometry id CS-KM to runtime entity XKX"
    south_members = set((axis.get("memberships") or {}).get("south") or [])
    assert "ATA" in south_members, "runtime South membership missing Antarctica (ATA); South-pole overlay would omit it"
    antarctica = (entities.get("territories") or {}).get("ATA") or {}
    assert antarctica.get("canonical_country") is False, "Antarctica must remain a non-sovereign map entity"
    assert antarctica.get("render_status") == "current", "Antarctica must be renderable from the existing geometry"
    assert runtime.get("reference_figures") and runtime.get("chains")
    groups = runtime.get("groups") or {}
    for group_id in REQUIRED_GROUP_COUNTS: assert group_id in groups, f"runtime missing group {group_id}"


def validate_registry_and_browser() -> None:
    registry = load_json("data/world-map-layer-registry.json"); entries = {entry.get("id"): entry for entry in registry.get("entries") or []}
    for axis_id in AXES:
        entry = entries.get(f"axis.{axis_id}") or {}
        assert entry.get("source_owner") == "data/world-map-data-runtime.json" and entry.get("runtime_axis") == axis_id
    for group_id in REQUIRED_GROUP_COUNTS:
        entry = entries.get(f"group.{group_id}") or {}
        assert entry.get("availability") == "current" and entry.get("source_owner") == "data/world-institution-memberships.json"
    compositor = read_text("world-map/3d-compositor.js")
    for token in ("axisMembers", "axisProfile", "referenceFigures", "chainsForCountry"): assert token in compositor, f"compositor missing runtime API {token}"
    assert "world-axis-profiles.json" not in compositor and "collectIsoArrays(data?.project_axis?.north" not in compositor
    app = read_text("world-map/3d-app.js")
    assert "CS-KM" in app and "XKX" in app, "World Map geometry normalization must alias Kosovo CS-KM to XKX"
    world_bar = read_text("world-map/3d-world-bar.js")
    for token in ("projection", "setProjection", "mercator", "globe", "__potatoAtlasProjection"): assert token in world_bar
    card = read_text("world-map/3d-country-card.js"); assert "axisProfile" in card and "chainsForCountry" in card
    browser_copy = (world_bar + "\n" + card + "\n" + compositor).lower()
    for phrase in BANNED_BROWSER_PHRASES: assert phrase not in browser_copy, f"banned project hierarchy wording in browser code: {phrase}"


def main() -> int:
    try:
        codes = canonical_codes(); entity_codes = registered_entity_codes()
        validate_axis_source(codes); validate_groups(); validate_chains(codes, entity_codes); validate_runtime(codes, entity_codes); validate_registry_and_browser()
    except (AssertionError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"World Map Axis/systems validation failed: {exc}", file=sys.stderr); return 1
    print("World Map Axis/systems validation passed."); return 0


if __name__ == "__main__": raise SystemExit(main())
