#!/usr/bin/env python3
"""Build neutral, sourced country metrics for the World Map.

Metrics are ordinary dated observations. They never determine Axis height,
project membership, moral rank, or a synthetic country score.
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
OUT = Path(os.environ.get("ATLAS_COUNTRY_METRICS_OUT", ROOT / "data" / "world-country-metrics.json"))
USER_AGENT = "ThePotatoOfLife-world-atlas-country-metrics/1.1"
SOURCE_NAME = "World Bank World Development Indicators"
SOURCE_ID = "world-bank-wdi"
EXPECTED_COUNTRIES = 195
BATCH_SIZE = 4


def metric(label, indicator, unit, domain):
    return {
        "label": label,
        "indicator": indicator,
        "unit": unit,
        "domain": domain,
        "semantic_role": "dated-observation",
        "axis_score": False,
    }


METRICS = {
    "population": metric("Population", "SP.POP.TOTL", "persons", "demography"),
    "gdp": metric("GDP", "NY.GDP.MKTP.CD", "current USD", "economy"),
    "gdp_per_capita": metric("GDP / person", "NY.GDP.PCAP.CD", "current USD/person", "economy"),
    "real_growth": metric("Real GDP growth", "NY.GDP.MKTP.KD.ZG", "percent/year", "economy"),
    "inflation": metric("Consumer price inflation", "FP.CPI.TOTL.ZG", "percent/year", "economy"),
    "unemployment": metric("Unemployment", "SL.UEM.TOTL.ZS", "percent of labour force", "labour"),
    "labor_force_participation": metric("Labour-force participation", "SL.TLF.CACT.ZS", "percent of population ages 15+", "labour"),
    "life_expectancy": metric("Life expectancy", "SP.DYN.LE00.IN", "years", "health/demography"),
    "urbanization": metric("Urban population", "SP.URB.TOTL.IN.ZS", "percent of population", "settlement"),
    "internet_penetration": metric("Internet use", "IT.NET.USER.ZS", "percent of population", "technology/information"),
    "electricity_access": metric("Electricity access", "EG.ELC.ACCS.ZS", "percent of population", "infrastructure/energy"),
    "trade_openness": metric("Trade / GDP", "NE.TRD.GNFS.ZS", "percent of GDP", "trade"),
    "co2_per_capita": metric("CO₂ emissions / person", "EN.GHG.CO2.PC.CE.AR5", "t CO2e/capita", "climate"),
    "fdi_inflow": metric("FDI net inflow", "BX.KLT.DINV.WD.GD.ZS", "percent of GDP", "finance/investment"),
}
INDICATOR_TO_METRIC = {spec["indicator"]: metric_id for metric_id, spec in METRICS.items()}


def get_json(url: str, timeout: int = 120, attempts: int = 3):
    last = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"World Bank request failed after {attempts} attempts: {last}") from last


def empty_series(wanted: set[str]) -> dict[str, dict[str, list[dict]]]:
    return {metric_id: {code: [] for code in wanted} for metric_id in METRICS}


def group_world_bank_rows(rows: list[dict], wanted: set[str]) -> dict[str, dict[str, list[dict]]]:
    grouped = empty_series(wanted)
    for row in rows or []:
        code = str(row.get("countryiso3code") or "").upper()
        indicator = str((row.get("indicator") or {}).get("id") or "")
        metric_id = INDICATOR_TO_METRIC.get(indicator)
        value = row.get("value")
        year = str(row.get("date") or "")
        if code not in wanted or not metric_id or value is None or not year:
            continue
        grouped[metric_id][code].append({"value": value, "year": int(year) if year.isdigit() else year})
    for by_country in grouped.values():
        for code, observations in by_country.items():
            unique = {str(item["year"]): item for item in observations}
            by_country[code] = sorted(unique.values(), key=lambda item: str(item["year"]), reverse=True)[:2]
    return grouped


def merge_series(target, source):
    for metric_id, by_country in source.items():
        for code, observations in by_country.items():
            target[metric_id][code].extend(observations)
            unique = {str(item["year"]): item for item in target[metric_id][code]}
            target[metric_id][code] = sorted(unique.values(), key=lambda item: str(item["year"]), reverse=True)[:2]


def fetch_metric_batch(metric_ids: list[str], wanted: set[str]):
    indicators = ";".join(METRICS[metric_id]["indicator"] for metric_id in metric_ids)
    query = urllib.parse.urlencode({"format":"json", "source":2, "per_page":12000, "mrnev":2})
    url = f"https://api.worldbank.org/v2/country/all/indicator/{urllib.parse.quote(indicators, safe=';')}?{query}"
    payload = get_json(url)
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise RuntimeError(f"Malformed World Bank response for {metric_ids}")
    return group_world_bank_rows(payload[1], wanted)


def fetch_all(wanted: set[str]):
    result = empty_series(wanted)
    errors = []
    ids = list(METRICS)
    for start in range(0, len(ids), BATCH_SIZE):
        batch = ids[start:start+BATCH_SIZE]
        try:
            merge_series(result, fetch_metric_batch(batch, wanted))
        except Exception as batch_error:
            for metric_id in batch:
                try:
                    merge_series(result, fetch_metric_batch([metric_id], wanted))
                except Exception as exc:
                    errors.append({"metric":metric_id, "indicator":METRICS[metric_id]["indicator"], "error":str(exc), "batch_error":str(batch_error)})
    return result, errors


def change(latest, previous):
    if not latest or not previous:
        return None
    try:
        current = float(latest["value"]); prior = float(previous["value"])
    except (KeyError, TypeError, ValueError):
        return None
    result = {"absolute": current-prior}
    if prior != 0:
        result["percent"] = (current-prior)/abs(prior)*100
    return result


def country_metrics_row(country: dict, series: dict, generated_at: str) -> dict:
    code = str(country["iso3"]).upper()
    output = {"country_id":country["id"], "name":country["name"], "metrics":{}}
    for metric_id, spec in METRICS.items():
        observations = series.get(metric_id, {}).get(code, [])
        if not observations:
            continue
        latest = observations[0]
        item = {
            "value":latest["value"], "year":latest["year"], "unit":spec["unit"],
            "indicator":spec["indicator"], "source":SOURCE_NAME, "source_id":SOURCE_ID,
            "status":"sourced", "retrieved_at":generated_at,
        }
        if len(observations) > 1:
            previous = observations[1]
            item["previous"] = {"value":previous["value"], "year":previous["year"]}
            delta = change(latest, previous)
            if delta:
                item["change_from_previous"] = delta
        output["metrics"][metric_id] = item
    return output


def build(out_path: Path = OUT) -> dict:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    countries = index.get("countries", [])
    if len(countries) != EXPECTED_COUNTRIES:
        raise RuntimeError(f"Expected {EXPECTED_COUNTRIES} countries; found {len(countries)}")
    wanted = {str(country["iso3"]).upper() for country in countries}
    series, errors = fetch_all(wanted)
    generated = datetime.now(timezone.utc).isoformat()
    rows = {str(country["iso3"]).upper(): country_metrics_row(country, series, generated) for country in countries}
    coverage = {metric_id: sum(1 for code in wanted if series[metric_id].get(code)) for metric_id in METRICS}
    payload = {
        "version":"1.1.0",
        "generated_at":generated,
        "record_type":"world-country-metrics-runtime",
        "scope":"Neutral comparable country observations. Values do not determine Axis height, moral rank, sovereignty, project membership or a synthetic country score.",
        "source":{"id":SOURCE_ID,"name":SOURCE_NAME,"url":"https://data.worldbank.org/indicator"},
        "missing_rule":"Missing is unknown/unavailable, never zero.",
        "temporal_rule":"Each metric keeps its latest available non-null observation and, when available, one prior comparable observation. Metric years may differ.",
        "metric_order":list(METRICS),
        "metrics":METRICS,
        "coverage":coverage,
        "acquisition_errors":errors,
        "countries":rows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = build()
    print(json.dumps({"output":str(OUT),"countries":len(payload["countries"]),"coverage":payload["coverage"],"errors":len(payload["acquisition_errors"])}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
