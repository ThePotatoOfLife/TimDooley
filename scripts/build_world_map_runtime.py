#!/usr/bin/env python3
"""Generate the compact World Map browser runtime from canonical repository owners."""
from __future__ import annotations

import json
import math
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTRY_INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRY_DIR = ROOT / "data" / "countries"
MEMBERSHIPS = ROOT / "data" / "world-institution-memberships.json"
AXIS_PROFILES = ROOT / "data" / "world-axis-profiles.json"
SYSTEM_CHAINS = ROOT / "data" / "world-system-chains.json"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"
RUNTIME_OUT = ROOT / "data" / "world-map-data-runtime.json"

METRICS = {
    "gdp_per_capita": {"label":"GDP / person","unit":"current USD / person","observation_aliases":["gdp_per_capita"],"fallback":("economy","gdp_per_capita_usd"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "real_growth": {"label":"Real GDP growth","unit":"percent/year","observation_aliases":["real_growth","real_gdp_growth"],"fallback":("economy","gdp_growth_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "inflation": {"label":"Inflation","unit":"percent/year","observation_aliases":["inflation"],"fallback":("economy","inflation_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "unemployment": {"label":"Unemployment","unit":"percent of labour force","observation_aliases":["unemployment"],"fallback":("economy","unemployment_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "debt_to_gdp": {"label":"Debt / GDP","unit":"percent","observation_aliases":["debt_to_gdp","government_debt_to_gdp"],"fallback":("public_finance","debt_to_gdp"),"fallback_period":("public_finance","year"),"fallback_source":("public_finance","source"),"fallback_source_url":("public_finance","source_url")},
}
INDICATOR_URLS = {
    "NY.GDP.PCAP.CD":"https://data.worldbank.org/indicator/NY.GDP.PCAP.CD",
    "NY.GDP.MKTP.KD.ZG":"https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG",
    "FP.CPI.TOTL.ZG":"https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG",
    "SL.UEM.TOTL.ZS":"https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS",
}
ORDINARY_AXIS_ROLES = {"primary", "secondary", "bridge", "shared"}
DEPENDENCY_TYPES = {"depends-on", "dependency", "strategic-dependency", "import-dependence", "depends_on"}
BUILD_KEY = re.compile(r"(^new_|project|tender|build|expansion|planned|plan_|first_phase|new_offshore)", re.I)


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


def observation_cell(record: dict, definition: dict):
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


def fallback_cell(record: dict, definition: dict):
    raw = nested(record, definition["fallback"])
    if isinstance(raw, dict):
        value = number(raw.get("value")); period = raw.get("year") or raw.get("reference_period") or raw.get("period"); source = raw.get("source"); source_url = raw.get("source_url")
    else:
        value = number(raw); period = nested(record, definition["fallback_period"]); source = nested(record, definition["fallback_source"]); source_url = nested(record, definition["fallback_source_url"])
    if value is None:
        return None
    return {"value":value,"unit":definition["unit"],"period":period,"source":source or "canonical country record","source_url":source_url,"indicator":None,"confidence":None}


def metric_cell(record: dict, definition: dict):
    return observation_cell(record, definition) or fallback_cell(record, definition)


def normalize_axis_profile(profile: dict, default_profile: dict) -> dict:
    source = profile if isinstance(profile, dict) else default_profile
    orientations = []
    for item in source.get("orientations", []) if isinstance(source, dict) else []:
        if isinstance(item, dict):
            orientations.append({key:item.get(key) for key in ("axis","role","basis","confidence","note")})
    return {"status":source.get("status") or ("classified" if orientations else "unresolved"),"orientations":orientations}


def strings(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if isinstance(item, (str, int, float)) and str(item).strip()]


def explicit_capabilities(record: dict) -> list[str]:
    values = []
    values += strings(record.get("capabilities"))
    values += strings((record.get("energy_and_resources") or {}).get("strategic_assets"))
    values += strings((record.get("trade_and_value_chains") or {}).get("strategic_value_chains"))
    values += strings((record.get("technology_research") or {}).get("strategic_capabilities"))
    return list(dict.fromkeys(values))[:16]


def explicit_dependencies(record: dict) -> list[str]:
    values = []
    values += strings(record.get("dependencies"))
    values += strings(record.get("strategic_dependencies"))
    values += strings((record.get("energy_and_resources") or {}).get("import_dependencies"))
    values += strings((record.get("trade_and_value_chains") or {}).get("critical_import_dependencies"))
    for relation in record.get("relationships", []) or []:
        if not isinstance(relation, dict):
            continue
        relation_type = str(relation.get("type") or relation.get("relationship") or "").lower()
        if relation_type in DEPENDENCY_TYPES:
            target = str(relation.get("target") or relation.get("counterparty") or relation.get("note") or "").strip()
            if target:
                values.append(target.replace("-", " "))
    return list(dict.fromkeys(values))[:12]


def explicit_builds(record: dict) -> list[dict]:
    builds = []
    for key, raw in (record.get("observations") or {}).items():
        if not isinstance(raw, dict) or not BUILD_KEY.search(str(key)):
            continue
        if not raw.get("source") or not raw.get("source_url"):
            continue
        builds.append({
            "id":str(key),
            "label":str(key).replace("_", " "),
            "value":raw.get("value"),
            "unit":raw.get("unit"),
            "period":raw.get("reference_period") or raw.get("year") or raw.get("period"),
            "source":raw.get("source"),
            "source_url":raw.get("source_url"),
        })
    return builds[:10]


def evidence_domains(record: dict, capabilities: list[str], dependencies: list[str], builds: list[dict], chain_ids: list[str], gateway_ids: list[str]) -> list[str]:
    domains = []
    if capabilities: domains.append("capability")
    if dependencies: domains.append("dependency")
    if builds: domains.append("projects")
    if chain_ids: domains.append("functional-chains")
    if gateway_ids: domains.append("gateways")
    if record.get("energy_and_resources"): domains.append("energy-resources")
    if record.get("trade_and_value_chains"): domains.append("trade-value-chains")
    if record.get("security_and_external_relations"): domains.append("security-external-relations")
    return list(dict.fromkeys(domains))


def build_runtime() -> dict:
    index = load(COUNTRY_INDEX)
    countries = index.get("countries", [])
    if len(countries) != 195:
        raise RuntimeError(f"canonical country index must contain 195 countries; found {len(countries)}")

    memberships = load(MEMBERSHIPS)
    axis_source = load(AXIS_PROFILES)
    chain_source = load(SYSTEM_CHAINS)
    gateway_source = load(GATEWAYS)
    gateways = deepcopy(gateway_source.get("gateways", {}))

    groups = {}
    for group_id, group in memberships.get("groups", {}).items():
        members = list(group.get("members", []))
        groups[group_id] = {"label":group.get("label",group_id),"members":members,"member_count":len(members),"official_member_count":group.get("official_member_count",len(members)),"non_country_members":list(group.get("non_country_members",[])),"non_canonical_members":list(group.get("non_canonical_members",[])),"suspended_members":list(group.get("suspended_members",[])),"observer_states":list(group.get("observer_states",[])),"as_of":group.get("as_of"),"source":group.get("source"),"source_url":group.get("source_url"),"notes":group.get("notes")}

    chains = deepcopy(chain_source.get("chains", {}))
    runtime_countries = {}
    runtime_axis_countries = {}
    axis_memberships = {axis_id:[] for axis_id in axis_source.get("axes", {})}
    axis_profiles = axis_source.get("profiles", {})
    default_axis_profile = axis_source.get("default_profile", {"status":"unresolved","orientations":[]})
    coverage = {metric_id:0 for metric_id in METRICS}
    periods = {metric_id:[] for metric_id in METRICS}
    system_coverage = {key:0 for key in ("capabilities","dependencies","builds","chains","gateways")}

    for row in countries:
        code = str(row.get("iso3") or "").upper(); country_id = row.get("id")
        if not code or not country_id:
            raise RuntimeError(f"country index row missing identity: {row}")
        record_path = COUNTRY_DIR / f"{country_id}.json"
        if not record_path.is_file():
            raise RuntimeError(f"missing canonical country record: {record_path.relative_to(ROOT)}")
        record = load(record_path)
        cells = {}
        for metric_id, definition in METRICS.items():
            cell = metric_cell(record, definition)
            if not cell: continue
            cells[metric_id] = cell; coverage[metric_id] += 1
            if cell.get("period") not in (None, ""): periods[metric_id].append(str(cell["period"]))

        chain_ids = sorted(chain_id for chain_id, chain in chains.items() if code in (chain.get("members") or []))
        gateway_ids = sorted(gateway_id for gateway_id, gateway in gateways.items() if code in (gateway.get("countries") or []))
        capabilities = explicit_capabilities(record)
        dependencies = explicit_dependencies(record)
        builds = explicit_builds(record)
        for key, value in (("capabilities",capabilities),("dependencies",dependencies),("builds",builds),("chains",chain_ids),("gateways",gateway_ids)):
            if value: system_coverage[key] += 1
        systems = {
            "capabilities":capabilities,
            "dependencies":dependencies,
            "builds":builds,
            "chains":chain_ids,
            "gateways":gateway_ids,
            "resilience":{"evidence_domains":evidence_domains(record,capabilities,dependencies,builds,chain_ids,gateway_ids),"policy":"no aggregate score inferred"},
        }
        runtime_countries[code] = {"id":country_id,"name":row.get("name"),"metrics":cells,"systems":systems}

        normalized = normalize_axis_profile(axis_profiles.get(code), default_axis_profile)
        runtime_axis_countries[code] = normalized
        for orientation in normalized["orientations"]:
            if orientation.get("axis") in axis_memberships and orientation.get("role") in ORDINARY_AXIS_ROLES:
                axis_memberships[orientation["axis"]].append(code)

    for axis_id in axis_memberships:
        axis_memberships[axis_id] = sorted(set(axis_memberships[axis_id]))

    metric_meta = {}
    for metric_id, definition in METRICS.items():
        observed = sorted(set(periods[metric_id]))
        metric_meta[metric_id] = {"label":definition["label"],"unit":definition["unit"],"coverage":coverage[metric_id],"country_count":len(countries),"coverage_percent":round((coverage[metric_id]/len(countries))*100,1),"period_min":observed[0] if observed else None,"period_max":observed[-1] if observed else None,"missing_policy":"unknown"}

    return {
        "version":"1.2.0",
        "generated_from":{"country_index":"data/countries/index.json","country_records":"data/countries/*.json","institution_memberships":"data/world-institution-memberships.json","axis_profiles":"data/world-axis-profiles.json","system_chains":"data/world-system-chains.json","gateways":"data/world-map-gateways.json"},
        "country_count":len(countries),
        "groups":groups,
        "axis":{"axes":deepcopy(axis_source.get("axes",{})),"memberships":axis_memberships,"countries":runtime_axis_countries,"center_junction":deepcopy(axis_source.get("center_junction",{})),"project_cosmology":deepcopy(axis_source.get("project_cosmology",{}))},
        "reference_figures":deepcopy(axis_source.get("reference_figures",[])),
        "chains":chains,
        "gateway_model":deepcopy(chain_source.get("gateway_model",{})),
        "gateways":gateways,
        "system_coverage":system_coverage,
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
    print(json.dumps({"country_count":runtime["country_count"],"groups":{key:value["member_count"] for key,value in runtime["groups"].items()},"axis":{key:len(value) for key,value in runtime["axis"]["memberships"].items()},"chains":len(runtime["chains"]),"gateways":len(runtime["gateways"]),"systems":runtime["system_coverage"],"metrics":{key:value["coverage"] for key,value in runtime["metrics"].items()},"output":str(RUNTIME_OUT.relative_to(ROOT))}, indent=2))
