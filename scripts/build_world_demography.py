#!/usr/bin/env python3
"""Build a compact, sourced population + religion snapshot for the 3D atlas.

Population prefers each canonical country's existing sourced observation and falls
back to the World Bank population indicator only when the local record has no
usable value. Religious composition uses the public Our World in Data Grapher API,
which adapts Pew Research Center's 2025 Global Religious Composition Estimates.

The output is a presentation/runtime artifact. It does not overwrite canonical
country records and it keeps observation year/source metadata explicit.
"""
from __future__ import annotations

import csv
import io
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "countries" / "index.json"
COUNTRIES_DIR = ROOT / "data" / "countries"
OUT = Path(os.environ.get("ATLAS_DEMOGRAPHY_OUT", ROOT / "data" / "world-country-demography.json"))
EXPECTED = 195

OWID_BASE = "https://ourworldindata.org/grapher/religious-composition.csv"
RELIGIONS = {
    "christian": "christians",
    "muslim": "muslims",
    "hindu": "hindus",
    "buddhist": "buddhists",
    "jewish": "jews",
    "other_religions": "other_religions",
    "unaffiliated": "unaffiliated",
}
WORLD_BANK_POP = "SP.POP.TOTL"
USER_AGENT = "ThePotatoOfLife-world-atlas-demography/1.0"


def fetch_text(url: str, timeout: int = 180) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8-sig")


def fetch_json(url: str, timeout: int = 180):
    return json.loads(fetch_text(url, timeout))


def number(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def local_population(country: dict):
    path = COUNTRIES_DIR / f"{country['id']}.json"
    if not path.exists():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    obs = record.get("observations", {}).get("population")
    if not isinstance(obs, dict):
        return None
    value = number(obs.get("value"))
    if value is None:
        return None
    return {
        "value": int(round(value)),
        "year": obs.get("year") or obs.get("reference_period") or record.get("updated"),
        "source": obs.get("source") or "canonical country record",
        "source_url": obs.get("source_url"),
        "confidence": obs.get("confidence") or "sourced-observation",
    }


def world_bank_population() -> dict[str, dict]:
    """Return the newest population observation per ISO3 across all API pages."""
    out: dict[str, dict] = {}
    page = 1
    while True:
        query = urllib.parse.urlencode({"format": "json", "per_page": 1000, "mrv": 5, "page": page})
        url = f"https://api.worldbank.org/v2/country/all/indicator/{WORLD_BANK_POP}?{query}"
        payload = fetch_json(url)
        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
            raise RuntimeError(f"World Bank population payload malformed on page {page}")
        meta = payload[0] if isinstance(payload[0], dict) else {}
        if meta.get("message"):
            raise RuntimeError(f"World Bank rejected population request: {meta['message']}")
        for row in payload[1]:
            code = str(row.get("countryiso3code") or "").upper()
            value = number(row.get("value"))
            year = str(row.get("date") or "")
            if len(code) != 3 or value is None:
                continue
            old = out.get(code)
            if old is None or year > str(old.get("year") or ""):
                out[code] = {
                    "value": int(round(value)),
                    "year": int(year) if year.isdigit() else year,
                    "source": "World Bank",
                    "source_url": f"https://data.worldbank.org/indicator/{WORLD_BANK_POP}?locations={code}",
                    "indicator": WORLD_BANK_POP,
                    "confidence": "international-official",
                }
        pages = int(meta.get("pages") or 1)
        if page >= pages:
            break
        page += 1
    return out


def owid_religion(slug: str) -> dict[str, float]:
    query = urllib.parse.urlencode({
        "v": 1,
        "csvType": "full",
        "useColumnShortNames": "false",
        "indicator": "share",
        "religion": slug,
    })
    text = fetch_text(f"{OWID_BASE}?{query}")
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    value_fields = [f for f in fields if f not in {"Entity", "Code", "Year"}]
    if not value_fields:
        raise RuntimeError(f"OWID religion CSV has no value field for {slug}: {fields}")
    value_field = value_fields[0]
    out = {}
    for row in reader:
        if str(row.get("Year")) != "2020":
            continue
        code = str(row.get("Code") or "").upper()
        value = number(row.get(value_field))
        if len(code) == 3 and value is not None:
            out[code] = round(value, 2)
    if len(out) < 150:
        raise RuntimeError(f"Religion coverage unexpectedly low for {slug}: {len(out)}")
    return out


def main() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    countries = index.get("countries", [])
    if len(countries) != EXPECTED:
        raise RuntimeError(f"Expected {EXPECTED} canonical countries; found {len(countries)}")

    wb = {}
    local = {c["iso3"]: local_population(c) for c in countries}
    missing = [code for code, value in local.items() if not value]
    if missing:
        try:
            wb = world_bank_population()
        except Exception as exc:
            print(f"World Bank fallback unavailable: {exc}")

    religion_by_group = {}
    religion_errors = []
    for key, slug in RELIGIONS.items():
        try:
            religion_by_group[key] = owid_religion(slug)
        except Exception as exc:
            religion_errors.append(f"{key}: {exc}")
            religion_by_group[key] = {}

    rows = {}
    for country in countries:
        code = country["iso3"]
        pop = local.get(code) or wb.get(code)
        composition = {
            key: religion_by_group.get(key, {}).get(code)
            for key in RELIGIONS
            if religion_by_group.get(key, {}).get(code) is not None
        }
        row = {"name": country["name"]}
        if pop:
            row["population"] = pop
        if composition:
            row["religion"] = {
                "year": 2020,
                "unit": "percent of population",
                "composition": composition,
                "source": "Pew Research Center (2025), adapted by Our World in Data",
                "source_url": "https://ourworldindata.org/grapher/religious-composition",
                "original_source_url": "https://www.pewresearch.org/dataset/dataset-of-global-religious-composition-estimates-for-2010-and-2020/",
                "classification_note": "Unaffiliated includes people who identify with no religion, including atheists and agnostics; this global dataset does not split those categories separately.",
            }
        rows[code] = row

    pop_coverage = sum(1 for row in rows.values() if row.get("population", {}).get("value") is not None)
    religion_coverage = sum(1 for row in rows.values() if len(row.get("religion", {}).get("composition", {})) >= 6)
    if pop_coverage < 150:
        raise RuntimeError(f"Population coverage too low: {pop_coverage}")
    if religion_coverage < 150:
        raise RuntimeError(f"Religion coverage too low: {religion_coverage}; errors={religion_errors}")

    payload = {
        "version": "1.0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_type": "world-country-demography-runtime",
        "scope": "Presentation/runtime snapshot; canonical country records remain the source owners for their own sourced observations.",
        "population_coverage": pop_coverage,
        "religion_coverage": religion_coverage,
        "religion_categories": list(RELIGIONS.keys()),
        "religion_reference_year": 2020,
        "religion_method": "Seven mutually exclusive identity categories from Pew Research Center's Global Religious Composition Estimates, surfaced through Our World in Data.",
        "religion_errors": religion_errors,
        "countries": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT),
        "population_coverage": pop_coverage,
        "religion_coverage": religion_coverage,
        "religion_errors": religion_errors,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
