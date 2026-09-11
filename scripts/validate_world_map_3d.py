#!/usr/bin/env python3
"""Validate the 3D World Relational Atlas renderer and its runtime/data contracts."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "world-map" / "3d.html"
APP = ROOT / "world-map" / "3d-app.js"
HOVER = ROOT / "world-map" / "3d-hover.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
EVIDENCE = ROOT / "world-map" / "3d-evidence.js"
UI = ROOT / "world-map" / "3d-ui.js"
SELECTION_UI = ROOT / "world-map" / "3d-selection-ui.js"
TIME = ROOT / "world-map" / "3d-time.js"
FIELDS = ROOT / "world-map" / "3d-fields.js"
NETWORKS = ROOT / "world-map" / "3d-networks.js"
RUNTIME = ROOT / "data" / "world-map-3d-runtime.json"
WORLD = ROOT / "data" / "world-relational-map.json"
COUNTRIES = ROOT / "data" / "countries" / "index.json"


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON: {path.relative_to(ROOT)} — {exc}")
        return {}


def fail_if_missing(text: str, tokens: tuple[str, ...], label: str, errors: list[str]) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing required feature marker: {token}")


def check_js_syntax(text: str, label: str, warnings: list[str], errors: list[str]) -> None:
    node = shutil.which("node")
    if not node:
        warnings.append(f"node not available; skipped JavaScript syntax check for {label}")
        return
    js = text.replace("import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';", "const maplibregl = {};")
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
        handle.write(js)
        temp = Path(handle.name)
    try:
        result = subprocess.run([node, "--check", str(temp)], capture_output=True, text=True)
        if result.returncode:
            errors.append(f"{label} JavaScript syntax check failed: " + (result.stderr.strip() or result.stdout.strip()))
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for path in (HTML, APP, HOVER, BOOTSTRAP, EVIDENCE, UI, SELECTION_UI, TIME, FIELDS, NETWORKS, RUNTIME, WORLD, COUNTRIES):
        if not path.exists():
            errors.append(f"missing required atlas file: {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1

    html = HTML.read_text(encoding="utf-8", errors="replace")
    app = APP.read_text(encoding="utf-8", errors="replace")
    hover = HOVER.read_text(encoding="utf-8", errors="replace")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8", errors="replace")
    evidence = EVIDENCE.read_text(encoding="utf-8", errors="replace")
    ui = UI.read_text(encoding="utf-8", errors="replace")
    selection_ui = SELECTION_UI.read_text(encoding="utf-8", errors="replace")
    time_js = TIME.read_text(encoding="utf-8", errors="replace")
    fields = FIELDS.read_text(encoding="utf-8", errors="replace")
    networks = NETWORKS.read_text(encoding="utf-8", errors="replace")
    runtime = load_json(RUNTIME, errors)
    world = load_json(WORLD, errors)
    countries = load_json(COUNTRIES, errors)

    fail_if_missing(html, ('id="map"','id="panel"','id="status"','id="search"','id="country-list"','id="height"','id="compare"','id="interior"','id="relations"','id="relationType"','id="traceDepth"','id="fit"','id="tilt"','id="globe"','id="world"','id="layersMenu"','id="traceMenu"','id="timeMenu"','id="viewMenu"','id="panelToggle"','id="focusMode"','id="timeMode"','id="timeDate"','id="timeDate2"','id="atlasTimeState"','class="app panel-collapsed"','src="./3d-hover.js"','src="./3d-pathfinder.js"','src="./3d-evidence.js"','src="./3d-time.js"','src="./3d-ui.js"',"Geography, graph topology, project hierarchy and time are separate coordinates"),"world-map/3d.html",errors)
    fail_if_missing(bootstrap,("ATLAS_VERSION = new URL(import.meta.url).searchParams.get('v')","function versionedModule","await import(versionedModule('./3d-hover.js'))","waitForCore","countries-fill","window.__potatoAtlasReady","Path finder","Demography","Progressive UI","declareDormant('Evidence'","declareDormant('Fields'","declareDormant('Networks'","declareDormant('Time'","declareDormant('Axis depth'","declareDormant('Axis operators'","declareDormant('North Axis'","potato-atlas-interactive","__potatoAtlasDiagnostics","deploymentVersion"),"world-map/3d-bootstrap.js",errors)
    fail_if_missing(selection_ui,("atlasSelectionDock","__potatoAtlasLayerRegistry","potato-atlas-selection-change","Module orbit · advanced","Connections","clearCountrySelection"),"world-map/3d-selection-ui.js",errors)
    fail_if_missing(ui,("function setPanel","function setFocus","panel-collapsed","ui-focus","atlas:panel-open","atlas:focus-mode","axisFieldView","empiricalNetworkView","axisDepthNavigator","axisCompactToggle","MutationObserver","potato-atlas-module-ready","__potatoAtlasAttachBasemap","__potatoAtlasUI"),"world-map/3d-ui.js",errors)
    fail_if_missing(time_js,("atlas-time-contract.json","north-axis-membership-history.json","timeMode","changed_between","searchParams.set('timeMode'","atlas-time-change","unknownDatePolicy","No exact dated project-field snapshot is safe to apply automatically","Current project Fields and empirical Networks are not automatically rewritten as historical layers","__potatoAtlasTime"),"world-map/3d-time.js",errors)
    fail_if_missing(fields,("historicalSuppressed","atlas-time-change","setHistoricalSuppressed","Current project-field snapshot hidden in historical mode"),"world-map/3d-fields.js",errors)
    fail_if_missing(networks,("historicalSuppressed","atlas-time-change","setHistoricalSuppressed","Current network snapshot hidden in historical mode"),"world-map/3d-networks.js",errors)
    fail_if_missing(app,("function relationEdgesFor","function edgeKey","function traceGraph","function traceRelationData","function traceHubData","function updateSpatial","function geometryBounds","function fitCodes","function toggleCompareCountry","function deselectCountry","function selectFeature","__potatoAtlasSelection","potato-atlas-selection-change","__potatoAtlasOverlayHandled","function renderCompare","function traceRows","window.openModule","window.goCountry","window.fitTrace","window.fitCompare","window.leaveCompare","TRACE_MAX_DEPTH = 3","TRACE_MAX_NODES","TRACE_MAX_EDGES","new Map([[root, 0]])","queue.shift()","visited.has(other)","searchParams.set('country'","searchParams.set('compare'","searchParams.set('rel'","searchParams.set('depth'","trace-hubs","semantic-hubs","semantic-links","compare-hubs","relations","maplibre-gl@6.9.0","OpenStreetMap contributors","Atlas data failed to load","Breadth-first traversal","A relation line describes a typed connection","Project-canon material is separate from empirical country data","documented physical/public finance"),"world-map/3d-app.js",errors)
    fail_if_missing(hover,("ATLAS_VERSION = new URL(import.meta.url).searchParams.get('v')","function versionedModule","await import(versionedModule('./3d-app.js'))","GEO_LOCAL","GEO_PRIMARY","GEO_FALLBACK","REST_LOCAL","function bestGeometryResponse","function fallbackRestCountries","atlasResilientFetch","local minimal country runtime","CAPITALS_LOCAL","world-capitals.geo.json","installCapitalsWhenUseful","capital-cities","capital-city-major-labels","capital-city-labels","function countryHtml","function capitalHtml","mousemove","mouseleave"),"world-map/3d-hover.js",errors)
    fail_if_missing(evidence,("id = 'evidenceEye'","id = 'evidencePanel'","world-country-facts.json","world-country-demography.json","world-relational-map.json","function projectStatuses","function relationsFor","Source provenance and epistemic context","Project interpretation","Repetition is not corroboration","window.refreshAtlasEvidence","function refreshIfSelectionChanged","new MutationObserver","selectedCode() !== renderedCode","function timeCompatibility","atlas-time-change"),"world-map/3d-evidence.js",errors)

    if "setTimeout(window.refreshAtlasEvidence" in evidence:
        errors.append("Eye refresh regressed to click-dependent timeout synchronization")
    if "query.wikidata.org" in hover:
        errors.append("3D hover regressed to a live Wikidata SPARQL dependency; capital context must use the deploy snapshot")
    if "observe(document.body" in ui:
        errors.append("progressive UI regressed to a body-wide MutationObserver that can self-trigger during summary updates")
    if "setTimeout(settleLateControls" in ui:
        errors.append("progressive UI regressed to startup polling for dormant controls")
    if "await import('./3d-hover.js')" in bootstrap:
        errors.append("bootstrap regressed to an unversioned core module import; deployment cache isolation would be incomplete")
    if "await import('./3d-app.js')" in hover:
        errors.append("hover regressed to an unversioned app-core import; deployment cache isolation would be incomplete")

    for text,label in ((app,"3d-app.js"),(hover,"3d-hover.js"),(bootstrap,"3d-bootstrap.js"),(evidence,"3d-evidence.js"),(ui,"3d-ui.js"),(selection_ui,"3d-selection-ui.js"),(time_js,"3d-time.js"),(fields,"3d-fields.js"),(networks,"3d-networks.js")):
        check_js_syntax(text,label,warnings,errors)

    if runtime.get("status") != "active renderer contract": errors.append("world-map-3d-runtime must be marked as the active renderer contract")
    if runtime.get("projection_contract") != "data/atlas-projection-contract.json": errors.append("3D runtime must point to the shared Atlas projection contract")
    if runtime.get("time_contract") != "data/atlas-time-contract.json": errors.append("3D runtime must point to the Atlas time contract")
    implemented=set(runtime.get("implemented_2026_09_10",[]))
    for fragment in ("Compare","relation","polygon","URL","recursive","trace","Path","population","Eye","Axis","Time","progressive"):
        if not any(fragment.lower() in str(item).lower() for item in implemented): errors.append(f"runtime implemented list does not document {fragment} functionality")
    if runtime.get("compare_mode",{}).get("status") not in {"implemented","implemented-basic"}: errors.append("runtime compare_mode is not marked implemented")
    if runtime.get("trace_mode",{}).get("maximum_depth") != 3: errors.append("runtime trace_mode must document maximum depth 3")
    if runtime.get("path_mode",{}).get("status") != "implemented": errors.append("runtime path_mode is not marked implemented")
    if runtime.get("evidence_mode",{}).get("status") != "implemented-inspector": errors.append("runtime evidence_mode does not document the implemented Eye inspector")
    if runtime.get("time_mode",{}).get("status") != "implemented-conservative-foundation": errors.append("runtime time_mode does not document conservative Time foundation")
    if "suppressed" not in str(runtime.get("time_mode",{}).get("current_overlay_guard","")).lower(): errors.append("runtime time mode does not document current-overlay suppression in historical mode")
    architecture=runtime.get("renderer_architecture",{})
    if "3d-evidence.js" not in str(architecture.get("evidence","")): errors.append("runtime renderer architecture does not assign ownership to Eye")
    if "3d-time.js" not in str(architecture.get("time","")): errors.append("runtime renderer architecture does not assign ownership to Time")
    if "3d-ui.js" not in str(architecture.get("interface_controller","")): errors.append("runtime renderer architecture does not assign ownership to progressive UI")

    country_rows=countries.get("countries",[]);canonical_codes={row.get("iso3") for row in country_rows if row.get("iso3")}
    if len(canonical_codes)!=195: errors.append(f"expected 195 canonical country ISO3 codes; found {len(canonical_codes)}")
    permitted_noncanonical={"GRL","FRO"};referenced:set[str]=set();edge_keys:set[tuple[str,str,tuple[str,...],str]]=set()
    for edge in world.get("curated_edges",[]):
        a,b=edge.get("a"),edge.get("b")
        if not a or not b: errors.append(f"curated edge missing endpoint: {edge}");continue
        if a==b: errors.append(f"curated edge self-loop is probably accidental: {a}")
        referenced.update((a,b));types=edge.get("types") or [];layer=edge.get("layer") or ""
        if not types: errors.append(f"curated edge {a}-{b} has no relationship types")
        if not layer: errors.append(f"curated edge {a}-{b} has no layer/epistemic classification")
        key=tuple(sorted((a,b)))+(tuple(sorted(types)),layer)
        if key in edge_keys: errors.append(f"duplicate curated relation detected: {a}-{b} {types} {layer}")
        edge_keys.add(key)
    for section in ("north","west","east"):
        for value in world.get("project_axis",{}).get(section,{}).values():
            if isinstance(value,list): referenced.update(code for code in value if isinstance(code,str) and len(code)==3)
    unknown=sorted(referenced-canonical_codes-permitted_noncanonical)
    if unknown: errors.append(f"world-map references unknown/unapproved ISO3-like codes: {unknown}")
    relation_types=sorted({t for edge in world.get("curated_edges",[]) for t in edge.get("types",[])})
    if not relation_types: errors.append("world relational map exposes no typed curated relationships")
    if "All relation types" not in html: errors.append("3d map does not expose the all-types relation filter option")
    if "fitBounds" not in app or "geometryBounds" not in app: errors.append("3d map no longer appears to fit actual polygon geometry")
    if "compareCodes.length>=4" not in app and "compareCodes.length >= 4" not in app: errors.append("could not confirm four-country Compare cap during interaction")
    if ".slice(0,4)" not in app: errors.append("could not confirm four-country Compare cap for restored URL state")
    if "Math.min(TRACE_MAX_DEPTH" not in app: errors.append("recursive Trace depth is not clamped to its browser-safe maximum")
    if "visited.has(other)" not in app: errors.append("recursive Trace does not visibly prevent country cycles")
    if "return bestGeometryResponse()" not in hover: errors.append("external geometry request is not routed through resilient local-first loading")
    if "fetchJsonResponse(REST_LOCAL" not in hover: errors.append("REST Countries enrichment does not prefer same-origin deployed snapshot")

    print(f"Canonical countries: {len(canonical_codes)}")
    print(f"Curated relation types: {len(relation_types)}")
    print(f"Referenced country/territory codes: {len(referenced)}")
    print("Trace contract: breadth-first · 1–3 hops · cycle guarded · capped")
    print("UI contract: map-first · grouped controls · contextual inspector · opt-in Axis · focus mode")
    print("Time contract: Current / As-of / Compare-dates · URL persisted · current-only overlays suppressed historically")
    print("Eye-Time contract: observation years are checked against requested historical view")
    print("Boot contract: local snapshot · core-first · advanced overlays dormant until requested · deployment-versioned module chain")
    print("Runtime contract: active renderer · projection/time contracts · Path/Trace/Compare/Eye/Axis documented")
    print(f"Errors: {len(errors)} · Warnings: {len(warnings)}")
    for warning in warnings: print("WARNING:", warning)
    if errors:
        print("WORLD MAP 3D VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1
    print("WORLD MAP 3D VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())