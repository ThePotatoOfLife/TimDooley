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
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
OUT = Path(os.environ.get("ATLAS_D4_OUT", ROOT / "data" / "world-country-observables.json"))
EXPECTED = 195
USER_AGENT = "ThePotatoOfLife-world-atlas-d4/1.2"

METRICS = {
    "population": {
        "label": "Population",
        "indicator": "SP.POP.TOTL",
        "unit": "persons",
        "domain": "demography",
        "role": "scale",
    },
    "gdp": {
        "label": "GDP",
        "indicator": "NY.GDP.MKTP.CD",
        "unit": "current USD",
        "domain": "economy",
        "role": "production scale",
    },
    "gdp_per_capita": {
        "label": "GDP / person",
        "indicator": "NY.GDP.PCAP.CD",
        "unit": "current USD/person",
        "domain": "economy",
        "role": "production per person",
    },
    "real_growth": {
        "label": "Real GDP growth",
        "indicator": "NY.GDP.MKTP.KD.ZG",
        "unit": "percent/year",
        "domain": "economy",
        "role": "motion",
    },
    "unemployment": {
        "label": "Unemployment",
        "indicator": "SL.UEM.TOTL.ZS",
        "unit": "percent of labour force",
        "domain": "labour",
        "role": "labour utilization",
    },
    "life_expectancy": {
        "label": "Life expectancy",
        "indicator": "SP.DYN.LE00.IN",
        "unit": "years",
        "domain": "health/demography",
        "role": "human outcome",
    },
    "urbanization": {
        "label": "Urban population",
        "indicator": "SP.URB.TOTL.IN.ZS",
        "unit": "percent of population",
        "domain": "settlement",
        "role": "urbanization",
    },
    "internet_penetration": {
        "label": "Internet use",
        "indicator": "IT.NET.USER.ZS",
        "unit": "percent of population",
        "domain": "technology/information",
        "role": "digital connectivity",
    },
    "trade_openness": {
        "label": "Trade / GDP",
        "indicator": "NE.TRD.GNFS.ZS",
        "unit": "percent of GDP",
        "domain": "trade",
        "role": "cross-border trade intensity",
    },
    "net_migration": {
        "label": "Net migration",
        "indicator": "SM.POP.NETM",
        "unit": "persons over reference period",
        "domain": "demography/migration",
        "role": "cross-border population flow balance",
    },
    "energy_dependence": {
        "label": "Net energy imports",
        "indicator": "EG.IMP.CONS.ZS",
        "unit": "percent of energy use",
        "domain": "energy",
        "role": "external energy balance",
    },
    "fdi_inflow": {
        "label": "FDI net inflow",
        "indicator": "BX.KLT.DINV.WD.GD.ZS",
        "unit": "percent of GDP",
        "domain": "finance/investment",
        "role": "cross-border capital inflow intensity",
    },
}

INDICATOR_TO_METRIC = {spec["indicator"]: metric_id for metric_id, spec in METRICS.items()}


def get_json(url: str, timeout: int = 180):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def fetch_all(wanted: set[str]) -> dict[str, dict[str, list[dict]]]:
    """Fetch the Source-2 WDI D4 indicators in one batched API request."""
    indicators = ";".join(spec["indicator"] for spec in METRICS.values())
    query = urllib.parse.urlencode({
        "format": "json",
        "source": 2,
        "per_page": 20000,
        "mrnev": 2,
    })
    payload = get_json(
        f"https://api.worldbank.org/v2/country/all/indicator/{urllib.parse.quote(indicators, safe=';')}?{query}"
    )
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise RuntimeError("World Bank returned malformed batched D4 payload")

    grouped = {
        metric_id: {code: [] for code in wanted}
        for metric_id in METRICS
    }
    for row in payload[1]:
        code = str(row.get("countryiso3code") or "").upper()
        indicator = str((row.get("indicator") or {}).get("id") or "")
        metric_id = INDICATOR_TO_METRIC.get(indicator)
        value = row.get("value")
        year = str(row.get("date") or "")
        if code not in wanted or not metric_id or value is None or not year:
            continue
        grouped[metric_id][code].append({
            "value": value,
            "year": int(year) if year.isdigit() else year,
        })

    for metric_values in grouped.values():
        for code in metric_values:
            metric_values[code].sort(key=lambda item: str(item.get("year") or ""), reverse=True)
            metric_values[code] = metric_values[code][:2]
    return grouped


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
    series = fetch_all(wanted)
    coverage = {
        metric_id: sum(1 for observations in values.values() if observations)
        for metric_id, values in series.items()
    }

    minimum = 150
    if coverage["population"] < minimum or coverage["gdp"] < minimum:
        raise RuntimeError(
            f"D4 observable coverage too low: population={coverage['population']}, "
            f"gdp={coverage['gdp']}, required_each>={minimum}"
        )

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
                "value": latest["value"],
                "year": latest["year"],
                "unit": spec["unit"],
                "source": "World Bank World Development Indicators",
                "source_id": "world-bank-wdi",
                "indicator": spec["indicator"],
                "status": "sourced",
                "retrieved_at": generated,
            }
            if previous:
                item["previous"] = {
                    "value": previous["value"],
                    "year": previous["year"],
                }
                change = delta(latest, previous)
                if change:
                    item["change_from_previous"] = change
            metrics[metric_id] = item
        rows[code] = {
            "name": country["name"],
            "country_id": country["id"],
            "metrics": metrics,
        }

    payload = {
        "version": "1.2.0",
        "generated_at": generated,
        "record_type": "world-country-observables-runtime",
        "axis_dimension": 4,
        "scope": "Presentation/runtime D4 snapshot. Values remain dated sourced observations and do not determine Axis height, moral rank or project membership.",
        "source": {
            "id": "world-bank-wdi",
            "name": "World Bank World Development Indicators",
            "url": "https://data.worldbank.org/indicator",
            "api_source_id": 2,
        },
        "metric_order": list(METRICS),
        "metrics": {
            metric_id: {**spec, "axis_role": "D4 observable"}
            for metric_id, spec in METRICS.items()
        },
        "coverage": coverage,
        "country_count": len(rows),
        "temporal_rule": "Latest available non-null observation is shown per metric; years may differ by metric. One prior comparable observation is retained when available for future D6 change analysis.",
        "quality_rules": [
            "Do not compare incompatible units as one height or score.",
            "Do not assume all metrics share the same reference year.",
            "Current USD GDP and GDP/person are not PPP measures.",
            "Unemployment follows the World Bank/ILO series definition and is not identical to every national unemployment series.",
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
    print(json.dumps({
        "output": str(OUT),
        "countries": len(rows),
        "metrics": list(METRICS),
        "coverage": coverage,
        "world_bank_requests": 1,
    }, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
