#!/usr/bin/env python3
"""Build a reviewed ADM1 statistics sidecar from two tabular source exports.

The importer is intentionally acquisition-agnostic: it does not download data.
For Statistics Denmark, feed reviewed BEFOLK3 population and ARE207 area exports
plus a source contract whose subdivision_mapping rows contain verified
statbank_area_code values.

A production build fails closed when stable source geography codes have not yet
been reviewed. Region names are checked as an additional human-readable guard,
not used as the sole canonical join.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def norm(value: object) -> str:
    return clean(value).casefold()


def number(value: object, *, integer: bool) -> float | int:
    text = clean(value).replace("\u00a0", "").replace(" ", "")
    if not text:
        raise ValueError("empty numeric value")
    # StatBank exports may use Danish decimal commas. Thousands separators are
    # rejected instead of guessed; reviewed exports should request plain values.
    if "," in text and "." in text:
        raise ValueError(f"ambiguous numeric separators: {value!r}")
    text = text.replace(",", ".")
    result = float(text)
    if result <= 0:
        raise ValueError(f"value must be positive: {value!r}")
    if integer:
        if not result.is_integer():
            raise ValueError(f"population must be an integer: {value!r}")
        return int(result)
    return result


def read_rows(path: Path) -> list[dict[str, str]]:
    sample = path.read_text(encoding="utf-8-sig")
    try:
        dialect = csv.Sniffer().sniff(sample[:4096], delimiters=";,	")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(sample.splitlines(), dialect=dialect))


def indexed_rows(
    rows: list[dict[str, str]],
    *,
    code_column: str,
    name_column: str,
    value_column: str,
    expected: dict[str, dict],
    label: str,
    integer: bool,
) -> dict[str, dict]:
    found: dict[str, dict] = {}
    unknown: list[str] = []
    for row in rows:
        code = clean(row.get(code_column))
        name = clean(row.get(name_column))
        value = row.get(value_column)
        if not code and not name and not clean(value):
            continue
        mapping = expected.get(code)
        if mapping is None:
            unknown.append(f"{code or '∅'} {name or '∅'}")
            continue
        expected_name = clean(mapping.get("name"))
        if norm(name) != norm(expected_name):
            raise SystemExit(
                f"{label}: code {code} name mismatch: expected {expected_name!r}, got {name!r}"
            )
        if code in found:
            raise SystemExit(f"{label}: duplicate source geography code {code}")
        try:
            parsed = number(value, integer=integer)
        except ValueError as exc:
            raise SystemExit(f"{label}: {code} {expected_name}: {exc}")
        found[code] = {"mapping": mapping, "value": parsed}
    if unknown:
        raise SystemExit(f"{label}: unexpected source rows; export the reviewed region selection only: {', '.join(unknown[:8])}")
    missing = sorted(set(expected) - set(found))
    if missing:
        raise SystemExit(f"{label}: missing verified source geography codes: {', '.join(missing)}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-contract", type=Path, required=True)
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--area", type=Path, required=True)
    parser.add_argument("--population-code-column", required=True)
    parser.add_argument("--population-name-column", required=True)
    parser.add_argument("--population-value-column", required=True)
    parser.add_argument("--area-code-column", required=True)
    parser.add_argument("--area-name-column", required=True)
    parser.add_argument("--area-value-column", required=True)
    parser.add_argument("--retrieved-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    for path in (args.source_contract, args.population, args.area):
        if not path.is_file():
            raise SystemExit(f"input missing: {path}")

    contract = json.loads(args.source_contract.read_text(encoding="utf-8"))
    iso3 = clean(contract.get("parent_iso3")).upper()
    if not re.fullmatch(r"[A-Z]{3}", iso3):
        raise SystemExit("source contract parent_iso3 must be three uppercase letters")
    mappings = contract.get("subdivision_mapping") or []
    if not mappings:
        raise SystemExit("source contract has no subdivision_mapping")
    codes: dict[str, dict] = {}
    for row in mappings:
        stable_id = clean(row.get("subdivision_id"))
        code = clean(row.get("statbank_area_code"))
        name = clean(row.get("name"))
        if not stable_id or not name:
            raise SystemExit("source contract mapping rows require subdivision_id + name")
        if not code:
            raise SystemExit(
                f"{stable_id} {name}: verified statbank_area_code is required before statistics generation"
            )
        if code in codes:
            raise SystemExit(f"duplicate verified statbank_area_code in source contract: {code}")
        codes[code] = row

    population_rows = indexed_rows(
        read_rows(args.population),
        code_column=args.population_code_column,
        name_column=args.population_name_column,
        value_column=args.population_value_column,
        expected=codes,
        label="population",
        integer=True,
    )
    area_rows = indexed_rows(
        read_rows(args.area),
        code_column=args.area_code_column,
        name_column=args.area_name_column,
        value_column=args.area_value_column,
        expected=codes,
        label="area",
        integer=False,
    )

    metrics = contract.get("metrics") or {}
    pop_source = metrics.get("population") or {}
    area_source = metrics.get("area_km2") or {}
    period = clean(contract.get("reference_period")) or None
    records = []
    for code, mapping in sorted(codes.items(), key=lambda item: clean(item[1].get("subdivision_id"))):
        pop = population_rows[code]["value"]
        area = area_rows[code]["value"]
        records.append({
            "subdivision_id": clean(mapping.get("subdivision_id")),
            "population": pop,
            "population_meta": {
                "period": period,
                "unit": "persons",
                "source": clean(contract.get("source_owner")),
                "source_ref": clean(pop_source.get("source_url")),
                "source_table": clean(pop_source.get("table")),
                "source_geography_code": code,
                "status": "observed",
            },
            "area_km2": area,
            "area_km2_meta": {
                "period": period,
                "unit": "km2",
                "source": clean(contract.get("source_owner")),
                "source_ref": clean(area_source.get("source_url")),
                "source_table": clean(area_source.get("table")),
                "source_geography_code": code,
                "status": "observed",
            },
        })

    payload = {
        "schema_version": "1.0.0",
        "status": "review-required-generated-statistics",
        "parent_iso3": iso3,
        "reference_period": period,
        "source_owner": clean(contract.get("source_owner")),
        "retrieved_at": args.retrieved_at,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "source_contract": args.source_contract.name,
            "population_sha256": sha256(args.population),
            "area_sha256": sha256(args.area),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WORLD MAP SUBDIVISION STATISTICS IMPORT PASSED · {iso3} · {len(records)} records")
    print(f"population sha256: {payload['inputs']['population_sha256']}")
    print(f"area sha256: {payload['inputs']['area_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
