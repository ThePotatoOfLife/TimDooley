#!/usr/bin/env python3
"""Build a compact D4 observable-country snapshot for the 3D Atlas.

The runtime keeps a small, globally comparable World Bank WDI vector separate
from project-symbolic Axis height. Every value retains indicator, unit, year,
source and status. Where available, one prior comparable observation is kept so
later D6 change/spiral views can be derived from evidence rather than invented.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
OUT = Path(os.environ.get("ATLAS_D4_OUT", ROOT / "data" / "world-country-observables.json"))
EXPECTED = 195
USER_AGENT = "ThePotatoOfLife-world-atlas-d4/1.5"
BATCH_SIZE = 4

METRICS = {
    "population": {"label": "Population", "indicator": "SP.POP.TOTL", "unit": "persons", "domain": "demography", "role": "scale"},
    "gdp": {"label": "GDP", "indicator": "NY.GDP.MKTP.CD", "unit": "current USD", "domain": "economy", "role": "production scale"},
    "gdp_per_capita": {"label": "GDP / person", "indicator": "NY.GDP.PCAP.CD", "unit": "current USD/person", "domain": "economy", "role": "production per person"},
    "real_growth": {"label": "Real GDP growth", "indicator": "NY.GDP.MKTP.KD.ZG", "unit": "percent/year", "domain": "economy", "role": "motion"},
    "unemployment": {"label": "Unemployment", "indicator": "SL.UEM.TOTL.ZS", "unit": "percent of labour force", "domain": "labour", "role": "labour utilization"},
    "labor_force_participation": {"label": "Labour-force participation", "indicator": "SL.TLF.CACT.ZS", "unit": "percent of population ages 15+", "domain": "labour", "role": "labour-market participation"},
    "life_expectancy": {"label": "Life expectancy", "indicator": "SP.DYN.LE00.IN", "unit": "years", "domain": "health/demography", "role": "human outcome"},
    "fertility_rate": {"label": "Fertility rate", "indicator": "SP.DYN.TFRT.IN", "unit": "births per woman", "domain": "demography", "role": "population reproduction"},
    "urbanization": {"label": "Urban population", "indicator": "SP.URB.TOTL.IN.ZS", "unit": "percent of population", "domain": "settlement", "role": "urbanization"},
    "internet_penetration": {"label": "Internet use", "indicator": "IT.NET.USER.ZS", "unit": "percent of population", "domain": "technology/information", "role": "digital connectivity"},
    "electricity_access": {"label": "Electricity access", "indicator": "EG.ELC.ACCS.ZS", "unit": "percent of population", "domain": "infrastructure/energy", "role": "basic energy access"},
    "trade_openness": {"label": "Trade / GDP", "indicator": "NE.TRD.GNFS.ZS", "unit": "percent of GDP", "domain": "trade", "role": "cross-border trade intensity"},
    "net_migration": {"label": "Net migration", "indicator": "SM.POP.NETM", "unit": "persons over reference period", "domain": "demography/migration", "role": "cross-border population flow balance"},
    "energy_dependence": {"label": "Net energy imports", "indicator": "EG.IMP.CONS.ZS", "unit": "percent of energy use", "domain": "energy", "role": "external energy balance"},
    "fdi_inflow": {"label": "FDI net inflow", "indicator": "BX.KLT.DINV.WD.GD.ZS", "unit": "percent of GDP", "domain": "finance/investment", "role": "cross-border capital inflow intensity"},
    "co2_per_capita": {"label": "CO2 emissions / person", "indicator": "EN.ATM.CO2E.PC", "unit": "metric tons CO2/person", "domain": "environment/energy", "role": "territorial emissions intensity per person"},
}

INDICATOR_TO_METRIC = {spec["indicator"]: metric_id for metric_id, spec in METRICS.items()}


def get_json(url: str, timeout: int = 180, attempts: int = 3):
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.load(response)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(attempt * 1.5)
    raise RuntimeError(f"World Bank request failed after {attempts} attempts: {last_error}")


def empty_series(wanted: set[str]) -> dict[str, dict[str, list[dict]]]:
    return {metric_id: {code: [] for code in wanted} for metric_id in METRICS}


def fetch_batch(metric_ids: list[str], wanted: set[str]) -> dict[str, dict[str, list[dict]]]:
    indicators = ";".join(METRICS[metric_id]["indicator"] for metric_id in metric_ids)
    query = urllib.parse.urlencode({"format": "json", "source": 2, "per_page": 12000, "mrnev": 2})
    url = f"https://api.worldbank.org/v2/country/all/indicator/{urllib.parse.quote(indicators, safe=';')}?{query}"
    payload = get_json(url)
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise RuntimeError(f"World Bank returned malformed D4 payload for batch {metric_ids}")

    allowed = set(metric_ids)
    grouped = {metric_id: {code: [] for code in wanted} for metric_id in metric_ids}
    for row in payload[1]:
        code = str(row.get("countryiso3code") or "").upper()
        indicator = str((row.get("indicator") or {}).get("id") or "")
        metric_id = INDICATOR_TO_METRIC.get(indicator)
        value = row.get("value")
        year = str(row.get("date") or "")
        if code not in wanted or metric_id not in allowed or value is None or not year:
            continue
        grouped[metric_id][code].append({"value": value, "year": int(year) if year.isdigit() else year})
    return grouped


def merge_series(target: dict[str, dict[str, list[dict]]], source: dict[str, dict[str, list[dict]]]) -> None:
    for metric_id, by_code in source.items():
        for code, observations in by_code.items():
            target[metric_id][code].extend(observations)


def fetch_all(wanted: set[str]) -> tuple[dict[str, dict[str, list[dict]]], int, list[str], list[dict]]:
    """Fetch D4 indicators in small resilient batches, recording failed series."""
    grouped = empty_series(wanted)
    metric_ids = list(METRICS)
    request_count = 0
    fallback_metrics: list[str] = []
    failed_metrics: list[dict] = []

    for start in range(0, len(metric_ids), BATCH_SIZE):
        batch = metric_ids[start:start + BATCH_SIZE]
        try:
            print(f"Fetching WDI D4 batch: {', '.join(batch)}", flush=True)
            merge_series(grouped, fetch_batch(batch, wanted))
            request_count += 1
        except Exception as exc:
            print(f"Batch failed ({', '.join(batch)}): {exc}; retrying each series separately.", flush=True)
            for metric_id in batch:
                fallback_metrics.append(metric_id)
                print(f"Fetching WDI D4 fallback series: {metric_id}", flush=True)
                try:
                    merge_series(grouped, fetch_batch([metric_id], wanted))
                    request_count += 1
                except Exception as metric_exc:
                    failed_metrics.append({"metric": metric_id, "indicator": METRICS[metric_id]["indicator"], "error": str(metric_exc)})
                    print(f"SERIES FAILED: {metric_id} ({METRICS[metric_id]['indicator']}): {metric_exc}", flush=True)

    for metric_values in grouped.values():
        for code in metric_values:
            unique: dict[str, dict] = {}
            for item in metric_values[code]:
                unique.setdefault(str(item.get("year")), item)
            observations = list(unique.values())
            observations.sort(key=lambda item: str(item.get("year") or ""), reverse=True)
            metric_values[code] = observations[:2]
    return grouped, request_count, sorted(set(fallback_metrics)), failed_metrics


def delta(latest: dict | None, previous: dict | None) -> dict | None:
    if not latest or not previous:
        return None
    try:
        current = float(latest["value"])
        prior = float(previous["value"])
    except (TypeError, ValueError, KeyError):
        return None
    out = {"absolute": current - prior}
    if prior != 0:
        out["percent"] = (current - prior) / abs(prior) * 100
    return out


def main() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    countries = index.get("countries", [])
    if len(countries) != EXPECTED:
        raise RuntimeError(f"Expected {EXPECTED} canonical countries; found {len(countries)}")

    by_code = {str(country["iso3"]).upper(): country for country in countries}
    wanted = set(by_code)
    series, request_count, fallback_metrics, failed_metrics = fetch_all(wanted)
    coverage = {metric_id: sum(1 for observations in values.values() if observations) for metric_id, values in series.items()}
    print(json.dumps({"d4_coverage": coverage, "requests": request_count, "fallback_metrics": fallback_metrics, "failed_metrics": failed_metrics}, indent=2), flush=True)

    minimum = 150
    failures: list[str] = []
    if coverage["population"] < minimum or coverage["gdp"] < minimum:
        failures.append(f"population={coverage['population']} and gdp={coverage['gdp']} require >= {minimum}")
    for metric_id in ("labor_force_participation", "fertility_rate", "electricity_access", "co2_per_capita"):
        if coverage[metric_id] < 120:
            failures.append(f"{metric_id}={coverage[metric_id]} requires >= 120")
    if failed_metrics:
        failures.append("series acquisition failed for: " + ", ".join(item["metric"] for item in failed_metrics))
    if failures:
        raise RuntimeError("D4 observable build gate failed: " + "; ".join(failures))

    generated = datetime.now(timezone.utc).isoformat()
    rows = {}
    for code, country in by_code.items():
        metrics = {}
        for metric_id, spec in METRICS.items():
            observations = series[metric_id].get(code, [])
            if not observations:
                continue
            latest = observations[0]
            previous = observations[1] if len(observations) > 1 else None
            item = {
                "value": latest["value"], "year": latest["year"], "unit": spec["unit"],
                "source": "World Bank World Development Indicators", "source_id": "world-bank-wdi",
                "indicator": spec["indicator"], "status": "sourced", "retrieved_at": generated,
            }
            if previous:
                item["previous"] = {"value": previous["value"], "year": previous["year"]}
                change = delta(latest, previous)
                if change:
                    item["change_from_previous"] = change
            metrics[metric_id] = item
        rows[code] = {"name": country["name"], "country_id": country["id"], "metrics": metrics}

    payload = {
        "version": "1.5.0",
        "generated_at": generated,
        "record_type": "world-country-observables-runtime",
        "axis_dimension": 4,
        "scope": "Presentation/runtime D4 snapshot. Values remain dated sourced observations and do not determine Axis height, moral rank or project membership.",
        "source": {"id": "world-bank-wdi", "name": "World Bank World Development Indicators", "url": "https://data.worldbank.org/indicator", "api_source_id": 2},
        "acquisition": {"batch_size": BATCH_SIZE, "request_count": request_count, "fallback_metrics": fallback_metrics, "failed_metrics": failed_metrics},
        "metric_order": list(METRICS),
        "metrics": {metric_id: {**spec, "axis_role": "D4 observable"} for metric_id, spec in METRICS.items()},
        "coverage": coverage,
        "country_count": len(rows),
        "temporal_rule": "Latest available non-null observation is shown per metric; years may differ by metric. One prior comparable observation is retained when available for future D6 change analysis.",
        "quality_rules": [
            "Do not compare incompatible units as one height or score.",
            "Do not assume all metrics share the same reference year.",
            "Current USD GDP and GDP/person are not PPP measures.",
            "Unemployment follows the World Bank/ILO series definition and is not identical to every national unemployment series.",
            "Labour-force participation is not an employment rate and retains the source-series definition.",
            "Fertility rate is a total-fertility-rate estimate, not a birth count.",
            "Electricity access does not measure reliability, affordability, generation mix or grid quality.",
            "CO2/person is a territorial emissions indicator, not a consumption-based carbon footprint.",
            "Trade/GDP is gross trade intensity, not bilateral dependency or trade balance.",
            "Net migration is a balance over the source reference period, not a bilateral migration edge.",
            "Negative net energy imports can indicate a net exporter; this measure is not an electricity-mix measure.",
            "FDI net inflow can be negative and does not identify the investor counterpart without bilateral data.",
            "Missing is unknown/unavailable, never zero.",
            "Prior observations seed D6 change analysis but remain ordinary dated D4 observations.",
        ],
        "countries": rows,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "countries": len(rows), "metrics": list(METRICS), "coverage": coverage, "world_bank_requests": request_count, "fallback_metrics": fallback_metrics}, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
