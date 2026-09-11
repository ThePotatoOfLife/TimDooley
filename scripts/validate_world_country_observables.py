#!/usr/bin/env python3
"""Validate the built D4 observable runtime and its 3D Atlas consumers."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
SNAPSHOT = SITE / "data" / "world-country-observables.json"
REPORT = ROOT / "world-country-observables-report.txt"

EXPECTED_METRICS = {
    "population": "SP.POP.TOTL",
    "gdp": "NY.GDP.MKTP.CD",
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "real_growth": "NY.GDP.MKTP.KD.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
    "labor_force_participation": "SL.TLF.CACT.ZS",
    "life_expectancy": "SP.DYN.LE00.IN",
    "fertility_rate": "SP.DYN.TFRT.IN",
    "urbanization": "SP.URB.TOTL.IN.ZS",
    "internet_penetration": "IT.NET.USER.ZS",
    "electricity_access": "EG.ELC.ACCS.ZS",
    "trade_openness": "NE.TRD.GNFS.ZS",
    "net_migration": "SM.POP.NETM",
    "energy_dependence": "EG.IMP.CONS.ZS",
    "fdi_inflow": "BX.KLT.DINV.WD.GD.ZS",
    "co2_per_capita": "EN.ATM.CO2E.PC",
}

PARITY_FILES = (
    "world-map/3d-selection-ui.js",
    "world-map/3d-country-dimensions.js",
    "world-map/3d-d4-observables.js",
    "world-map/3d-metric-dimensions.js",
)


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for rel in PARITY_FILES:
        source = ROOT / rel
        built = SITE / rel
        if not source.exists():
            errors.append(f"missing source Atlas module: {rel}")
            continue
        if not built.exists():
            errors.append(f"built Pages artifact omitted Atlas module: {rel}")
            continue
        if source.read_bytes() != built.read_bytes():
            errors.append(f"built Atlas module drifted from validated source: {rel}")

    if not SNAPSHOT.exists():
        errors.append("built Pages artifact omitted data/world-country-observables.json")
        snapshot = {}
    else:
        snapshot = load_json(SNAPSHOT, errors)

    if snapshot:
        if snapshot.get("record_type") != "world-country-observables-runtime":
            errors.append("D4 snapshot has unexpected record_type")
        if snapshot.get("axis_dimension") != 4:
            errors.append("D4 snapshot must remain an Axis-D4 observable runtime")
        countries = snapshot.get("countries", {})
        if not isinstance(countries, dict) or len(countries) != 195:
            errors.append(f"D4 snapshot must contain 195 canonical countries; found {len(countries) if isinstance(countries, dict) else 'non-object'}")
        if snapshot.get("country_count") != 195:
            errors.append(f"D4 snapshot country_count must be 195; found {snapshot.get('country_count')}")

        registry = snapshot.get("metrics", {})
        metric_order = snapshot.get("metric_order", [])
        missing = sorted(set(EXPECTED_METRICS) - set(registry))
        if missing:
            errors.append(f"D4 snapshot metric registry missing: {missing}")
        if set(metric_order) != set(EXPECTED_METRICS):
            errors.append("D4 snapshot metric_order does not match the 16-metric runtime contract")
        for metric_id, indicator in EXPECTED_METRICS.items():
            spec = registry.get(metric_id, {})
            if spec.get("indicator") != indicator:
                errors.append(f"D4 metric {metric_id} lost indicator {indicator}")
            if not spec.get("unit"):
                errors.append(f"D4 metric {metric_id} has no explicit unit")

        coverage = snapshot.get("coverage", {})
        for metric_id in ("population", "gdp"):
            if int(coverage.get(metric_id, 0) or 0) < 150:
                errors.append(f"D4 {metric_id} coverage fell below 150")
        for metric_id in ("labor_force_participation", "fertility_rate", "electricity_access", "co2_per_capita"):
            if int(coverage.get(metric_id, 0) or 0) < 120:
                errors.append(f"D4 {metric_id} coverage fell below 120")

        previous_count = 0
        typed_count = 0
        for code, row in countries.items() if isinstance(countries, dict) else []:
            metrics = row.get("metrics", {}) if isinstance(row, dict) else {}
            for metric_id, item in metrics.items():
                if metric_id not in EXPECTED_METRICS or not isinstance(item, dict):
                    continue
                if item.get("value") is not None and item.get("year") is not None and item.get("indicator") and item.get("unit"):
                    typed_count += 1
                previous = item.get("previous")
                if isinstance(previous, dict) and previous.get("value") is not None and previous.get("year") is not None:
                    previous_count += 1
        if typed_count < 1500:
            errors.append(f"D4 snapshot typed observation count suspiciously low: {typed_count}")
        if previous_count < 1000:
            warnings.append(f"D6 seed coverage is lower than expected: {previous_count} prior comparable observations")

    observable_js = ROOT / "world-map" / "3d-d4-observables.js"
    metric_js = ROOT / "world-map" / "3d-metric-dimensions.js"
    if observable_js.exists():
        text = observable_js.read_text(encoding="utf-8")
        for marker in ("atlas-d4-compare", "D6 seed", "labor_force_participation", "electricity_access", "fertility_rate", "co2_per_capita"):
            if marker not in text:
                errors.append(f"D4 inspector missing integration marker: {marker}")
    if metric_js.exists():
        text = metric_js.read_text(encoding="utf-8")
        for marker in ("axis:d3-coverage", "axis:d6-change", "labor_force_participation", "electricity_access"):
            if marker not in text:
                errors.append(f"D4 metric-height module missing integration marker: {marker}")

    lines = [
        f"D4 observable runtime errors: {len(errors)} · warnings: {len(warnings)}",
        *[f"WARNING: {warning}" for warning in warnings],
    ]
    if errors:
        lines.append("D4 OBSERVABLE VALIDATION FAILED")
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("D4 OBSERVABLE VALIDATION PASSED")
    report = "\n".join(lines) + "\n"
    REPORT.write_text(report, encoding="utf-8")
    print(report, end="")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
