#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
RISK_WEIGHTS = {"error": 10, "warning": 3, "note": 0}
RISK_DOMAINS = (
    "render_ownership",
    "feature_state",
    "style_lifecycle",
    "event_lifecycle",
    "popup_interaction",
    "data_mutation",
    "url_state",
    "dom_ownership",
)
DEFAULT_RENDER_STACK_SLOTS = (
    "physical-surface",
    "physical-water",
    "physical-line",
    "geography-context",
    "context-network",
    "selection-emphasis",
)


def line_for(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def record(kind: str, resource: str, module: str, operation: str, line: int, confidence: str = "high", **details: Any) -> dict[str, Any]:
    return {
        "kind": kind,
        "resource": resource,
        "module": module,
        "operation": operation,
        "line": line,
        "confidence": confidence,
        "details": details,
    }


def discover_modules(root: Path) -> list[Path]:
    world = root / "world-map"
    if not world.is_dir():
        return []
    return sorted(path for path in world.glob("3d-*.js") if path.is_file())


def literal_pairs(source: str, pattern: re.Pattern[str]):
    for match in pattern.finditer(source):
        yield match, match.groups()


def scan_module(path: Path, repo_root: Path) -> list[dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    module = path.relative_to(repo_root).as_posix()
    out: list[dict[str, Any]] = []

    patterns: list[tuple[str, re.Pattern[str], Any]] = [
        (
            "source_create",
            re.compile(r"\b(?:map\.)?addSource\(\s*['\"]([^'\"]+)['\"]"),
            lambda g: (f"source:{g[0]}", "addSource"),
        ),
        (
            "layer_create",
            re.compile(r"\b(?:map\.)?addLayer\(\s*\{[\s\S]{0,500}?\bid\s*:\s*['\"]([^'\"]+)['\"]", re.M),
            lambda g: (f"layer:{g[0]}", "addLayer"),
        ),
        (
            "source_remove",
            re.compile(r"\b(?:map\.)?removeSource\(\s*['\"]([^'\"]+)['\"]"),
            lambda g: (f"source:{g[0]}", "removeSource"),
        ),
        (
            "layer_remove",
            re.compile(r"\b(?:map\.)?removeLayer\(\s*['\"]([^'\"]+)['\"]"),
            lambda g: (f"layer:{g[0]}", "removeLayer"),
        ),
        (
            "paint_write",
            re.compile(r"\b(?:map\.)?setPaintProperty\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"),
            lambda g: (f"paint:{g[0]}:{g[1]}", "setPaintProperty"),
        ),
        (
            "layout_write",
            re.compile(r"\b(?:map\.)?setLayoutProperty\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"),
            lambda g: (f"layout:{g[0]}:{g[1]}", "setLayoutProperty"),
        ),
        (
            "set_data",
            re.compile(r"\b(?:map\.)?getSource\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\??\.\s*setData\s*\("),
            lambda g: (f"set-data:{g[0]}", "setData"),
        ),
        (
            "url_write",
            re.compile(r"\bsearchParams\.(?:set|delete)\(\s*['\"]([^'\"]+)['\"]"),
            lambda g: (f"url:{g[0]}", "searchParams"),
        ),
        (
            "public_api",
            re.compile(r"\bwindow\.(__potatoAtlas[A-Za-z0-9_$]+)\s*="),
            lambda g: (f"api:{g[0]}", "window-assign"),
        ),
        (
            "dom_id",
            re.compile(r"\b(?:[A-Za-z_$][\w$]*\.)?id\s*=\s*['\"]([^'\"]+)['\"]"),
            lambda g: (f"dom:{g[0]}", "dom-id"),
        ),
    ]

    for kind, pattern, make in patterns:
        for match, groups in literal_pairs(source, pattern):
            resource_id, operation = make(groups)
            out.append(record(kind, resource_id, module, operation, line_for(source, match.start())))

    # Literal MapLibre event listeners. Layer-scoped listeners have a third literal argument.
    event_pattern = re.compile(
        r"\bmap\.(?:on|once|off)\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?",
        re.M,
    )
    for match in event_pattern.finditer(source):
        event, layer = match.group(1), match.group(2)
        out.append(record("map_listener", f"map-event:{event}:{layer or 'global'}", module, "map-event", line_for(source, match.start()), event=event, layer=layer))
        if event == "styledata":
            out.append(record("style_restore", f"style-restore:{module}", module, "styledata", line_for(source, match.start())))

    dom_event_pattern = re.compile(r"\b(window|document)\.addEventListener\(\s*['\"]([^'\"]+)['\"]")
    for match in dom_event_pattern.finditer(source):
        target, event = match.group(1), match.group(2)
        out.append(record("dom_listener", f"dom-event:{target}:{event}", module, "addEventListener", line_for(source, match.start()), target=target, event=event))

    # Feature-state keys from literal source + literal state object. Bound the state object so this stays conservative.
    fs_pattern = re.compile(
        r"\bmap\.setFeatureState\(\s*\{[\s\S]{0,300}?\bsource\s*:\s*['\"]([^'\"]+)['\"][\s\S]{0,300}?\}\s*,\s*\{([\s\S]{0,400}?)\}\s*\)",
        re.M,
    )
    key_pattern = re.compile(r"(?:^|[,\s])([A-Za-z_$][\w$]*)\s*:")
    for match in fs_pattern.finditer(source):
        source_id, body = match.group(1), match.group(2)
        for key_match in key_pattern.finditer(body):
            key = key_match.group(1)
            out.append(record("feature_state_write", f"feature-state:{source_id}:{key}", module, "setFeatureState", line_for(source, match.start()), source=source_id, key=key))

    # Render-stack registration supports the common register(layer, slot) and register(layer,{slot:'...'}) forms.
    render_patterns = [
        re.compile(r"\b(?:renderStack|stack)\.register\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"),
        re.compile(r"\b(?:renderStack|stack)\.register\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{[\s\S]{0,250}?\bslot\s*:\s*['\"]([^'\"]+)['\"]"),
    ]
    for pattern in render_patterns:
        for match in pattern.finditer(source):
            layer_id, slot = match.group(1), match.group(2)
            out.append(record("render_stack", f"render-stack:{layer_id}", module, "register", line_for(source, match.start()), layer=layer_id, slot=slot))

    popup_matches = list(re.finditer(r"new\s+maplibregl\.Popup\s*\(", source))
    for index, match in enumerate(popup_matches, start=1):
        window_start = max(0, match.start() - 1800)
        window_end = min(len(source), match.end() + 2600)
        context = source[window_start:window_end]
        is_hover = bool(re.search(r"map\.on\(\s*['\"](?:mousemove|mouseenter|mouseover)['\"]", context))
        has_hover_class = "atlas-hover" in context
        out.append(record("popup", f"popup:{module}:{index}", module, "Popup", line_for(source, match.start()), transient=is_hover, has_hover_class=has_hover_class))

    return sorted(out, key=lambda row: (row["module"], row["line"], row["kind"], row["resource"]))


def load_contract(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("World Map audit contract must be a JSON object")
    return payload


def finding(code: str, severity: str, domain: str, message: str, resources: list[str] | None = None, modules: list[str] | None = None, remediation: str | None = None) -> dict[str, Any]:
    item = {
        "code": code,
        "severity": severity,
        "domain": domain,
        "message": message,
        "resources": sorted(set(resources or [])),
        "modules": sorted(set(modules or [])),
    }
    if remediation:
        item["remediation"] = remediation
    return item


def contract_shared(contract: dict[str, Any], resource_id: str, modules: set[str]) -> bool:
    entry = (contract.get("shared") or {}).get(resource_id)
    if not isinstance(entry, dict):
        return False
    expected = set(entry.get("modules") or [])
    return bool(entry.get("rationale")) and modules <= expected


def analyze(records: list[dict[str, Any]], contract: dict[str, Any], existing_modules: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    by_resource: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_resource[row["resource"]].append(row)

    ownership: dict[str, Any] = {}
    for resource_id in sorted(by_resource):
        rows = by_resource[resource_id]
        ownership[resource_id] = sorted({row["module"] for row in rows})

    # Duplicate creator/writer rules.
    collision_rules = (
        ("source:", "source_create", "duplicate-source-owner", "render_ownership", "literal source"),
        ("layer:", "layer_create", "duplicate-layer-owner", "render_ownership", "literal layer"),
        ("feature-state:", "feature_state_write", "feature-state-owner-collision", "feature_state", "feature-state key"),
    )
    for prefix, kind, code, domain, label in collision_rules:
        for resource_id, rows in sorted(by_resource.items()):
            if not resource_id.startswith(prefix):
                continue
            writers = {row["module"] for row in rows if row["kind"] == kind and row["confidence"] == "high"}
            if len(writers) > 1 and not contract_shared(contract, resource_id, writers):
                findings.append(finding(code, "error", domain, f"{label} has multiple uncontracted owners: {resource_id}", [resource_id], list(writers), "Declare intentional sharing with rationale or converge ownership."))

    owners = contract.get("owners") or {}
    if isinstance(owners, dict):
        for resource_id, modules in sorted(owners.items()):
            declared = modules if isinstance(modules, list) else [modules]
            for module in declared:
                if module not in existing_modules:
                    findings.append(finding("declared-owner-module-missing", "error", "render_ownership", f"Declared owner module is absent: {module}", [resource_id], [module], "Update the owner to an existing canonical module or remove the stale declaration."))
            observed_modules = set(ownership.get(resource_id) or [])
            if observed_modules and not observed_modules <= set(declared) and not contract_shared(contract, resource_id, observed_modules):
                findings.append(finding("declared-owner-conflict", "error", "render_ownership", f"Observed owner contradicts canonical owner for {resource_id}", [resource_id], list(observed_modules | set(declared)), "Converge the writer or explicitly document intentional sharing."))

    # Stale shared and ignore entries are warnings.
    for section in ("shared", "ignore"):
        entries = contract.get(section) or {}
        if not isinstance(entries, dict):
            continue
        for resource_id in sorted(entries):
            if section == "ignore" and any(resource_id in row["resource"] for row in records):
                continue
            if section == "shared" and resource_id in by_resource:
                continue
            findings.append(finding("stale-contract-entry", "warning", "render_ownership", f"Contract {section} entry no longer matches live inventory: {resource_id}", [resource_id], remediation="Remove or narrow the stale contract entry."))

    # Transient popup must participate in the Wave 4 drag suppression convention.
    for row in records:
        if row["kind"] == "popup" and row["details"].get("transient") and not row["details"].get("has_hover_class"):
            findings.append(finding("transient-popup-class-missing", "error", "popup_interaction", f"Transient hover popup is not marked with .atlas-hover in {row['module']}", [row["resource"]], [row["module"]], "Add the canonical atlas-hover marker or classify the popup as persistent/click-owned."))

    style_modules = sorted({row["module"] for row in records if row["kind"] == "style_restore"})
    if len(style_modules) > 1:
        findings.append(finding("multiple-style-restorers", "warning", "style_lifecycle", f"{len(style_modules)} modules independently participate in styledata restoration.", [f"style-restore:{m}" for m in style_modules], style_modules, "Keep restoration idempotent and coordinated; use the report to converge lifecycle ownership where races are observed."))

    allowed_slots = set(contract.get("render_stack_slots") or DEFAULT_RENDER_STACK_SLOTS)
    for row in records:
        if row["kind"] == "render_stack":
            slot = row["details"].get("slot")
            if slot and slot not in allowed_slots:
                findings.append(finding("unknown-render-stack-slot", "error", "render_ownership", f"Unknown render-stack slot {slot!r} in {row['module']}", [row["resource"]], [row["module"]], "Use a canonical slot or extend the contract deliberately."))

    # Advisory multi-writer warnings.
    for prefix, kind, code, domain in (
        ("set-data:", "set_data", "multiple-setdata-writers", "data_mutation"),
        ("url:", "url_write", "multiple-url-writers", "url_state"),
        ("dom:", "dom_id", "multiple-dom-creators", "dom_ownership"),
        ("api:", "public_api", "multiple-api-assigners", "event_lifecycle"),
    ):
        for resource_id, rows in sorted(by_resource.items()):
            if not resource_id.startswith(prefix):
                continue
            modules = {row["module"] for row in rows if row["kind"] == kind}
            if len(modules) > 1 and not contract_shared(contract, resource_id, modules):
                findings.append(finding(code, "warning", domain, f"Mutable resource has multiple writers: {resource_id}", [resource_id], list(modules), "Confirm a canonical owner or declare intentional sharing with rationale."))

    findings.sort(key=lambda item: (0 if item["severity"] == "error" else 1 if item["severity"] == "warning" else 2, item["domain"], item["code"], item["message"]))
    return findings, ownership


def build_report(records: list[dict[str, Any]], findings: list[dict[str, Any]], ownership: dict[str, Any]) -> dict[str, Any]:
    inventory: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        inventory[row["kind"]].append(row)
    inventory = {kind: sorted(rows, key=lambda r: (r["resource"], r["module"], r["line"])) for kind, rows in sorted(inventory.items())}

    risk_domains = {domain: 0 for domain in RISK_DOMAINS}
    for item in findings:
        risk_domains.setdefault(item["domain"], 0)
        risk_domains[item["domain"]] += RISK_WEIGHTS.get(item["severity"], 0)
    risk_domains = dict(sorted(risk_domains.items()))
    risk_score = min(100, sum(risk_domains.values()))
    errors = sum(1 for item in findings if item["severity"] == "error")
    warnings = sum(1 for item in findings if item["severity"] == "warning")
    notes = sum(1 for item in findings if item["severity"] == "note")
    modules = sorted({row["module"] for row in records})
    next_actions = [
        {"domain": domain, "risk": score}
        for domain, score in sorted(risk_domains.items(), key=lambda pair: (-pair[1], pair[0]))
        if score > 0
    ][:5]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "world-map",
        "summary": {
            "modules": len(modules),
            "resources": len(ownership),
            "errors": errors,
            "warnings": warnings,
            "notes": notes,
            "risk_score": risk_score,
        },
        "inventory": inventory,
        "ownership": {key: ownership[key] for key in sorted(ownership)},
        "findings": findings,
        "risk_domains": risk_domains,
        "next_actions": next_actions,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit World Map runtime architecture ownership and lifecycle risks.")
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--contract", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    contract_path = (args.contract or (root / "data" / "world-map-audit-contract.json")).resolve()
    report_path = (args.report or (root / "world-map-audit-report.json")).resolve()
    try:
        modules = discover_modules(root)
        records: list[dict[str, Any]] = []
        for path in modules:
            records.extend(scan_module(path, root))
        records.sort(key=lambda row: (row["resource"], row["module"], row["line"], row["kind"]))
        contract = load_contract(contract_path)
        findings, ownership = analyze(records, contract, {path.relative_to(root).as_posix() for path in modules})
        report = build_report(records, findings, ownership)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"WORLD MAP ARCHITECTURE AUDIT FAILED TO RUN: {exc}", file=sys.stderr)
        return 2

    summary = report["summary"]
    print(
        "WORLD MAP ARCHITECTURE AUDIT " + ("FAILED" if summary["errors"] else "PASSED")
        + f" · {summary['modules']} modules · {summary['resources']} resources"
        + f" · {summary['errors']} errors · {summary['warnings']} warnings · risk {summary['risk_score']}"
    )
    for item in report["findings"][:12]:
        print(f"- {item['severity'].upper()} {item['code']}: {item['message']}")
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
