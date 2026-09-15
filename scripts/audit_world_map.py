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
    "render_ownership", "feature_state", "style_lifecycle", "event_lifecycle",
    "popup_interaction", "data_mutation", "url_state", "dom_ownership",
)
DEFAULT_RENDER_STACK_SLOTS = (
    "physical-surface", "physical-water", "physical-line",
    "geography-context", "context-network", "selection-emphasis",
)
HOVER_EVENTS = {"mousemove", "mouseenter", "mouseover"}


def line_for(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def record(kind: str, resource: str, module: str, operation: str, line: int,
           confidence: str = "high", **details: Any) -> dict[str, Any]:
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
    return sorted(world.glob("3d-*.js")) if world.is_dir() else []


def _add_literal_matches(out: list[dict[str, Any]], source: str, module: str,
                         kind: str, pattern: str, build) -> None:
    for match in re.finditer(pattern, source, re.M):
        resource, operation = build(match.groups())
        out.append(record(kind, resource, module, operation, line_for(source, match.start())))


def _nearest_map_event(source: str, offset: int) -> str | None:
    # Classify a popup by the closest preceding map event registration. This avoids
    # treating persistent click popups as transient merely because the same module
    # also has nearby mouseenter cursor handlers.
    event_pattern = re.compile(r"\bmap\.(?:on|once)\(\s*['\"]([^'\"]+)['\"]")
    nearest: str | None = None
    nearest_start = -1
    for match in event_pattern.finditer(source, 0, offset):
        if match.start() > nearest_start:
            nearest_start = match.start()
            nearest = match.group(1)
    return nearest


def scan_module(path: Path, repo_root: Path) -> list[dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    module = path.relative_to(repo_root).as_posix()
    out: list[dict[str, Any]] = []

    literal_specs = (
        ("source_create", r"\b(?:map\.)?addSource\(\s*['\"]([^'\"]+)['\"]", lambda g: (f"source:{g[0]}", "addSource")),
        ("layer_create", r"\b(?:map\.)?addLayer\(\s*\{[\s\S]{0,500}?\bid\s*:\s*['\"]([^'\"]+)['\"]", lambda g: (f"layer:{g[0]}", "addLayer")),
        ("source_remove", r"\b(?:map\.)?removeSource\(\s*['\"]([^'\"]+)['\"]", lambda g: (f"source:{g[0]}", "removeSource")),
        ("layer_remove", r"\b(?:map\.)?removeLayer\(\s*['\"]([^'\"]+)['\"]", lambda g: (f"layer:{g[0]}", "removeLayer")),
        ("paint_write", r"\b(?:map\.)?setPaintProperty\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]", lambda g: (f"paint:{g[0]}:{g[1]}", "setPaintProperty")),
        ("layout_write", r"\b(?:map\.)?setLayoutProperty\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]", lambda g: (f"layout:{g[0]}:{g[1]}", "setLayoutProperty")),
        ("set_data", r"\b(?:map\.)?getSource\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\??\.\s*setData\s*\(", lambda g: (f"set-data:{g[0]}", "setData")),
        ("url_write", r"\bsearchParams\.(?:set|delete)\(\s*['\"]([^'\"]+)['\"]", lambda g: (f"url:{g[0]}", "searchParams")),
        ("public_api", r"\bwindow\.(__potatoAtlas[A-Za-z0-9_$]+)\s*=", lambda g: (f"api:{g[0]}", "window-assign")),
        # Require an actual JS property assignment target. Do not match `id="..."`
        # inside template HTML, especially dynamic ids such as `${esc(asset.id)}`.
        ("dom_id", r"\b[A-Za-z_$][\w$]*\.id\s*=\s*['\"]([^'\"]+)['\"]", lambda g: (f"dom:{g[0]}", "dom-id")),
    )
    for kind, pattern, build in literal_specs:
        _add_literal_matches(out, source, module, kind, pattern, build)

    event_pattern = re.compile(r"\bmap\.(?:on|once|off)\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?")
    for match in event_pattern.finditer(source):
        event, layer = match.group(1), match.group(2)
        out.append(record("map_listener", f"map-event:{event}:{layer or 'global'}", module,
                          "map-event", line_for(source, match.start()), event=event, layer=layer))
        if event == "styledata":
            out.append(record("style_restore", f"style-restore:{module}", module,
                              "styledata", line_for(source, match.start())))

    dom_event_pattern = re.compile(r"\b(window|document)\.addEventListener\(\s*['\"]([^'\"]+)['\"]")
    for match in dom_event_pattern.finditer(source):
        target, event = match.group(1), match.group(2)
        out.append(record("dom_listener", f"dom-event:{target}:{event}", module,
                          "addEventListener", line_for(source, match.start()), target=target, event=event))

    fs_pattern = re.compile(
        r"\bmap\.setFeatureState\(\s*\{[\s\S]{0,300}?\bsource\s*:\s*['\"]([^'\"]+)['\"][\s\S]{0,300}?\}\s*,\s*\{([\s\S]{0,400}?)\}\s*\)",
        re.M,
    )
    # A state key must begin the object or follow a comma. Whitespace alone is not
    # enough because ternary expressions (`condition ? value : 0`) contain colons.
    key_pattern = re.compile(r"(?:^|,)\s*([A-Za-z_$][\w$]*)\s*:")
    for match in fs_pattern.finditer(source):
        source_id, body = match.group(1), match.group(2)
        for key_match in key_pattern.finditer(body):
            key = key_match.group(1)
            out.append(record("feature_state_write", f"feature-state:{source_id}:{key}", module,
                              "setFeatureState", line_for(source, match.start()), source=source_id, key=key))

    render_patterns = (
        re.compile(r"\b(?:renderStack|stack)\.register\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"),
        re.compile(r"\b(?:renderStack|stack)\.register\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{[\s\S]{0,250}?\bslot\s*:\s*['\"]([^'\"]+)['\"]"),
    )
    for pattern in render_patterns:
        for match in pattern.finditer(source):
            layer_id, slot = match.group(1), match.group(2)
            out.append(record("render_stack", f"render-stack:{layer_id}", module, "register",
                              line_for(source, match.start()), layer=layer_id, slot=slot))

    for index, match in enumerate(re.finditer(r"new\s+maplibregl\.Popup\s*\(", source), start=1):
        preceding_event = _nearest_map_event(source, match.start())
        context = source[max(0, match.start() - 1200):min(len(source), match.end() + 2200)]
        out.append(record(
            "popup", f"popup:{module}:{index}", module, "Popup", line_for(source, match.start()),
            transient=preceding_event in HOVER_EVENTS,
            trigger_event=preceding_event,
            has_hover_class="atlas-hover" in context,
        ))

    return sorted(out, key=lambda row: (row["module"], row["line"], row["kind"], row["resource"]))


def load_contract(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("World Map audit contract must be a JSON object")
    return payload


def finding(code: str, severity: str, domain: str, message: str,
            resources: list[str] | None = None, modules: list[str] | None = None,
            remediation: str | None = None) -> dict[str, Any]:
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
    return bool(entry.get("rationale")) and modules <= set(entry.get("modules") or [])


def analyze(records: list[dict[str, Any]], contract: dict[str, Any],
            existing_modules: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    by_resource: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_resource[row["resource"]].append(row)

    ownership = {
        resource: sorted({row["module"] for row in rows})
        for resource, rows in sorted(by_resource.items())
    }

    for prefix, kind, code, domain, label in (
        ("source:", "source_create", "duplicate-source-owner", "render_ownership", "literal source"),
        ("layer:", "layer_create", "duplicate-layer-owner", "render_ownership", "literal layer"),
        ("feature-state:", "feature_state_write", "feature-state-owner-collision", "feature_state", "feature-state key"),
    ):
        for resource_id, rows in sorted(by_resource.items()):
            if not resource_id.startswith(prefix):
                continue
            writers = {row["module"] for row in rows if row["kind"] == kind and row["confidence"] == "high"}
            if len(writers) > 1 and not contract_shared(contract, resource_id, writers):
                findings.append(finding(
                    code, "error", domain, f"{label} has multiple uncontracted owners: {resource_id}",
                    [resource_id], list(writers), "Declare intentional sharing with rationale or converge ownership."
                ))

    owners = contract.get("owners") or {}
    if isinstance(owners, dict):
        for resource_id, modules in sorted(owners.items()):
            declared = modules if isinstance(modules, list) else [modules]
            for module in declared:
                if module not in existing_modules:
                    findings.append(finding(
                        "declared-owner-module-missing", "error", "render_ownership",
                        f"Declared owner module is absent: {module}", [resource_id], [module],
                        "Update the owner to an existing canonical module or remove the stale declaration."
                    ))
            observed = set(ownership.get(resource_id) or [])
            if observed and not observed <= set(declared) and not contract_shared(contract, resource_id, observed):
                findings.append(finding(
                    "declared-owner-conflict", "error", "render_ownership",
                    f"Observed owner contradicts canonical owner for {resource_id}",
                    [resource_id], list(observed | set(declared)),
                    "Converge the writer or explicitly document intentional sharing."
                ))

    for section in ("shared", "ignore"):
        entries = contract.get(section) or {}
        if not isinstance(entries, dict):
            continue
        for resource_id in sorted(entries):
            matched = resource_id in by_resource if section == "shared" else any(resource_id in row["resource"] for row in records)
            if not matched:
                findings.append(finding(
                    "stale-contract-entry", "warning", "render_ownership",
                    f"Contract {section} entry no longer matches live inventory: {resource_id}",
                    [resource_id], remediation="Remove or narrow the stale contract entry."
                ))

    for row in records:
        if row["kind"] == "popup" and row["details"].get("transient") and not row["details"].get("has_hover_class"):
            findings.append(finding(
                "transient-popup-class-missing", "error", "popup_interaction",
                f"Transient hover popup is not marked with .atlas-hover in {row['module']}",
                [row["resource"]], [row["module"]],
                "Add the canonical atlas-hover marker or classify the popup as persistent/click-owned."
            ))

    style_modules = sorted({row["module"] for row in records if row["kind"] == "style_restore"})
    if len(style_modules) > 1:
        findings.append(finding(
            "multiple-style-restorers", "warning", "style_lifecycle",
            f"{len(style_modules)} modules independently participate in styledata restoration.",
            [f"style-restore:{module}" for module in style_modules], style_modules,
            "Keep restoration idempotent and coordinated; converge lifecycle ownership where races are observed."
        ))

    allowed_slots = set(contract.get("render_stack_slots") or DEFAULT_RENDER_STACK_SLOTS)
    for row in records:
        if row["kind"] == "render_stack" and row["details"].get("slot") not in allowed_slots:
            slot = row["details"].get("slot")
            findings.append(finding(
                "unknown-render-stack-slot", "error", "render_ownership",
                f"Unknown render-stack slot {slot!r} in {row['module']}",
                [row["resource"]], [row["module"]], "Use a canonical slot or extend the contract deliberately."
            ))

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
                findings.append(finding(
                    code, "warning", domain, f"Mutable resource has multiple writers: {resource_id}",
                    [resource_id], list(modules), "Confirm a canonical owner or declare intentional sharing with rationale."
                ))

    findings.sort(key=lambda item: (
        0 if item["severity"] == "error" else 1 if item["severity"] == "warning" else 2,
        item["domain"], item["code"], item["message"],
    ))
    return findings, ownership


def build_report(records: list[dict[str, Any]], findings: list[dict[str, Any]],
                 ownership: dict[str, Any]) -> dict[str, Any]:
    inventory: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        inventory[row["kind"]].append(row)
    ordered_inventory = {
        kind: sorted(rows, key=lambda row: (row["resource"], row["module"], row["line"]))
        for kind, rows in sorted(inventory.items())
    }
    risk_domains = {domain: 0 for domain in RISK_DOMAINS}
    for item in findings:
        risk_domains[item["domain"]] = risk_domains.get(item["domain"], 0) + RISK_WEIGHTS.get(item["severity"], 0)
    risk_domains = dict(sorted(risk_domains.items()))
    modules = sorted({row["module"] for row in records})
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    notes = sum(item["severity"] == "note" for item in findings)
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
            "risk_score": min(100, sum(risk_domains.values())),
        },
        "inventory": ordered_inventory,
        "ownership": {key: ownership[key] for key in sorted(ownership)},
        "findings": findings,
        "risk_domains": risk_domains,
        "next_actions": next_actions,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit World Map runtime architecture ownership and lifecycle risks.")
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--contract", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    contract_path = (args.contract or (root / "data" / "world-map-audit-contract.json")).resolve()
    report_path = (args.report or (root / "world-map-audit-report.json")).resolve()
    try:
        modules = [path for path in discover_modules(root) if path.is_file()]
        records: list[dict[str, Any]] = []
        for path in modules:
            records.extend(scan_module(path, root))
        records.sort(key=lambda row: (row["resource"], row["module"], row["line"], row["kind"]))
        contract = load_contract(contract_path)
        findings, ownership = analyze(records, contract, {path.relative_to(root).as_posix() for path in modules})
        report = build_report(records, findings, ownership)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"WORLD MAP ARCHITECTURE AUDIT FAILED TO RUN: {exc}", file=sys.stderr)
        return 2

    summary = report["summary"]
    state = "FAILED" if summary["errors"] else "PASSED"
    print(
        f"WORLD MAP ARCHITECTURE AUDIT {state} · {summary['modules']} modules · "
        f"{summary['resources']} resources · {summary['errors']} errors · "
        f"{summary['warnings']} warnings · risk {summary['risk_score']}"
    )
    for item in report["findings"][:12]:
        print(f"- {item['severity'].upper()} {item['code']}: {item['message']}")
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
