#!/usr/bin/env python3
"""Validate the evidence-first World Map dependency impact trace contract."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPACT_UTILS = ROOT / "scripts" / "world_map_impact.py"
RUNTIME_BUILDER = ROOT / "scripts" / "build_world_map_runtime.py"
IMPACT_JS = ROOT / "world-map" / "3d-impact-trace.js"
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
WORLD_BAR = ROOT / "world-map" / "3d-world-bar.js"
COUNTRY_INDEX = ROOT / "data" / "countries" / "index.json"
ENTITIES = ROOT / "data" / "world-map-entities.json"
ANDORRA = ROOT / "data" / "countries" / "andorra.json"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"

FORBIDDEN_SCORE_FIELDS = {"impact_score", "risk_score", "resilience_score", "collapse_score"}


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8", errors="replace")


def load_module(path: Path, name: str):
    if not path.is_file():
        raise AssertionError(f"missing required file: {path.relative_to(ROOT)}")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"could not import {path.relative_to(ROOT)}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generated_runtime() -> dict:
    module = load_module(RUNTIME_BUILDER, "world_map_runtime_for_impact_validation")
    assert hasattr(module, "build_runtime"), "runtime builder must expose build_runtime()"
    return module.build_runtime()


def scan_forbidden_keys(value, path="impact") -> list[str]:
    errors = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_SCORE_FIELDS:
                errors.append(f"forbidden synthetic score field at {path}.{key}")
            errors.extend(scan_forbidden_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            errors.extend(scan_forbidden_keys(child, f"{path}[{idx}]"))
    return errors


def validate_directional_fixture(module) -> None:
    assert hasattr(module, "trace_incoming_impact"), "world_map_impact.py must expose trace_incoming_impact()"
    nodes = {
        "country:A": {"id":"country:A","kind":"country","label":"A"},
        "country:B": {"id":"country:B","kind":"country","label":"B"},
        "country:C": {"id":"country:C","kind":"country","label":"C"},
        "country:D": {"id":"country:D","kind":"country","label":"D"},
    }
    edges = [
        {"source":"country:A","target":"country:B","relationship":"depends-on","causal_status":"explicit-dependency"},
        {"source":"country:C","target":"country:A","relationship":"depends-on","causal_status":"explicit-dependency"},
        {"source":"country:D","target":"country:B","relationship":"connected-to","causal_status":"contextual-association"},
    ]
    result = module.trace_incoming_impact(nodes, edges, "country:B", max_depth=2)
    direct = [row["node"]["id"] for row in result.get("direct", [])]
    second = [row["node"]["id"] for row in result.get("second_order", [])]
    assert direct == ["country:A"], f"directional fixture direct mismatch: {direct}"
    assert second == ["country:C"], f"directional fixture second-order mismatch: {second}"
    assert "country:D" not in set(direct + second), "contextual connection D must not be promoted to causal impact"


def validate_runtime(runtime: dict) -> None:
    assert runtime.get("country_count") == 195, "impact work must preserve exactly 195 sovereign countries"
    impact = runtime.get("impact")
    assert isinstance(impact, dict), "generated runtime must contain impact plane"
    policy = impact.get("policy") or {}
    assert policy.get("max_browser_depth") == 2, "impact max browser depth must be exactly 2"
    assert policy.get("score_policy") == "no aggregate impact score inferred", "impact score policy missing/changed"
    nodes = impact.get("nodes") or {}
    edges = impact.get("edges") or []
    assert "country:AND" in nodes, "impact graph must include Andorra country node"
    assert "territory:GRL" in nodes, "impact graph must include Greenland territory node"
    assert nodes["territory:GRL"].get("kind") == "territory", "Greenland impact node must remain territory"
    assert any(node.get("kind") == "dependency-concept" for node in nodes.values()), "unresolved dependencies must survive as dependency-concept nodes"
    for idx, edge in enumerate(edges):
        for key in ("source", "target", "relationship", "causal_status"):
            assert edge.get(key), f"impact edge {idx} missing {key}"
        assert edge["source"] in nodes, f"impact edge {idx} source missing from nodes: {edge['source']}"
        assert edge["target"] in nodes, f"impact edge {idx} target missing from nodes: {edge['target']}"

    andorra_edges = [edge for edge in edges if edge.get("source") == "country:AND" and edge.get("relationship") == "depends-on"]
    matching = [edge for edge in andorra_edges if (nodes.get(edge.get("target")) or {}).get("label") == "France and Spain road access"]
    assert matching, "Andorra structured road-access dependency must survive impact projection"
    road = matching[0]
    assert road.get("mechanism") == "physical trade, tourism and labour mobility", "Andorra dependency mechanism lost"
    assert road.get("importance") == "critical", "Andorra dependency importance lost"

    forbidden = scan_forbidden_keys(impact)
    assert not forbidden, "; ".join(forbidden)


def validate_sources() -> None:
    index = load_json(COUNTRY_INDEX)
    assert len(index.get("countries") or []) == 195
    entities = load_json(ENTITIES)
    assert (entities.get("entities") or {}).get("GRL", {}).get("canonical_country") is False
    andorra = load_json(ANDORRA)
    deps = andorra.get("strategic_dependencies") or []
    assert any(isinstance(row, dict) and row.get("dependency") == "France and Spain road access" for row in deps), "Andorra fixture source changed"

    builder = read(RUNTIME_BUILDER)
    # Generic relationship topology must not become the causal impact source.
    assert "world-relational-map.json" not in builder.lower(), "impact runtime builder must not bulk-import world-relational-map curated edges"
    # These explicit phrases are forbidden as causal-generation shortcuts.
    assert not re.search(r"for\s+.*members.*depends-on", builder, re.I | re.S), "chain membership must not bulk-generate depends-on edges"
    assert not re.search(r"gateway.*countries.*depends-on", builder, re.I | re.S), "gateway country association must not bulk-generate depends-on edges"


def validate_browser() -> None:
    impact_js = read(IMPACT_JS)
    bootstrap = read(BOOTSTRAP)
    world_bar = read(WORLD_BAR)
    required = (
        "impactNode(id)",
        "impactFor(id)",
        "impactNodeForEntity(code)",
        "impactNodeForGateway(id)",
        "impactNodeForChain(id)",
        "atlas-impact-outline",
        "atlasImpactRoot",
        "atlasImpactDirect",
        "atlasImpactSecond",
        "Directly exposed",
        "Second-order",
        "Known alternatives",
        "Context",
        "searchParams.get('impact')",
        "searchParams.set('impact'",
        "represented dependencies, not a forecast",
    )
    for marker in required:
        assert marker in impact_js, f"3d-impact-trace.js missing marker: {marker}"
    assert "./3d-impact-trace.js" in bootstrap, "bootstrap must load impact trace module"
    assert bootstrap.find("./3d-chain-explorer.js") < bootstrap.find("./3d-impact-trace.js"), "impact trace must load after functional chains"
    assert "data-impact-" not in world_bar and "Impact" not in world_bar, "Impact must not become a permanent top-level World Bar control"


def validate_gateway_alternatives(runtime: dict) -> None:
    gateways = load_json(GATEWAYS).get("gateways") or {}
    for gateway_id in ("suez-sumed", "bab-el-mandeb"):
        alternatives = gateways.get(gateway_id, {}).get("alternatives") or []
        assert any(row.get("target") == "cape-good-hope-route" for row in alternatives if isinstance(row, dict)), f"{gateway_id} must explicitly document Cape rerouting alternative"
    impact = runtime.get("impact") or {}
    alt_edges = [edge for edge in impact.get("edges", []) if edge.get("causal_status") == "explicit-alternative"]
    expected_pairs = {
        ("gateway:suez-sumed", "gateway:cape-good-hope-route"),
        ("gateway:bab-el-mandeb", "gateway:cape-good-hope-route"),
    }
    got = {(edge.get("source"), edge.get("target")) for edge in alt_edges}
    assert expected_pairs.issubset(got), f"missing projected gateway alternatives: {sorted(expected_pairs - got)}"


def main() -> int:
    try:
        module = load_module(IMPACT_UTILS, "world_map_impact_validation")
        validate_directional_fixture(module)
        validate_sources()
        runtime = generated_runtime()
        validate_runtime(runtime)
        validate_gateway_alternatives(runtime)
        validate_browser()
    except (AssertionError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"World Map dependency impact validation failed: {exc}", file=sys.stderr)
        return 1
    print("World Map dependency impact validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
