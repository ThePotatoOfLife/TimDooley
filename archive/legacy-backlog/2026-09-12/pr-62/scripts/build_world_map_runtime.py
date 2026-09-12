#!/usr/bin/env python3
"""Generate the compact World Map browser runtime from canonical repository owners."""
from __future__ import annotations

import json
import math
import re
from copy import deepcopy
from pathlib import Path

from world_map_impact import build_impact_plane, dependency_labels
from world_map_scalars import resolve_area, resolve_population

ROOT = Path(__file__).resolve().parents[1]
COUNTRY_INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRY_DIR = ROOT / "data" / "countries"
MEMBERSHIPS = ROOT / "data" / "world-institution-memberships.json"
AXIS_PROFILES = ROOT / "data" / "world-axis-profiles.json"
SYSTEM_CHAINS = ROOT / "data" / "world-system-chains.json"
GATEWAYS = ROOT / "data" / "world-map-gateways.json"
ENTITIES = ROOT / "data" / "world-map-entities.json"
AFRICA_SYSTEMS = ROOT / "data" / "world-africa-regional-systems.json"
DEMOGRAPHY = ROOT / "data" / "world-country-demography.json"
COUNTRY_FACTS = ROOT / "data" / "world-country-facts.json"
RUNTIME_OUT = ROOT / "data" / "world-map-data-runtime.json"

METRICS = {
    "gdp_per_capita": {"label":"GDP / person","unit":"current USD / person","observation_aliases":["gdp_per_capita"],"fallback":("economy","gdp_per_capita_usd"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "gdp_per_capita_ppp": {"label":"GDP / person · PPP","unit":"current international $ / person","observation_aliases":["gdp_per_capita_ppp"]},
    "real_growth": {"label":"Real GDP growth","unit":"percent/year","observation_aliases":["real_growth","real_gdp_growth"],"fallback":("economy","gdp_growth_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "inflation": {"label":"Inflation","unit":"percent/year","observation_aliases":["inflation"],"fallback":("economy","inflation_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "unemployment": {"label":"Unemployment","unit":"percent of labour force","observation_aliases":["unemployment"],"fallback":("economy","unemployment_percent"),"fallback_period":("economy","gdp_year"),"fallback_source":("economy","source"),"fallback_source_url":("economy","source_url")},
    "labour_force_participation": {"label":"Labour-force participation","unit":"percent of population age 15+","observation_aliases":["labour_force_participation"]},
    "life_expectancy": {"label":"Life expectancy","unit":"years","observation_aliases":["life_expectancy"]},
    "fertility": {"label":"Fertility","unit":"births per woman","observation_aliases":["fertility"]},
    "urbanization": {"label":"Urban population","unit":"percent of population","observation_aliases":["urbanization"]},
    "internet_use": {"label":"Internet use","unit":"percent of population","observation_aliases":["internet_penetration","internet_use"]},
    "co2_per_capita": {"label":"CO₂ / person","unit":"metric tons per person","observation_aliases":["co2_emissions","co2_per_capita"]},
    "debt_to_gdp": {"label":"Debt / GDP","unit":"percent","observation_aliases":["debt_to_gdp","government_debt_to_gdp"],"fallback":("public_finance","debt_to_gdp"),"fallback_period":("public_finance","year"),"fallback_source":("public_finance","source"),"fallback_source_url":("public_finance","source_url")},
}
INDICATOR_URLS = {
    "NY.GDP.PCAP.CD":"https://data.worldbank.org/indicator/NY.GDP.PCAP.CD",
    "NY.GDP.PCAP.PP.CD":"https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD",
    "NY.GDP.MKTP.KD.ZG":"https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG",
    "FP.CPI.TOTL.ZG":"https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG",
    "SL.UEM.TOTL.ZS":"https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS",
    "SL.TLF.CACT.ZS":"https://data.worldbank.org/indicator/SL.TLF.CACT.ZS",
    "SP.DYN.LE00.IN":"https://data.worldbank.org/indicator/SP.DYN.LE00.IN",
    "SP.DYN.TFRT.IN":"https://data.worldbank.org/indicator/SP.DYN.TFRT.IN",
    "SP.URB.TOTL.IN.ZS":"https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS",
    "IT.NET.USER.ZS":"https://data.worldbank.org/indicator/IT.NET.USER.ZS",
    "EN.ATM.CO2E.PC":"https://data.worldbank.org/indicator/EN.ATM.CO2E.PC",
}
ORDINARY_AXIS_ROLES = {"primary", "secondary", "bridge", "shared"}
BUILD_KEY = re.compile(r"(^new_|project|tender|build|expansion|planned|plan_|first_phase|new_offshore)", re.I)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional(path: Path) -> dict:
    try:
        return load(path) if path.is_file() else {}
    except Exception:
        return {}


def nested(record: dict, path: tuple[str, ...] | None):
    if not path:
        return None
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
        return {
            "value": value,
            "unit": definition["unit"],
            "period": raw.get("year") or raw.get("reference_period") or raw.get("period"),
            "source": raw.get("source") or "canonical country observation",
            "source_url": raw.get("source_url") or INDICATOR_URLS.get(indicator),
            "indicator": indicator,
            "confidence": raw.get("confidence"),
        }
    return None


def fallback_cell(record: dict, definition: dict):
    if not definition.get("fallback"):
        return None
    raw = nested(record, definition.get("fallback"))
    if isinstance(raw, dict):
        value = number(raw.get("value"))
        period = raw.get("year") or raw.get("reference_period") or raw.get("period")
        source = raw.get("source")
        source_url = raw.get("source_url")
    else:
        value = number(raw)
        period = nested(record, definition.get("fallback_period"))
        source = nested(record, definition.get("fallback_source"))
        source_url = nested(record, definition.get("fallback_source_url"))
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
            orientations.append({key:item.get(key) for key in ("axis","role","basis","confidence","note","source_url") if item.get(key) is not None})
    return {"status":source.get("status") or ("classified" if orientations else "unresolved"),"orientations":orientations}


def merge_axis_profile(base: dict, overlays: list[dict]) -> dict:
    result = deepcopy(base)
    orientations = list(result.get("orientations") or [])
    seen = {(item.get("axis"), item.get("role"), item.get("basis")) for item in orientations}
    for item in overlays or []:
        if not isinstance(item, dict):
            continue
        normalized = {key:item.get(key) for key in ("axis","role","basis","confidence","note","source_url") if item.get(key) is not None}
        key = (normalized.get("axis"), normalized.get("role"), normalized.get("basis"))
        if key not in seen:
            orientations.append(normalized)
            seen.add(key)
    result["orientations"] = orientations
    result["status"] = "classified" if orientations else result.get("status", "unresolved")
    return result


def strings(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if isinstance(item, (str, int, float)) and str(item).strip()]


def explicit_capabilities(record: dict) -> list[str]:
    values = strings(record.get("capabilities")) + strings((record.get("energy_and_resources") or {}).get("strategic_assets")) + strings((record.get("trade_and_value_chains") or {}).get("strategic_value_chains")) + strings((record.get("technology_research") or {}).get("strategic_capabilities"))
    return list(dict.fromkeys(values))[:16]


def explicit_builds(record: dict) -> list[dict]:
    builds = []
    for key, raw in (record.get("observations") or {}).items():
        if not isinstance(raw, dict) or not BUILD_KEY.search(str(key)) or not raw.get("source") or not raw.get("source_url"):
            continue
        builds.append({"id":str(key),"label":str(key).replace("_", " "),"value":raw.get("value"),"unit":raw.get("unit"),"period":raw.get("reference_period") or raw.get("year") or raw.get("period"),"source":raw.get("source"),"source_url":raw.get("source_url")})
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


def africa_for_country(code: str, africa_source: dict) -> list[dict]:
    rows = []
    for system_id, system in (africa_source.get("systems") or {}).items():
        if code in (system.get("members") or []):
            rows.append({"id":system_id,"label":system.get("label",system_id),"status":"current","kind":system.get("kind"),"source":system.get("source"),"source_url":system.get("source_url")})
        for former in system.get("former_or_transition_members", []) or []:
            if isinstance(former, dict) and former.get("code") == code:
                rows.append({"id":system_id,"label":system.get("label",system_id),"status":former.get("status"),"effective_date":former.get("effective_date"),"kind":system.get("kind"),"source":system.get("source"),"source_url":former.get("source_url") or system.get("source_url")})
    return rows


def build_runtime() -> dict:
    index = load(COUNTRY_INDEX)
    countries = index.get("countries", [])
    if len(countries) != 195:
        raise RuntimeError(f"canonical country index must contain 195 countries; found {len(countries)}")
    memberships = load(MEMBERSHIPS)
    axis_source = load(AXIS_PROFILES)
    chain_source = load(SYSTEM_CHAINS)
    gateway_source = load(GATEWAYS)
    entity_source = load(ENTITIES)
    africa_source = load(AFRICA_SYSTEMS)
    demography = load_optional(DEMOGRAPHY).get("countries", {})
    facts = load_optional(COUNTRY_FACTS).get("countries", {})
    gateways = deepcopy(gateway_source.get("gateways", {}))
    chains = deepcopy(chain_source.get("chains", {}))
    country_records = {}

    groups = {}
    for group_id, group in memberships.get("groups", {}).items():
        members = list(group.get("members", []))
        groups[group_id] = {"label":group.get("label",group_id),"members":members,"member_count":len(members),"official_member_count":group.get("official_member_count",len(members)),"non_country_members":list(group.get("non_country_members",[])),"non_canonical_members":list(group.get("non_canonical_members",[])),"suspended_members":list(group.get("suspended_members",[])),"observer_states":list(group.get("observer_states",[])),"partners":deepcopy(group.get("partners",[])),"as_of":group.get("as_of"),"source":group.get("source"),"source_url":group.get("source_url"),"notes":group.get("notes")}

    runtime_countries = {}
    runtime_axis_countries = {}
    runtime_entities = {}
    scalar_entities = {}
    axis_memberships = {axis_id:[] for axis_id in axis_source.get("axes", {})}
    axis_profiles = axis_source.get("profiles", {})
    default_axis_profile = axis_source.get("default_profile", {"status":"unresolved","orientations":[]})
    coverage = {metric_id:0 for metric_id in METRICS}
    periods = {metric_id:[] for metric_id in METRICS}
    system_coverage = {key:0 for key in ("capabilities","dependencies","builds","chains","gateways")}

    for row in countries:
        code = str(row.get("iso3") or "").upper()
        country_id = row.get("id")
        if not code or not country_id:
            raise RuntimeError(f"country index row missing identity: {row}")
        record_path = COUNTRY_DIR / f"{country_id}.json"
        if not record_path.is_file():
            raise RuntimeError(f"missing canonical country record: {record_path.relative_to(ROOT)}")
        record = load(record_path)
        country_records[code] = record
        cells = {}
        for metric_id, definition in METRICS.items():
            cell = metric_cell(record, definition)
            if not cell:
                continue
            cells[metric_id] = cell
            coverage[metric_id] += 1
            if cell.get("period") not in (None, ""):
                periods[metric_id].append(str(cell["period"]))

        pop_fallback = demography.get(code, {}).get("population") if isinstance(demography.get(code), dict) else None
        area_fact = facts.get(code, {}) if isinstance(facts.get(code), dict) else {}
        area_fallback = None
        if area_fact.get("area_km2") is not None:
            area_fallback = {"value":area_fact.get("area_km2"),"unit":"km²","definition":area_fact.get("area_definition") or "area","source":area_fact.get("field_sources",{}).get("area_km2") or area_fact.get("fallback_source") or "country facts runtime"}
        scalar_entities[code] = {k:v for k,v in {
            "population": resolve_population(record, pop_fallback),
            "area": resolve_area(record, area_fallback),
        }.items() if v is not None}

        chain_ids = sorted(chain_id for chain_id, chain in chains.items() if code in (chain.get("members") or []))
        gateway_ids = sorted(gateway_id for gateway_id, gateway in gateways.items() if code in (gateway.get("countries") or []))
        capabilities = explicit_capabilities(record)
        dependencies = dependency_labels(record)
        builds = explicit_builds(record)
        for key, value in (("capabilities",capabilities),("dependencies",dependencies),("builds",builds),("chains",chain_ids),("gateways",gateway_ids)):
            if value:
                system_coverage[key] += 1
        regional = africa_for_country(code, africa_source)
        systems = {"capabilities":capabilities,"dependencies":dependencies,"builds":builds,"chains":chain_ids,"gateways":gateway_ids,"regional":regional,"resilience":{"evidence_domains":evidence_domains(record,capabilities,dependencies,builds,chain_ids,gateway_ids),"policy":"no aggregate score inferred"}}
        runtime_countries[code] = {"id":country_id,"name":row.get("name"),"entity_type":"sovereign-country","canonical_country":True,"metrics":cells,"systems":systems}
        runtime_entities[code] = {"code":code,"id":country_id,"name":row.get("name"),"entity_type":"sovereign-country","canonical_country":True,"systems":{"chains":chain_ids,"regional":regional}}
        normalized = merge_axis_profile(normalize_axis_profile(axis_profiles.get(code), default_axis_profile), (africa_source.get("axis_overlays") or {}).get(code, []))
        runtime_axis_countries[code] = normalized
        for orientation in normalized["orientations"]:
            if orientation.get("axis") in axis_memberships and orientation.get("role") in ORDINARY_AXIS_ROLES:
                axis_memberships[orientation["axis"]].append(code)

    territories = {}
    for code, entity in (entity_source.get("entities") or {}).items():
        code = str(code).upper()
        profile = normalize_axis_profile(entity.get("axis_profile") or axis_profiles.get(code), default_axis_profile)
        chain_ids = sorted(chain_id for chain_id, chain in chains.items() if code in (chain.get("members") or []))
        projected = {"code":code,"id":entity.get("id"),"name":entity.get("name"),"entity_type":entity.get("entity_type"),"canonical_country":False,"sovereignty_context":entity.get("sovereignty_context"),"constitutional_parent":entity.get("constitutional_parent"),"capital":entity.get("capital"),"render_status":entity.get("render_status"),"population":deepcopy(entity.get("population")),"area":deepcopy(entity.get("area")),"label_anchor":deepcopy(entity.get("label_anchor")),"relationships":deepcopy(entity.get("relationships",[])),"axis_profile":profile,"systems":{"chains":chain_ids,"regional":[]}}
        territories[code] = projected
        runtime_entities[code] = projected
        runtime_axis_countries[code] = profile
        scalar_entities[code] = {k:v for k,v in {
            "population": resolve_population(entity),
            "area": resolve_area(entity),
        }.items() if v is not None}
        for orientation in profile["orientations"]:
            if orientation.get("axis") in axis_memberships and orientation.get("role") in ORDINARY_AXIS_ROLES:
                axis_memberships[orientation["axis"]].append(code)

    for axis_id in axis_memberships:
        axis_memberships[axis_id] = sorted(set(axis_memberships[axis_id]))

    metric_meta = {}
    for metric_id, definition in METRICS.items():
        observed = sorted(set(periods[metric_id]))
        metric_meta[metric_id] = {"label":definition["label"],"unit":definition["unit"],"coverage":coverage[metric_id],"country_count":len(countries),"coverage_percent":round((coverage[metric_id]/len(countries))*100,1),"period_min":observed[0] if observed else None,"period_max":observed[-1] if observed else None,"missing_policy":"unknown"}

    impact = build_impact_plane(countries, country_records, entity_source.get("entities", {}), gateways, chains)
    return {
        "version":"1.6.0",
        "generated_from":{"country_index":"data/countries/index.json","country_records":"data/countries/*.json","institution_memberships":"data/world-institution-memberships.json","axis_profiles":"data/world-axis-profiles.json","system_chains":"data/world-system-chains.json","gateways":"data/world-map-gateways.json","entities":"data/world-map-entities.json","africa_regional_systems":"data/world-africa-regional-systems.json","demography":"data/world-country-demography.json","country_facts":"data/world-country-facts.json","impact":"scripts/world_map_impact.py","scalars":"scripts/world_map_scalars.py"},
        "country_count":len(countries),
        "entities":{"country_count":len(countries),"territories":territories,"by_id":runtime_entities,"renderable_entity_count":len(countries)+sum(1 for entity in territories.values() if entity.get("render_status")=="current")},
        "scalars":{"missing_policy":"unknown-not-zero","by_entity":scalar_entities},
        "groups":groups,
        "africa":{"systems":deepcopy(africa_source.get("systems",{})),"for_country":{code:africa_for_country(code,africa_source) for code in runtime_countries},"axis_overlays":deepcopy(africa_source.get("axis_overlays",{})),"axis_rule":africa_source.get("axis_rule")},
        "axis":{"axes":deepcopy(axis_source.get("axes",{})),"memberships":axis_memberships,"countries":runtime_axis_countries,"center_junction":deepcopy(axis_source.get("center_junction",{})),"project_cosmology":deepcopy(axis_source.get("project_cosmology",{}))},
        "reference_figures":deepcopy(axis_source.get("reference_figures",[])),
        "chains":chains,
        "gateway_model":deepcopy(chain_source.get("gateway_model",{})),
        "gateways":gateways,
        "impact":impact,
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
    print(json.dumps({"country_count":runtime["country_count"],"entities":runtime["entities"]["renderable_entity_count"],"groups":{key:value["member_count"] for key,value in runtime["groups"].items()},"axis":{key:len(value) for key,value in runtime["axis"]["memberships"].items()},"chains":len(runtime["chains"]),"gateways":len(runtime["gateways"]),"impact_nodes":len(runtime["impact"]["nodes"]),"impact_edges":len(runtime["impact"]["edges"]),"systems":runtime["system_coverage"],"metrics":{key:value["coverage"] for key,value in runtime["metrics"].items()},"output":str(RUNTIME_OUT.relative_to(ROOT))}, indent=2))
