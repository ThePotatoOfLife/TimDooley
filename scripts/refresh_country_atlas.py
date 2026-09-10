#!/usr/bin/env python3
"""Refresh canonical country records from authoritative international data.

The website reads data/countries/<country-id>.json directly through the unified
index. External APIs are acquisition inputs only; a failed or incomplete refresh
never replaces a usable country record with an empty snapshot.
"""
from __future__ import annotations

import json
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "countries", "index.json")
OUT = os.path.join(ROOT, "data", "countries")
EXPECTED = 195
REQUEST_TIMEOUT_SECONDS = 60
MAX_ATTEMPTS = 4
RETRY_BASE_SECONDS = 2
TRANSIENT_HTTP_CODES = {408, 425, 429, 500, 502, 503, 504}
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
GROUPS = [
    ["population", "gdp", "gdp_per_capita", "gdp_per_capita_ppp", "real_growth"],
    ["inflation", "unemployment", "labour_force_participation", "life_expectancy", "fertility"],
    ["urbanization", "poverty", "co2_emissions", "internet_penetration"],
]


def _retry_delay(attempt: int, retry_after: str | None = None) -> float:
    if retry_after:
        try:
            return min(30.0, max(0.0, float(retry_after)))
        except ValueError:
            pass
    return min(30.0, RETRY_BASE_SECONDS * (2 ** (attempt - 1)))


def get_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ThePotatoOfLife-country-atlas/3.1",
            "Accept": "application/json",
        },
    )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code not in TRANSIENT_HTTP_CODES or attempt >= MAX_ATTEMPTS:
                raise
            delay = _retry_delay(attempt, exc.headers.get("Retry-After") if exc.headers else None)
            print(
                f"Transient HTTP {exc.code} from {url}; retrying in {delay:g}s "
                f"({attempt}/{MAX_ATTEMPTS})",
                file=sys.stderr,
            )
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            if attempt >= MAX_ATTEMPTS:
                raise RuntimeError(
                    f"Failed to retrieve {url} after {MAX_ATTEMPTS} attempts: {exc}"
                ) from exc
            delay = _retry_delay(attempt)
            print(
                f"Transient network error from {url}: {exc}; retrying in {delay:g}s "
                f"({attempt}/{MAX_ATTEMPTS})",
                file=sys.stderr,
            )
        time.sleep(delay)

    raise RuntimeError(f"Failed to retrieve {url}")


def world_bank(fields):
    result = {field: {} for field in fields}
    for field in fields:
        indicator = INDICATORS[field]
        page = 1
        while True:
            query = urllib.parse.urlencode(
                {"format": "json", "per_page": 1000, "mrv": 5, "page": page}
            )
            payload = get_json(
                "https://api.worldbank.org/v2/country/all/indicator/"
                f"{urllib.parse.quote(indicator, safe='')}?{query}"
            )
            if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
                raise RuntimeError(f"World Bank returned malformed payload for {indicator}")
            if isinstance(payload[0], dict) and payload[0].get("message"):
                raise RuntimeError(f"World Bank rejected {indicator}: {payload[0]['message']}")
            for row in payload[1]:
                iso = str(row.get("countryiso3code") or "").upper()
                value = row.get("value")
                year = str(row.get("date") or "")
                if not iso or value is None:
                    continue
                old = result[field].get(iso)
                if old is None or year > str(old.get("year") or ""):
                    result[field][iso] = {
                        "value": value,
                        "year": int(year) if year.isdigit() else year,
                        "source": "world-bank",
                        "indicator": indicator,
                    }
            pages = int(payload[0].get("pages") or 1)
            if page >= pages:
                break
            page += 1
    return result


def load(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def main():
    index = load(INDEX)
    countries = index.get("countries", [])
    if len(countries) != EXPECTED:
        raise RuntimeError(
            f"Canonical country index must contain {EXPECTED} records; found {len(countries)}"
        )
    ids = [country.get("id") for country in countries]
    iso = [str(country.get("iso3") or "").upper() for country in countries]
    if len(set(ids)) != EXPECTED or len(set(iso)) != EXPECTED or "" in iso:
        raise RuntimeError("Canonical country index has duplicate or missing identities")

    by_field = {field: {} for field in INDICATORS}
    requests = 0
    for group in GROUPS:
        result = world_bank(group)
        for field, values in result.items():
            by_field[field].update(values)
        requests += len(group)

    coverage = {field: len(by_field[field]) for field in INDICATORS}
    minimum = max(150, int(EXPECTED * 0.75))
    if coverage["population"] < minimum or coverage["gdp"] < minimum:
        raise RuntimeError(
            "Refusing incomplete refresh: "
            f"population={coverage['population']}, gdp={coverage['gdp']}, "
            f"required_each>={minimum}"
        )

    now = datetime.now(timezone.utc).isoformat()
    observations_written = 0
    countries_written = 0
    for country in countries:
        path = os.path.join(OUT, f"{country['id']}.json")
        if not os.path.exists(path):
            raise RuntimeError(f"Missing canonical country record: {path}")
        record = load(path)
        record.setdefault("record_type", "country")
        record.setdefault("identity", {})
        record["identity"].update(
            {
                "id": country["id"],
                "name": country["name"],
                "iso2": country["iso2"],
                "iso3": country["iso3"],
            }
        )
        record.setdefault("observations", {})
        record.setdefault("history", [])
        record.setdefault("coverage", {})
        record.setdefault("provenance", {})
        for field in INDICATORS:
            value = by_field[field].get(str(country["iso3"]).upper())
            if not value:
                continue
            value = dict(value)
            value["retrieved_at"] = now
            value["confidence"] = "international-official"
            old = record["observations"].get(field)
            if isinstance(old, dict) and old.get("value") != value.get("value"):
                record["history"].append(
                    {
                        "field": field,
                        "previous": old,
                        "replaced_at": now,
                        "reason": "new source observation",
                    }
                )
            record["observations"][field] = value
            observations_written += 1
        record["coverage"]["observations"] = len(record["observations"])
        record["coverage"]["sources"] = max(
            record["coverage"].get("sources", 0), 1 if record["observations"] else 0
        )
        record["provenance"]["last_refresh"] = now
        record["provenance"]["source_priority"] = "international-official"
        record["provenance"]["historical_observations_preserved"] = True
        with open(path, "w", encoding="utf-8") as file:
            json.dump(record, file, ensure_ascii=False, indent=2)
            file.write("\n")
        countries_written += 1

    print(
        json.dumps(
            {
                "updated_at": now,
                "countries_written": countries_written,
                "observations_written": observations_written,
                "bulk_indicator_requests": requests,
                "coverage": coverage,
                "source": "world-bank",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
