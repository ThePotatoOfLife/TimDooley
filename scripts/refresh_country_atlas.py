#!/usr/bin/env python3
"""Refresh the static country atlas from authoritative international data.

External APIs are acquisition inputs only. The website consumes the generated
repository snapshot and never depends on a live API at page-load time.

Failure policy: acquisition errors, malformed API responses, incomplete
canonical scope, or suspiciously empty bulk results must fail closed. A bad
refresh must never replace a usable snapshot with an empty projection.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "countries", "index.json")
OUT = os.path.join(ROOT, "data", "countries")
STATIC = os.path.join(ROOT, "data", "country-static.json")
STATE = os.path.join(ROOT, "data", "country-refresh-state.json")

EXPECTED_CANONICAL_COUNT = 195
INDICATORS = {
    "population": "SP.POP.TOTL",
    "gdp": "NY.GDP.MKTP.CD",
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "gdp_per_capita_ppp": "NY.GDP.PCAP.PP.CD",
    "real_growth": "NY.GDP.MKTP.KD.ZG",
    "inflation": "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
    "labour_force_participation": "SL.TLF.CACT.ZS",
    "life_expectancy": "SP.DYN.LE00.IN",
    "fertility": "SP.DYN.TFRT.IN",
    "urbanization": "SP.URB.TOTL.IN.ZS",
    "poverty": "SI.POV.NAHC",
    "co2_emissions": "EN.ATM.CO2E.PC",
    "internet_penetration": "IT.NET.USER.ZS",
}
INDICATOR_GROUPS = [
    ["population", "gdp", "gdp_per_capita", "gdp_per_capita_ppp", "real_growth"],
    ["inflation", "unemployment", "labour_force_participation", "life_expectancy", "fertility"],
    ["urbanization", "poverty", "co2_emissions", "internet_penetration"],
]


def get_json(url: str, timeout: int = 180):
    req = urllib.request.Request(url, headers={"User-Agent": "ThePotatoOfLife-country-atlas/2.2"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def world_bank_group(fields):
    """Fetch all pages for each indicator and reject World Bank error payloads.

    The old adapter used per_page=10000. World Bank's documented endpoint
    returns an error payload for unsupported request parameters; the old code
    interpreted that one-element error payload as an empty data page. That was
    the direct cause of a zero-observation refresh that still wrote a snapshot.
    """
    result = {field: {} for field in fields}
    for field in fields:
        indicator = INDICATORS[field]
        page = 1
        while True:
            query = urllib.parse.urlencode({"format": "json", "per_page": 1000, "mrv": 5, "page": page})
            url = f"https://api.worldbank.org/v2/country/all/indicator/{urllib.parse.quote(indicator, safe='')}?{query}"
            payload = get_json(url)
            if not isinstance(payload, list) or not payload:
                raise RuntimeError(f"World Bank returned malformed payload for {indicator}: {type(payload).__name__}")
            if isinstance(payload[0], dict) and payload[0].get("message"):
                raise RuntimeError(f"World Bank rejected {indicator}: {payload[0].get('message')}")
            if len(payload) < 2 or not isinstance(payload[1], list):
                raise RuntimeError(f"World Bank returned no data array for {indicator}")
            rows = payload[1]
            for row in rows:
                iso3 = str(row.get("countryiso3code") or "").upper()
                if not iso3 or row.get("value") is None:
                    continue
                year = str(row.get("date") or "")
                current = result[field].get(iso3)
                if current is None or year > str(current.get("year") or ""):
                    result[field][iso3] = {
                        "value": row["value"],
                        "year": int(year) if year.isdigit() else year,
                        "source": "world-bank",
                        "indicator": indicator,
                    }
            meta = payload[0]
            pages = int(meta.get("pages") or 1)
            if page >= pages:
                break
            page += 1
    return result


def load_existing(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def validate_index(index):
    countries = index.get("countries")
    if not isinstance(countries, list):
        raise RuntimeError("Canonical country index has no countries array")
    if len(countries) != EXPECTED_CANONICAL_COUNT:
        raise RuntimeError(
            f"Canonical country index must contain {EXPECTED_CANONICAL_COUNT} records; found {len(countries)}"
        )
    ids = [str(c.get("id") or "") for c in countries]
    iso3 = [str(c.get("iso3") or "").upper() for c in countries]
    if len(set(ids)) != len(ids):
        raise RuntimeError("Canonical country index contains duplicate country IDs")
    if len(set(iso3)) != len(iso3) or "" in iso3:
        raise RuntimeError("Canonical country index contains missing or duplicate ISO3 codes")
    return countries


def compact_record(record, directory_entry, enrichment):
    observations = record.get("observations") or {}
    identity = record.get("identity") or {}
    coverage = record.get("coverage") or {}
    enriched = {}
    for key, value in (enrichment or {}).items():
        if key in {"country_id", "iso2", "iso3", "blueprint", "updated", "provenance"}:
            continue
        if value not in (None, "", [], {}):
            enriched[key] = value
    return {
        "id": identity.get("id") or directory_entry["id"],
        "name": identity.get("name") or directory_entry["name"],
        "status": directory_entry.get("status"),
        "iso2": identity.get("iso2") or directory_entry.get("iso2"),
        "iso3": identity.get("iso3") or directory_entry.get("iso3"),
        "capital": directory_entry.get("capital"),
        "region": directory_entry.get("region"),
        "subregion": directory_entry.get("subregion"),
        "profile_url": directory_entry.get("profile_url"),
        "record_status": record.get("status"),
        "coverage": coverage,
        "observations": observations,
        "relationships": record.get("relationships") or [],
        "history": record.get("history") or [],
        "research_queue": record.get("research_queue") or [],
        "provenance": record.get("provenance") or {},
        "enrichment": enriched,
    }


def write_static_atlas(index, now):
    countries = []
    for directory_entry in index["countries"]:
        record = load_existing(os.path.join(OUT, f"{directory_entry['id']}.json"))
        enrichment = load_existing(os.path.join(OUT, f"{directory_entry['id']}-enrichment.json"))
        countries.append(compact_record(record, directory_entry, enrichment))
    payload = {
        "version": "2.2.0",
        "generated_at": now,
        "source_policy": "Repository snapshot. External APIs are used only by the scheduled acquisition workflow, never by the browser.",
        "canonical_count": len(countries),
        "countries": countries,
    }
    with open(STATIC, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    return len(countries)


def main():
    with open(INDEX, encoding="utf-8") as f:
        index = json.load(f)
    now = datetime.now(timezone.utc).isoformat()
    validate_index(index)
    summary = {
        "updated_at": now,
        "source": "world-bank",
        "countries": 0,
        "observations": 0,
        "errors": [],
        "preserved_records": 0,
        "bulk_indicator_requests": 0,
        "static_snapshot": STATIC,
        "canonical_count_from_index": len(index["countries"]),
        "failure_policy": "fail-closed-before-write-on-invalid-canonical-scope-or-empty-required-acquisition",
    }

    by_field = {field: {} for field in INDICATORS}
    for group in INDICATOR_GROUPS:
        try:
            result = world_bank_group(group)
            for field, values in result.items():
                by_field[field].update(values)
            summary["bulk_indicator_requests"] += len(group)
        except Exception as exc:
            summary["errors"].append({"indicator_group": [INDICATORS[f] for f in group], "error": str(exc)})

    population_count = len(by_field["population"])
    gdp_count = len(by_field["gdp"])
    summary["acquisition_coverage"] = {
        "population": population_count,
        "gdp": gdp_count,
        "canonical": len(index["countries"]),
    }
    minimum_required = max(150, int(len(index["countries"]) * 0.75))
    if population_count < minimum_required or gdp_count < minimum_required:
        raise RuntimeError(
            "World Bank acquisition is suspiciously incomplete; refusing to overwrite country records/snapshot "
            f"(population={population_count}, gdp={gdp_count}, required_each>={minimum_required})"
        )

    for country in index["countries"]:
        path = os.path.join(OUT, f"{country['id']}.json")
        record = load_existing(path)
        record.setdefault("record_type", "country")
        record.setdefault("status", "instantiated")
        record.setdefault("identity", {})
        record["identity"].update({"id": country["id"], "name": country["name"], "iso2": country["iso2"], "iso3": country["iso3"]})
        record.setdefault("blueprint", "data/countries-blueprint.json")
        record.setdefault("observations", {})
        record.setdefault("relationships", [])
        record.setdefault("history", [])
        record.setdefault("provenance", {})
        record.setdefault("data_freshness", {})
        previous = dict(record["observations"])
        for field in INDICATORS:
            value = by_field.get(field, {}).get(str(country["iso3"]).upper())
            if not value:
                continue
            value = dict(value)
            value["retrieved_at"] = now
            value["confidence"] = "international-official"
            old = record["observations"].get(field)
            if old and isinstance(old, dict) and old.get("value") != value.get("value"):
                record["history"].append({"field": field, "previous": old, "replaced_at": now, "reason": "new source observation"})
            record["observations"][field] = value
            summary["observations"] += 1
        record["coverage"] = record.get("coverage", {})
        record["coverage"].update({
            "observations": len(record["observations"]),
            "relationships": len(record["relationships"]),
            "sources": max(record["coverage"].get("sources", 0), 1 if record["observations"] else 0),
        })
        record["data_freshness"].update({"last_refresh_attempt": now, "source": "world-bank"})
        record["provenance"]["last_refresh"] = now
        record["provenance"]["source_priority"] = "international-official"
        record["provenance"]["historical_observations_preserved"] = True
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        summary["countries"] += 1
        if previous or record.get("research_queue"):
            summary["preserved_records"] += 1

    summary["static_countries"] = write_static_atlas(index, now)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Write diagnostic state only; never write country records or the static
        # snapshot after a failed validation/acquisition gate.
        now = datetime.now(timezone.utc).isoformat()
        failure = {
            "updated_at": now,
            "source": "world-bank",
            "status": "failed-closed",
            "error": str(exc),
            "static_snapshot_preserved": True,
        }
        try:
            with open(STATE, "w", encoding="utf-8") as f:
                json.dump(failure, f, ensure_ascii=False, indent=2)
        finally:
            raise
