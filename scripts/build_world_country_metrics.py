#!/usr/bin/env python3
"""Build the harmonized same-origin country-metric runtime for the 3D Atlas.

World Bank WDI supplies cross-country comparable observations. If acquisition is
temporarily unavailable, the builder may reuse only canonical observations that
carry the exact expected WDI indicator id; incompatible national/local values are
never promoted merely to fill coverage. Population density is a labeled derived
presentation value using the same population observation and atlas area snapshot.
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

from refresh_country_atlas import INDICATORS, world_bank

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRIES_DIR = ROOT / "data" / "countries"
DEFAULT_OUT = ROOT / "data" / "world-country-metrics.json"
EXPECTED = 195
MINIMUM_CORE_COVERAGE = 150

METRIC_META = {
    "population": {"label": "Population", "unit": "people", "transform": "log1p"},
    "gdp": {"label": "GDP", "unit": "current USD", "transform": "log1p"},
    "gdp_per_capita": {"label": "GDP per capita", "unit": "current USD / person", "transform": "log1p"},
    "gdp_per_capita_ppp": {"label": "GDP per capita PPP", "unit": "current international $ / person", "transform": "log1p"},
    "real_growth": {"label": "Real GDP growth", "unit": "percent", "transform": "diverging-zero"},
    "inflation": {"label": "Inflation", "unit": "percent", "transform": "diverging-zero"},
    "unemployment": {"label": "Unemployment", "unit": "percent of labour force", "transform": "bounded-percent"},
    "labour_force_participation": {"label": "Labour-force participation", "unit": "percent age 15+", "transform": "bounded-percent"},
    "life_expectancy": {"label": "Life expectancy", "unit": "years", "transform": "linear"},
    "fertility": {"label": "Fertility", "unit": "births / woman", "transform": "linear"},
    "urbanization": {"label": "Urbanization", "unit": "percent of population", "transform": "bounded-percent"},
    "poverty": {"label": "National poverty headcount", "unit": "percent", "transform": "bounded-percent"},
    "co2_emissions": {"label": "CO₂ emissions per capita", "unit": "t CO₂ / person", "transform": "log1p"},
    "internet_penetration": {"label": "Internet penetration", "unit": "percent of population", "transform": "bounded-percent"},
}


def finite_number(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def percentile(values: list[float], fraction: float) -> float | None:
    values = sorted(v for v in values if math.isfinite(v))
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    position = max(0.0, min(1.0, fraction)) * (len(values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1.0 - weight) + values[upper] * weight


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else default


def canonical_fallback(countries: list[dict]) -> dict[str, dict[str, dict]]:
    """Return only locally stored observations proven to use the expected WDI id."""
    by_field: dict[str, dict[str, dict]] = {field: {} for field in INDICATORS}
    for country in countries:
        code = str(country.get("iso3") or "").upper()
        record = load_json(COUNTRIES_DIR / f"{country['id']}.json")
        observations = record.get("observations") if isinstance(record.get("observations"), dict) else {}
        for field, indicator in INDICATORS.items():
            raw = observations.get(field)
            if not isinstance(raw, dict) or raw.get("indicator") != indicator:
                continue
            value = finite_number(raw.get("value"))
            if value is None:
                continue
            by_field[field][code] = {
                "value": value,
                "year": raw.get("year") or raw.get("reference_period"),
                "source": raw.get("source") or "world-bank",
                "indicator": indicator,
                "confidence": raw.get("confidence") or "stored-comparable-observation",
            }
    return by_field


def acquire(countries: list[dict]) -> tuple[dict[str, dict[str, dict]], list[str]]:
    """Acquire each indicator independently so one provider error does not erase others."""
    fallback = canonical_fallback(countries)
    by_field: dict[str, dict[str, dict]] = {field: dict(rows) for field, rows in fallback.items()}
    errors: list[str] = []
    for field in INDICATORS:
        try:
            result = world_bank([field]).get(field, {})
            if result:
                by_field[field] = result
        except Exception as exc:
            errors.append(f"{field}: {exc}")
    return by_field, errors


def metric_observation(field: str, raw: dict) -> dict | None:
    value = finite_number(raw.get("value"))
    if value is None:
        return None
    period = raw.get("year") or raw.get("period") or raw.get("reference_period")
    if period in (None, ""):
        return None
    return {
        "value": int(value) if field == "population" and value.is_integer() else value,
        "unit": METRIC_META[field]["unit"],
        "period": period,
        "source": "World Bank WDI",
        "source_id": INDICATORS[field],
        "confidence": raw.get("confidence") or "international-official",
    }


def area_snapshot(out_path: Path) -> dict[str, dict]:
    candidates = [out_path.with_name("world-country-facts.json"), ROOT / "data" / "world-country-facts.json"]
    for path in candidates:
        if path.exists():
            payload = load_json(path)
            rows = payload.get("countries") if isinstance(payload, dict) else None
            if isinstance(rows, dict):
                return rows
    return {}


def add_density(rows: dict[str, dict], facts: dict[str, dict]) -> None:
    for code, metrics in rows.items():
        population = metrics.get("population")
        area = finite_number(facts.get(code, {}).get("area_km2"))
        pop = finite_number(population.get("value")) if isinstance(population, dict) else None
        if pop is None or area is None or area <= 0:
            continue
        metrics["population_density"] = {
            "value": pop / area,
            "unit": "people / km²",
            "period": population.get("period"),
            "source": "World Bank WDI population + atlas area snapshot",
            "derived": True,
            "components": {
                "population_source_id": INDICATORS["population"],
                "population_period": population.get("period"),
                "area_km2": area,
                "area_source": facts.get(code, {}).get("field_sources", {}).get("area_km2") or facts.get(code, {}).get("source_owner") or "atlas area snapshot",
                "area_definition": facts.get(code, {}).get("area_definition") or "area",
            },
        }


def registry(rows: dict[str, dict]) -> dict[str, dict]:
    definitions: dict[str, dict] = {}
    all_meta = dict(METRIC_META)
    all_meta["population_density"] = {
        "label": "Population density",
        "unit": "people / km²",
        "transform": "log1p",
        "derived": True,
    }
    for metric_id, meta in all_meta.items():
        values = [finite_number(country.get(metric_id, {}).get("value")) for country in rows.values()]
        values = [value for value in values if value is not None]
        entry = {
            **meta,
            "direction": "neutral",
            "coverage": len(values),
        }
        if metric_id in INDICATORS:
            entry["indicator"] = INDICATORS[metric_id]
        if values:
            entry["observed_domain"] = [min(values), max(values)]
            low, high = percentile(values, 0.02), percentile(values, 0.98)
            entry["display_domain"] = [low, high]
            entry["display_domain_method"] = "2nd–98th percentile clipping for color readability; raw values unchanged"
        definitions[metric_id] = entry
    return definitions


def build(out_path: Path | str | None = None) -> dict:
    out = Path(out_path or os.environ.get("ATLAS_METRICS_OUT", DEFAULT_OUT))
    index = load_json(INDEX)
    countries = index.get("countries", [])
    if len(countries) != EXPECTED:
        raise RuntimeError(f"Expected {EXPECTED} canonical countries; found {len(countries)}")
    canonical = {country["iso3"] for country in countries}
    by_field, acquisition_errors = acquire(countries)

    rows: dict[str, dict] = {code: {} for code in canonical}
    for field in INDICATORS:
        for code, raw in by_field[field].items():
            if code not in canonical:
                continue
            observation = metric_observation(field, raw)
            if observation:
                rows[code][field] = observation

    facts = area_snapshot(out)
    add_density(rows, facts)
    rows = {code: metrics for code, metrics in rows.items() if metrics}
    definitions = registry(rows)
    for core in ("population", "gdp"):
        if definitions.get(core, {}).get("coverage", 0) < MINIMUM_CORE_COVERAGE:
            raise RuntimeError(
                f"Refusing incomplete metric runtime: {core} coverage="
                f"{definitions.get(core, {}).get('coverage', 0)} < {MINIMUM_CORE_COVERAGE}; "
                f"acquisition_errors={acquisition_errors}"
            )

    payload = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_type": "world-country-metrics-runtime",
        "scope": "Presentation/runtime projection of cross-country comparable indicators. Canonical country records remain source owners for country-specific enrichment.",
        "reference_policy": "Latest non-null WDI observation among the provider's most recent five periods; periods remain visible and values are never projected backward in historical Time mode.",
        "acquisition_errors": acquisition_errors,
        "metrics": definitions,
        "countries": rows,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    out = Path(os.environ.get("ATLAS_METRICS_OUT", DEFAULT_OUT))
    payload = build(out)
    print(json.dumps({
        "output": str(out),
        "countries": len(payload["countries"]),
        "metrics": {key: value.get("coverage", 0) for key, value in payload["metrics"].items()},
        "acquisition_errors": payload["acquisition_errors"],
    }, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
