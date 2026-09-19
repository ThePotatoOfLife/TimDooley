#!/usr/bin/env python3
"""Validate the ADL H.E.A.T. World Map evidence layer and provenance boundary."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data/world-incidents/adl-heat/metadata.json"
SUMMARY = ROOT / "data/world-incidents/adl-heat/state-summary.json"
GEO = ROOT / "data/world-incidents/adl-heat/incidents.geo.json"
MODULE = ROOT / "world-map/3d-adl-heat.js"
HTML = ROOT / "world-map/index.html"
LIFECYCLE = ROOT / "world-map/3d-panel-lifecycle.js"
IMPORTER = ROOT / "scripts/import_adl_heat.py"
MUD_MODULE = ROOT / "world-map/3d-mud-below-us.js"
MUD_DATA = ROOT / "data/world-symbolic/us-mud-below-project-cases.geo.json"

EXPECTED_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA",
    "ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR",
    "PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
}

def load(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}

def require(text: str, token: str, label: str, errors: list[str]) -> None:
    if token not in text:
        errors.append(f"{label} missing marker: {token}")

def main() -> int:
    errors: list[str] = []
    for path in (META,SUMMARY,GEO,MODULE,HTML,LIFECYCLE,IMPORTER,MUD_MODULE,MUD_DATA):
        if not path.exists():
            errors.append(f"missing ADL H.E.A.T. artifact: {path.relative_to(ROOT)}")
    if errors:
        for error in errors: print("ERROR:", error)
        return 1

    meta = load(META, errors)
    summary = load(SUMMARY, errors)
    geo = load(GEO, errors)
    js = MODULE.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8")
    importer = IMPORTER.read_text(encoding="utf-8")
    mud_js = MUD_MODULE.read_text(encoding="utf-8")
    mud_data = load(MUD_DATA, errors)

    if meta.get("id") != "adl-heat":
        errors.append("metadata id must remain adl-heat")
    if meta.get("source_organization") != "Anti-Defamation League (ADL), Center on Extremism":
        errors.append("metadata must preserve explicit ADL source ownership")
    snap = meta.get("snapshot") or {}
    if snap.get("status") not in {"historical-seed","official-export"}:
        errors.append("snapshot status must be historical-seed or official-export")
    if snap.get("status") == "historical-seed" and "not the current" not in str(snap.get("limitation","")).lower():
        errors.append("historical seed must explicitly say it is not the current ADL download")
    semantics = str((meta.get("methodology") or {}).get("display_semantics","")).lower()
    for phrase in ("not a general hate score","not", "population-normalized"):
        if phrase not in semantics:
            errors.append(f"methodology display semantics missing boundary phrase: {phrase}")

    states = summary.get("states") or {}
    codes = {key.removeprefix("US-") for key in states}
    if codes != EXPECTED_STATES:
        errors.append(f"state summary must contain 50 states + DC exactly; got {len(codes)} entries")
    if summary.get("dataset_id") != "adl-heat":
        errors.append("state summary must retain dataset_id adl-heat")

    features = geo.get("features") or []
    if geo.get("type") != "FeatureCollection" or not features:
        errors.append("incident GeoJSON must be a non-empty FeatureCollection")
    ids: set[str] = set()
    state_counts: dict[str,int] = {}
    for i, feature in enumerate(features):
        fid = str(feature.get("id") or "")
        if not fid or fid in ids:
            errors.append(f"incident feature {i} has missing/duplicate id")
        ids.add(fid)
        props = feature.get("properties") or {}
        sid = props.get("subdivision_id")
        if sid not in states:
            errors.append(f"incident feature {fid} has unknown subdivision_id {sid}")
        else:
            state_counts[sid] = state_counts.get(sid,0) + 1
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates") or []
        if geometry.get("type") != "Point" or len(coords) < 2:
            errors.append(f"incident feature {fid} is missing Point geometry")
        for field in ("date","incident_type","source_owner","source_status"):
            if field not in props:
                errors.append(f"incident feature {fid} missing {field}")

    if snap.get("status") == "historical-seed":
        expected = int(snap.get("geocoded_record_count") or 0)
        if expected != len(features):
            errors.append(f"historical seed metadata says {expected} geocoded records but GeoJSON has {len(features)}")

    for token in (
        "atlas-subdivisions-active","adl-heat-state-fill","adl-heat-state-outline","adl-heat-incident-points",
        "feature-state","ADL H.E.A.T. filters","not a general hate score or crime score",
        "__potatoAtlasAdlHeat","evidenceLayer","adlYear","adlType",
        "clickPriority:85","renderStateInspector","renderIncident",
        "incidentTypeTokens","flatMap","retainPartition('USA')","releasePartition?.('USA')",
        "State shading = filtered record count","data-adl-focus",
    ):
        require(js, token, "world-map/3d-adl-heat.js", errors)
    for token in ("id=\"adlHeatLayer\"","ADL H.E.A.T. incidents","U.S. evidence","id=\"mudBelowLayer\"","Mud / Below cases","state centroids"):
        require(html, token, "world-map/index.html", errors)
    for token in ("bindAdlHeatLayerControl","./3d-adl-heat.js","__potatoAtlasAdlHeat?.toggle"):
        require(lifecycle, token, "world-map/3d-panel-lifecycle.js", errors)
    for token in ("bindMudBelowLayerControl","./3d-mud-below-us.js","__potatoAtlasMudBelow?.toggle"):
        require(lifecycle, token, "world-map/3d-panel-lifecycle.js", errors)
    for token in ("hydrateEvidenceLayersFromUrl","evidenceLayer","projectLayer","mud-below-us"):
        require(lifecycle, token, "world-map/3d-panel-lifecycle.js", errors)
    for token in ("project-symbolic-case","state-centroid","retainPartition('USA')","not an objective classification"):
        require(mud_js, token, "world-map/3d-mud-below-us.js", errors)
    if mud_data.get("type") != "FeatureCollection" or len(mud_data.get("features") or []) < 2:
        errors.append("Mud / Below project overlay must retain at least two broad U.S. project case anchors")
    if (mud_data.get("metadata") or {}).get("coordinate_policy") != "state-centroid-only":
        errors.append("Mud / Below project overlay must preserve state-centroid-only coordinate policy")
    for feature in mud_data.get("features") or []:
        props = feature.get("properties") or {}
        if props.get("anchor_precision") != "state-centroid":
            errors.append(f"Mud / Below feature {feature.get('id')} must use state-centroid precision")
        if "not" not in str(props.get("boundary","")).lower():
            errors.append(f"Mud / Below feature {feature.get('id')} is missing attribution/privacy boundary")
    for token in ("official ADL H.E.A.T. CSV export","source_sha256","missing_geometry_count","csv.DictReader"):
        require(importer, token, "scripts/import_adl_heat.py", errors)

    if "fetch('https://www.adl.org" in js or 'fetch("https://www.adl.org' in js:
        errors.append("runtime must not scrape ADL live; it must use committed same-origin snapshots")
    if "hate score" not in js.lower():
        errors.append("runtime must preserve explicit no-hate-score disclosure")

    node = shutil.which("node")
    if node:
        result = subprocess.run([node, "--check", str(MODULE)], cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            errors.append("3d-adl-heat.js syntax check failed: " + (result.stderr.strip() or result.stdout.strip()))
        mud_result = subprocess.run([node, "--check", str(MUD_MODULE)], cwd=ROOT, capture_output=True, text=True)
        if mud_result.returncode:
            errors.append("3d-mud-below-us.js syntax check failed: " + (mud_result.stderr.strip() or mud_result.stdout.strip()))

    print(f"ADL H.E.A.T. snapshot: {snap.get('status')} · {len(features)} geocoded records · {len(states)} state/DC summaries")
    print("Runtime: canonical subdivision feature-state fill + explicit state outlines + lazy locality points + URL filters + source inspector")
    print("Project overlay: Mud / Below case anchors use state-centroid-only coordinates and attributed project terminology")
    print("Provenance: source-owned classifications · snapshot vintage visible · no generic hate score")
    if errors:
        print("ADL H.E.A.T. WORLD MAP VALIDATION FAILED")
        for error in errors: print("-", error)
        return 1
    print("ADL H.E.A.T. WORLD MAP VALIDATION PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
