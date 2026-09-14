#!/usr/bin/env python3
"""Validate complete population coverage in a generated World Map demography runtime."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED = 195


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="data/countries/index.json")
    parser.add_argument("--runtime", required=True)
    args = parser.parse_args()

    index = json.loads(Path(args.index).read_text(encoding="utf-8"))
    runtime = json.loads(Path(args.runtime).read_text(encoding="utf-8"))
    codes = {row.get("iso3") for row in index.get("countries", []) if row.get("iso3")}
    errors: list[str] = []

    if len(codes) != EXPECTED:
        errors.append(f"expected {EXPECTED} canonical ISO3 codes; found {len(codes)}")

    rows = runtime.get("countries", {})
    resolved = 0
    for code in sorted(codes):
        population = (rows.get(code) or {}).get("population")
        if not isinstance(population, dict):
            errors.append(f"{code}: missing population")
            continue
        value = population.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"{code}: population must be positive")
            continue
        if not population.get("source"):
            errors.append(f"{code}: population source missing")
        if population.get("year") in (None, "") and population.get("period") in (None, ""):
            errors.append(f"{code}: population reference period missing")
        resolved += 1

    if resolved != EXPECTED:
        errors.append(f"resolved population coverage must be {EXPECTED}; found {resolved}")
    if runtime.get("population_coverage") != resolved:
        errors.append("declared population_coverage does not match resolved rows")

    if errors:
        print("WORLD POPULATION BUILD VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print(f"WORLD POPULATION BUILD VALIDATION PASSED · {resolved}/{EXPECTED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
