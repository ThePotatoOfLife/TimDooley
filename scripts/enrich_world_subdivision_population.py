#!/usr/bin/env python3
"""Enrich World Map subdivision snapshots with sourced population observations.

Geometry ownership stays in build_world_subdivisions.py. This module attaches
statistical observations to existing same-origin subdivision snapshots without
changing geometry or inventing missing values.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBDIVISION_DIR = Path(os.environ.get("ATLAS_SUBDIVISIONS_OUT_DIR", ROOT / "data" / "world-subdivisions"))
STATBANK_TABLE = "BEFOLK3"
STATBANK_TABLEINFO_URL = "https://api.statbank.dk/v1/tableinfo"
STATBANK_DATA_URL = "https://api.statbank.dk/v1/data"
STATBANK_SOURCE_URL = "https://www.statbank.dk/BEFOLK3"
SOURCE_NAME = "Statistics Denmark, StatBank table BEFOLK3"
USER_AGENT = "ThePotatoOfLife-world-atlas-subdivision-population/1.0"
CURRENT_PERIOD = "2026"
EXPECTED_DANISH_REGIONS = {
    "Region Hovedstaden",
    "Region Sjælland",
    "Region Syddanmark",
    "Region Midtjylland",
    "Region Nordjylland",
}


def post_json(url: str, payload: dict, *, timeout: int = 120) -> bytes:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def normalize_label(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _variable(tableinfo: dict, *needles: str) -> dict:
    variables = tableinfo.get("variables") or []
    for variable in variables:
        haystack = " ".join(
            [str(variable.get("id") or ""), str(variable.get("text") or "")]
        ).casefold()
        if any(needle.casefold() in haystack for needle in needles):
            return variable
    raise RuntimeError(f"StatBank table metadata is missing variable matching {needles}")


def _value_id(variable: dict, predicate) -> str:
    for value in variable.get("values") or []:
        if predicate(str(value.get("text") or ""), str(value.get("id") or "")):
            return str(value.get("id"))
    raise RuntimeError(f"StatBank variable {variable.get('id')} has no matching value")


def statbank_selection(tableinfo: dict, *, period: str = CURRENT_PERIOD) -> dict:
    region = _variable(tableinfo, "region", "område")
    sex = _variable(tableinfo, "sex", "køn")
    age = _variable(tableinfo, "age", "alder")
    time = _variable(tableinfo, "year", "time", "tid")

    region_values = []
    region_names = []
    for value in region.get("values") or []:
        text = str(value.get("text") or "").strip()
        if text in EXPECTED_DANISH_REGIONS:
            region_values.append(str(value.get("id")))
            region_names.append(text)
    if set(region_names) != EXPECTED_DANISH_REGIONS:
        missing = sorted(EXPECTED_DANISH_REGIONS - set(region_names))
        raise RuntimeError(f"StatBank region catalogue is missing current regions: {missing}")

    def is_total(text: str, value_id: str) -> bool:
        label = normalize_label(text)
        code = normalize_label(value_id)
        return label in {"total", "all", "age, total", "sex, total"} or code in {"tot", "ialt"}

    time_value = _value_id(
        time,
        lambda text, value_id: str(value_id) == str(period) or str(text).strip() == str(period),
    )
    return {
        "region_variable": str(region.get("id")),
        "region_values": region_values,
        "sex_variable": str(sex.get("id")),
        "sex_total": _value_id(sex, is_total),
        "age_variable": str(age.get("id")),
        "age_total": _value_id(age, is_total),
        "time_variable": str(time.get("id")),
        "time_value": time_value,
    }


def statbank_request(selection: dict) -> dict:
    return {
        "table": STATBANK_TABLE,
        "format": "CSV",
        "lang": "en",
        "variables": [
            {"code": selection["region_variable"], "values": selection["region_values"]},
            {"code": selection["sex_variable"], "values": [selection["sex_total"]]},
            {"code": selection["age_variable"], "values": [selection["age_total"]]},
            {"code": selection["time_variable"], "values": [selection["time_value"]]},
        ],
    }


def parse_statbank_population_csv(text: str) -> dict[str, int]:
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ";"
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        raise RuntimeError("StatBank population response is empty")
    header = [normalize_label(cell) for cell in rows[0]]
    region_index = next(
        (i for i, name in enumerate(header) if "region" in name or "område" in name),
        0,
    )
    value_index = None
    for i, name in enumerate(header):
        if name in {"content", "indhold", "value", "population"}:
            value_index = i
            break
    if value_index is None:
        value_index = len(header) - 1

    out: dict[str, int] = {}
    for row in rows[1:]:
        if len(row) <= max(region_index, value_index):
            continue
        region_name = str(row[region_index]).strip()
        raw = str(row[value_index]).strip().replace(".", "").replace(" ", "")
        raw = raw.replace(",", ".")
        try:
            value = int(round(float(raw)))
        except ValueError:
            continue
        if region_name and value > 0:
            out[region_name] = value
    return out


def fetch_denmark_population(*, period: str = CURRENT_PERIOD) -> dict[str, int]:
    tableinfo = json.loads(
        post_json(STATBANK_TABLEINFO_URL, {"table": STATBANK_TABLE, "lang": "en"}).decode("utf-8")
    )
    selection = statbank_selection(tableinfo, period=period)
    data = post_json(STATBANK_DATA_URL, statbank_request(selection)).decode("utf-8-sig")
    population = parse_statbank_population_csv(data)
    missing = sorted(EXPECTED_DANISH_REGIONS - set(population))
    if missing:
        raise RuntimeError(f"StatBank population response is missing regions: {missing}")
    return population


def enrich_denmark_payload(payload: dict, population: dict[str, int], *, period: str = CURRENT_PERIOD) -> dict:
    result = json.loads(json.dumps(payload))
    for feature in result.get("features") or []:
        props = feature.get("properties") or {}
        name = str(props.get("name") or "").strip()
        value = population.get(name)
        if value is None:
            props.pop("population", None)
            continue
        props["population"] = {
            "value": int(value),
            "unit": "persons",
            "period": str(period),
            "source": SOURCE_NAME,
            "source_url": STATBANK_SOURCE_URL,
            "confidence": "official-statistical-observation",
        }
    metadata = result.setdefault("metadata", {})
    covered = sum(1 for feature in result.get("features") or [] if (feature.get("properties") or {}).get("population", {}).get("value"))
    metadata["population_vintage"] = str(period)
    metadata["population_source"] = SOURCE_NAME
    metadata["population_coverage"] = covered
    return result


def update_index(index: dict, payload: dict, *, period: str = CURRENT_PERIOD) -> dict:
    result = json.loads(json.dumps(index))
    descriptor = result.setdefault("partitions", {}).setdefault("DNK", {})
    covered = sum(1 for feature in payload.get("features") or [] if (feature.get("properties") or {}).get("population", {}).get("value"))
    descriptor["population_status"] = "official-observation" if covered else "unknown-not-zero"
    descriptor["population_vintage"] = str(period) if covered else None
    descriptor["population_source"] = SOURCE_NAME if covered else None
    descriptor["population_coverage"] = covered
    return result


def main() -> int:
    dnk_path = SUBDIVISION_DIR / "DNK.geo.json"
    index_path = SUBDIVISION_DIR / "index.json"
    if not dnk_path.exists() or not index_path.exists():
        raise RuntimeError(f"Subdivision snapshots not found in {SUBDIVISION_DIR}")
    population = fetch_denmark_population(period=CURRENT_PERIOD)
    payload = json.loads(dnk_path.read_text(encoding="utf-8"))
    enriched = enrich_denmark_payload(payload, population, period=CURRENT_PERIOD)
    index = update_index(json.loads(index_path.read_text(encoding="utf-8")), enriched, period=CURRENT_PERIOD)
    dnk_path.write_text(json.dumps(enriched, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "partition": "DNK",
        "period": CURRENT_PERIOD,
        "population_coverage": enriched.get("metadata", {}).get("population_coverage"),
        "features": len(enriched.get("features") or []),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
