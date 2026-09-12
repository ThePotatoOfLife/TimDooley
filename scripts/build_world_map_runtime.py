#!/usr/bin/env python3
"""Generate the compact World Map browser runtime.

This projection never fetches the network. Canonical country records, explicit
institutional memberships, project Axis profiles, and functional-chain records
remain the source owners; this file only reshapes them for fast browser use.
"""
from __future__ import annotations

import json
import math
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTRY_INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRY_DIR = ROOT / "data" / "countries"
MEMBERSHIPS = ROOT / "data" / "world-institution-memberships.json"
AXIS_PROFILES = ROOT / "data" / "world-axis-profiles.json"
SYSTEM_CHAINS = ROOT / "data" / "world-system-chains.json"
RUNTIME_OUT = ROOT / "data" / "world-map-data-runtime.json"

METRICS = {
    "gdp_per_capita": {"label":"GDP / person","unit":"current USD / person","observation_aliases":["gdp_per_capita"],"fallback":("economy","gdp_per_capita_usd"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "real_growth": {"label":"Real GDP growth","unit":"percent/year","observation_aliases":["real_growth","real_gdp_growth"],"fallback":("economy","gdp_growth_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "inflation": {"label":"Inflation","unit":"percent/year","observation_aliases":["inflation"],"fallback":("economy","inflation_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "unemployment": {"label":"Unemployment","unit":"percent of labour force","observation_aliases":["unemployment"],"fallback":("economy","unemployment_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "debt_to_gdp": {"label":"Debt / GDP","unit":"percent","observation_aliases":["debt_to_gdp","government_debt_to_gdp"],"fallback":("public_finance","debt_to_gdp"),"fallback_period":("public_finance","year"),"fallback_source":("public_finance","source"),"fallback_source_url":("public_finance","source_url")},
}

INDICATOR_URLS = {
    "NY.GDP.PCAP.CD": "https://data.worldbank.org/indicator/NY.GDP.PCAP.CD",
    "NY.GDP.MKTP.KD.ZG": "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG",
    "FP.CPI.TOTL.ZG": "https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG",
    "SL.UEM.TOTL.ZS": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS",
}
ORDINARY_AXIS_ROLES = {"primary", "secondary", "bridge", "shared"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def nested(record: dict, path: tuple[str, ...]):
    value = record
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def number(value):
    try:
        candidate = float(value)
    except (TypeError, ValueError):
        return None
    return candidate if math.isfinite(candidate) else None


def observation_cell(record: dict, metric_id: str, definition: dict):
    observations = record.get("observations", {})
    for alias in definition["observation_aliases"]:
        raw = observations.get(alias)
        if not isinstance(raw, dict):
            continue
        value = number(raw.get("value"))
        if value is None:
            continue
        indicator = raw.get("indicator")
        return {"value":value,"unit":definition["unit"],"period":raw.get("year") or raw.get("reference_period") or raw.get("period"),"source":raw.get("source") or "canonical country observation","source_url":raw.get("source_url") or INDICATOR_URLS.get(indicator),"indicator":indicator,"confidence":raw.get("confidence")}
    return None


def fallback_cell(record: dict, metric_id: str, definition: dict):
    raw = nested(record, definition["fallback"])
    if isinstance(raw, dict):
        value = number(raw.get("value")); period = raw.get("year") or raw.get("reference_period") or raw.get("period"); source = raw.get("source"); source_url = raw.get("source_url")
    else:
        value = number(raw); period = nested(record, definition["fallback_period"]); source = nested(record, definition["fallback_source"]); source_url = nested(record, definition["fallback_source_url"])
    if value is None:
        return None
    return {"value":value,"unit":definition["unit"],"period":period,"source":source or "canonical country record","source_url":source_url,"indicator":None,"confidence":None}


def metric_cell(record: dict, metric_id: str, definition: dict):
    return observation_cell(record, metric_id, definition) or fallback_cell(record, metric_id, definition)


def normalize_axis_profile(profile: dict, default_profile: dict) -> dict:
    source = profile if isinstance(profile, dict) else default_profile
    orientations = []
    for item in source.get("orientations", []) if isinstance(source, dict) else []:
        if not isinstance(item, dict):
            continue
        orientations.append({
            "axis": item.get("axis"),
            "role": item.get("role"),
            "basis": item.get("basis"),
            "confidence": item.get("confidence"),
            "note": item.get("note"),
        })
    return {"status": source.get("status") or ("classified" if orientations else "unresolved"), "orientations": orientations}


def build_runtime() -> dict:
    index = load(COUNTRY_INDEX)
    countries = index.get("countries", [])
    if len(countries) != 195:
        raise RuntimeError(f"canonical country index must contain 195 countries; found {len(countries)}")

    memberships = load(MEMBERSHIPS)
    axis_source = load(AXIS_PROFILES)
    chain_source = load(SYSTEM_CHAINS)

    groups = {}
    for group_id, group in memberships.get("groups", {}).items():
        members = list(group.get("members", []))
        groups[group_id] = {
            "label": group.get("label", group_id),
            "members": members,
            "member_count": len(members),
            "official_member_count": group.get("official_member_count", len(members)),
            "non_country_members": list(group.get("non_country_members", [])),
            "non_canonical_members": list(group.get("non_canonical_members", [])),
            "suspended_members": list(group.get("suspended_members", [])),
            "observer_states": list(group.get("observer_states", [])),
            "as_of": group.get("as_of"),
            "source": group.get("source"),
            "source_url": group.get("source_url"),
            "notes": group.get("notes"),
        }

    runtime_countries: dict[str, dict] = {}
    runtime_axis_countries: dict[str, dict] = {}
    axis_memberships = {axis_id: [] for axis_id in axis_source.get("axes", {})}
    axis_profiles = axis_source.get("profiles", {})
    default_axis_profile = axis_source.get("default_profile", {"status":"unresolved","orientations":[]})
    coverage = {metric_id: 0 for metric_id in METRICS}
    periods = {metric_id: [] for metric_id in METRICS}

    for row in countries:
        code = str(row.get("iso3") or "").upper()
        country_id = row.get("id")
        if not code or not country_id:
            raise RuntimeError(f"country index row missing identity: {row}")
        record_path = COUNTRY_DIR / f"{country_id}.json"
        if not record_path.is_file():
            raise RuntimeError(f"missing canonical country record: {record_path.relative_to(ROOT)}")
        record = load(record_path)
        cells = {}
        for metric_id, definition in METRICS.items():
            cell = metric_cell(record, metric_id, definition)
            if not cell:
                continue
            cells[metric_id] = cell
            coverage[metric_id] += 1
            if cell.get("period") not in (None, ""):
                periods[metric_id].append(str(cell["period"]))
        runtime_countries[code] = {"id":country_id,"name":row.get("name"),"metrics":cells}

        normalized = normalize_axis_profile(axis_profiles.get(code), default_axis_profile)
        runtime_axis_countries[code] = normalized
        for orientation in normalized["orientations"]:
            axis_id = orientation.get("axis")
            if axis_id in axis_memberships and orientation.get("role") in ORDINARY_AXIS_ROLES:
                axis_memberships[axis_id].append(code)

    for axis_id in axis_memberships:
        axis_memberships[axis_id] = sorted(set(axis_memberships[axis_id]))

    metric_meta = {}
    for metric_id, definition in METRICS.items():
        observed_periods = sorted(set(periods[metric_id]))
        metric_meta[metric_id] = {"label":definition["label"],"unit":definition["unit"],"coverage":coverage[metric_id],"country_count":len(countries),"coverage_percent":round((coverage[metric_id]/len(countries))*100,1),"period_min":observed_periods[0] if observed_periods else None,"period_max":observed_periods[-1] if observed_periods else None,"missing_policy":"unknown"}

    return {
        "version":"1.1.0",
        "generated_from":{
            "country_index":"data/countries/index.json",
            "country_records":"data/countries/*.json",
            "institution_memberships":"data/world-institution-memberships.json",
            "axis_profiles":"data/world-axis-profiles.json",
            "system_chains":"data/world-system-chains.json"
        },
        "country_count":len(countries),
        "groups":groups,
        "axis":{"axes":deepcopy(axis_source.get("axes", {})),"memberships":axis_memberships,"countries":runtime_axis_countries,"center_junction":deepcopy(axis_source.get("center_junction", {})),"project_cosmology":deepcopy(axis_source.get("project_cosmology", {}))},
        "reference_figures":deepcopy(axis_source.get("reference_figures", [])),
        "chains":deepcopy(chain_source.get("chains", {})),
        "gateway_model":deepcopy(chain_source.get("gateway_model", {})),
        "metrics":metric_meta,
        "countries":runtime_countries,
    }


def build_runtime_file(path: Path = RUNTIME_OUT) -> dict:
    runtime = build_runtime()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(runtime, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return runtime


if __name__ == "__main__":
    runtime = build_runtime_file()
    print(json.dumps({"country_count":runtime["country_count"],"groups":{key:value["member_count"] for key,value in runtime["groups"].items()},"axis":{key:len(value) for key,value in runtime["axis"]["memberships"].items()},"chains":len(runtime["chains"]),"metrics":{key:value["coverage"] for key,value in runtime["metrics"].items()},"output":str(RUNTIME_OUT.relative_to(ROOT))}, indent=2))
