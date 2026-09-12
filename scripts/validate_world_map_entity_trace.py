#!/usr/bin/env python3
"""Validate the entity-aware Trace investigation surface.

Entity Trace is a contextual capability of the canonical registry-driven World
Map. The ordinary map stays compact: selecting a country reveals the country
card, and that card is the entry point into deeper country details and the
normalized entity graph. Legacy Progressive UI / Trace-menu ownership must not
be required by this contract.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "atlas-entity-trace-contract.json"
JS = ROOT / "world-map" / "3d-entity-trace.js"
CARD = ROOT / "world-map" / "3d-country-card.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
REL = ROOT / "data" / "relationships.json"
NODES = ROOT / "data" / "nodes.json"
COUNTRIES = ROOT / "data" / "countries" / "index.json"
BRIDGE = ROOT / "data" / "global-graph-bridge.json"


def load(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for path in (CONTRACT, JS, CARD, BOOTSTRAP, REL, NODES, COUNTRIES, BRIDGE):
        if not path.exists():
            errors.append(f"missing entity-trace dependency: {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1

    contract = load(CONTRACT, errors)
    bridge = load(BRIDGE, errors)
    relationships = load(REL, errors)
    js = JS.read_text(encoding="utf-8", errors="replace")
    card = CARD.read_text(encoding="utf-8", errors="replace")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8", errors="replace")

    if contract.get("status") != "implemented-one-hop-inspector":
        errors.append("entity Trace contract must remain implemented-one-hop-inspector")
    if contract.get("runtime") != "world-map/3d-entity-trace.js":
        errors.append("entity Trace contract does not own the runtime module")
    if contract.get("scope", {}).get("depth") != 1:
        errors.append("first entity Trace implementation must remain depth 1 until growth gates are met")
    if contract.get("scope", {}).get("surface") != "Country card / contextual investigation":
        errors.append("entity Trace must be entered contextually from the canonical country card")
    if bridge.get("public_reader") != "index.html":
        errors.append("global graph bridge public reader changed; entity Trace routing must be reviewed")

    evidence_contract = contract.get("evidence", {})
    if set(evidence_contract.get("filters", [])) != {"evidence class", "confidence"}:
        errors.append("entity Trace contract must expose evidence-class and confidence filters")
    completed = set(contract.get("growth_gate", {}).get("completed", []))
    for gate in (
        "add evidence-class filtering",
        "add confidence filtering",
        "route archive endpoints through bridge/public-reader rules",
    ):
        if gate not in completed:
            errors.append(f"entity Trace completed gate not recorded: {gate}")

    required_js = (
        "data/relationships.json",
        "data/nodes.json",
        "data/countries/index.json",
        "data/global-graph-bridge.json",
        "function archiveRoute",
        "explicitBridges",
        "valid_from",
        "valid_to",
        "validity unknown",
        "record date is not treated as its start date",
        "Entity Trace expands topology, not geography",
        "window.__potatoEntityTrace",
        "atlas-time-change",
        "potato-atlas-working-selection-change",
        "potato-atlas-entity-trace-change",
        "queueMicrotask(render)",
        "entityEvidenceFilter",
        "entityConfidenceFilter",
        "function passesFilters",
        "function setEnabled",
        "function toggle",
        "All evidence classes",
        "All confidence levels",
        "they are not a truth score",
    )
    for marker in required_js:
        if marker not in js:
            errors.append(f"3d-entity-trace.js missing contract marker: {marker}")
    if "setTimeout(render" in js:
        errors.append("entity Trace regressed to timer-dependent panel refresh")
    if "lat:" in js or "lon:" in js or "geometry:" in js:
        warnings.append("entity Trace contains coordinate/geometry language; review before allowing non-country spatial rendering")
    if "#traceMenu .menu-pop" in js:
        errors.append("entity Trace still depends on the retired Progressive UI Trace menu")

    # The ordinary country card is the contextual door into deep investigation.
    # It may expose two quiet actions, but it must not grow another permanent
    # top-level toolbar.
    required_card = (
        'data-country-action="details"',
        'data-country-action="entity-trace"',
        "window.__potatoAtlasLoadModule",
        "./3d-entity-trace.js",
        "window.__potatoEntityTrace",
        "panel-collapsed",
        "More country data",
        "Trace connections",
    )
    for marker in required_card:
        if marker not in card:
            errors.append(f"3d-country-card.js missing contextual investigation marker: {marker}")

    if "window.__potatoAtlasLoadModule = loadAfterPaint" not in bootstrap:
        errors.append("bootstrap no longer exposes the shared versioned optional-module loader")
    if "declareDormant('Entity Trace', './3d-entity-trace.js', 'Trace menu')" in bootstrap:
        errors.append("bootstrap still describes the retired Trace menu as Entity Trace owner")
    if "declareDormant('Entity Trace', './3d-entity-trace.js', 'country-card contextual action')" not in bootstrap:
        errors.append("bootstrap must describe the country-card contextual action as Entity Trace trigger")

    rels = relationships.get("relationships", [])
    if not rels:
        errors.append("normalized relationship graph is empty")
    evidence_classes = {str(row.get("evidence")) for row in rels if row.get("evidence")}
    confidence_classes = {str(row.get("confidence")) for row in rels if row.get("confidence")}
    if len(evidence_classes) < 2:
        warnings.append("normalized graph currently exposes fewer than two evidence classes")
    if not confidence_classes:
        warnings.append("normalized graph currently exposes no explicit confidence classes")

    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
            handle.write(js)
            temp = Path(handle.name)
        try:
            result = subprocess.run([node, "--check", str(temp)], capture_output=True, text=True)
            if result.returncode:
                errors.append("entity Trace JavaScript syntax failed: " + (result.stderr.strip() or result.stdout.strip()))
        finally:
            temp.unlink(missing_ok=True)
    else:
        warnings.append("node unavailable; skipped entity Trace JavaScript syntax check")

    print(f"Normalized relationships: {len(rels)}")
    print(f"Evidence classes represented: {len(evidence_classes)}")
    print(f"Confidence classes represented: {len(confidence_classes)}")
    print("Entity Trace: country-card entry · shared versioned loader · one-hop inspector · bridge-routed archive links · Time-aware validity labels · evidence/confidence filters · no fake coordinates")
    print(f"Errors: {len(errors)} · Warnings: {len(warnings)}")
    for warning in warnings:
        print("WARNING:", warning)
    if errors:
        print("ENTITY TRACE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("ENTITY TRACE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
