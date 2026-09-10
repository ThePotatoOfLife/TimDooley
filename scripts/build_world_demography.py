#!/usr/bin/env python3
"""Build a compact, sourced population + religion snapshot for the 3D atlas.

Population prefers each canonical country's existing sourced observation and falls
back to UN World Population Prospects 2024 as surfaced by Our World in Data when
the local record has no usable value. Religious composition uses the public Our
World in Data Grapher API, adapting Pew Research Center's 2025 Global Religious
Composition Estimates.

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

OWID_RELIGION = "https://ourworldindata.org/grapher/religious-composition.csv"
OWID_POPULATION = "https://ourworldindata.org/grapher/population-unwpp.csv?v=1&csvType=full&useColumnShortNames=false"
RELIGIONS = {
    "christian": "christians",
    "muslim": "muslims",
    "hindu": "hindus",
    "buddhist": "buddhists",
    "jewish": "jews",
    "other_religions": "other_religions",
    "unaffiliated": "unaffiliated",
}
USER_AGENT = "ThePotatoOfLife-world-atlas-demography/1.2"


def fetch_text(url: str, timeout: int = 180) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8-sig")


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


def owid_population() -> dict[str, dict]:
    """Return 2023 UN WPP population estimates indexed by ISO3."""
    text = fetch_text(OWID_POPULATION)
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    value_fields = [f for f in fields if f not in {"Entity", "Code", "Year"}]
    if not value_fields:
        raise RuntimeError(f"UN WPP population CSV has no value field: {fields}")
    value_field = value_fields[0]
    out = {}
    for row in reader:
        if str(row.get("Year")) != "2023":
            continue
        code = str(row.get("Code") or "").upper()
        value = number(row.get(value_field))
        if len(code) != 3 or value is None:
            continue
        out[code] = {
            "value": int(round(value)),
            "year": 2023,
            "source": "UN World Population Prospects 2024, processed by Our World in Data",
            "source_url": "https://ourworldindata.org/grapher/population-unwpp",
            "confidence": "international-official-estimate",
        }
    if len(out) < 190:
        raise RuntimeError(f"UN WPP population coverage unexpectedly low: {len(out)}")
    return out


def owid_religion(slug: str) -> dict[str, float]:
    query = urllib.parse.urlencode({
        "v": 1,
        "csvType": "full",
        "useColumnShortNames": "false",
        "indicator": "share",
        "religion": slug,
    })
    text = fetch_text(f"{OWID_RELIGION}?{query}")
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


def derive_unaffiliated_from_any_religion() -> dict[str, float]:
    """Pew's seven categories are exhaustive, so unaffiliated = 100 - any religion."""
    affiliated = owid_religion("any_religion")
    return {code: round(max(0.0, min(100.0, 100.0 - share)), 2) for code, share in affiliated.items()}


def main() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    countries = index.get("countries", [])
    if len(countries) != EXPECTED:
        raise RuntimeError(f"Expected {EXPECTED} canonical countries; found {len(countries)}")

    local = {c["iso3"]: local_population(c) for c in countries}
    fallback = {}
    if any(not value for value in local.values()):
        try:
            fallback = owid_population()
        except Exception as exc:
            print(f"UN WPP population fallback unavailable: {exc}", flush=True)

    religion_by_group = {}
    religion_errors = []
    religion_fallbacks = []
    for key, slug in RELIGIONS.items():
        try:
            religion_by_group[key] = owid_religion(slug)
        except Exception as exc:
            religion_errors.append(f"{key}: {exc}")
            religion_by_group[key] = {}

    if len(religion_by_group.get("unaffiliated", {})) < 150:
        try:
            religion_by_group["unaffiliated"] = derive_unaffiliated_from_any_religion()
            religion_fallbacks.append(
                "unaffiliated derived as 100 minus Pew/OWID share affiliated with any religion after direct unaffiliated endpoint failure"
            )
        except Exception as exc:
            religion_errors.append(f"unaffiliated complement fallback: {exc}")

    rows = {}
    for country in countries:
        code = country["iso3"]
        pop = local.get(code) or fallback.get(code)
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
                "derivation_note": (
                    "Unaffiliated was derived as 100 minus the share affiliated with any religion when the direct unaffiliated endpoint was unavailable."
                    if religion_fallbacks else None
                ),
            }
        rows[code] = row

    pop_coverage = sum(1 for row in rows.values() if row.get("population", {}).get("value") is not None)
    religion_coverage = sum(1 for row in rows.values() if len(row.get("religion", {}).get("composition", {})) == 7)
    if pop_coverage < 150:
        raise RuntimeError(f"Population coverage too low: {pop_coverage}")
    if religion_coverage < 150:
        raise RuntimeError(
            f"Complete seven-category religion coverage too low: {religion_coverage}; errors={religion_errors}"
        )

    payload = {
        "version": "1.2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_type": "world-country-demography-runtime",
        "scope": "Presentation/runtime snapshot; canonical country records remain the source owners for their own sourced observations.",
        "population_coverage": pop_coverage,
        "religion_coverage": religion_coverage,
        "religion_coverage_definition": "countries with all seven mutually exclusive Pew religious-identity categories",
        "religion_categories": list(RELIGIONS.keys()),
        "religion_reference_year": 2020,
        "religion_method": "Seven mutually exclusive identity categories from Pew Research Center's Global Religious Composition Estimates, surfaced through Our World in Data.",
        "population_fallback": "UN World Population Prospects 2024 (2023 estimates), processed by Our World in Data",
        "religion_errors": religion_errors,
        "religion_fallbacks": religion_fallbacks,
        "countries": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT),
        "population_coverage": pop_coverage,
        "religion_coverage": religion_coverage,
        "religion_errors": religion_errors,
        "religion_fallbacks": religion_fallbacks,
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
