"""Shared integrity checks for the generated World Map population runtime."""
from __future__ import annotations

from numbers import Real

REQUIRED_POPULATION_FIELDS = ("unit", "period", "source", "resolution_tier")


def _canonical_codes(index: dict) -> list[str]:
    return [
        str(row.get("iso3") or "").upper()
        for row in index.get("countries", [])
        if row.get("iso3")
    ]


def _valid_population_value(value) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and value > 0


def population_coverage(runtime: dict) -> int:
    rows = runtime.get("countries", {})
    if not isinstance(rows, dict):
        return 0
    return sum(
        1
        for row in rows.values()
        if isinstance(row, dict)
        and isinstance(row.get("population"), dict)
        and _valid_population_value(row["population"].get("value"))
    )


def validate_population_runtime(index: dict, runtime: dict, expected: int = 195) -> list[str]:
    errors: list[str] = []
    codes = _canonical_codes(index)
    unique_codes = set(codes)

    if len(codes) != expected or len(unique_codes) != expected:
        errors.append(
            f"expected {expected} unique canonical country ISO3 codes; "
            f"found {len(codes)} rows / {len(unique_codes)} unique"
        )

    rows = runtime.get("countries", {})
    if not isinstance(rows, dict):
        return errors + ["population runtime countries must be an object"]

    resolved = 0
    for code in sorted(unique_codes):
        row = rows.get(code)
        if not isinstance(row, dict):
            errors.append(f"{code}: missing population runtime row")
            continue
        population = row.get("population")
        if not isinstance(population, dict):
            errors.append(f"{code}: missing population cell")
            continue
        if not _valid_population_value(population.get("value")):
            errors.append(f"{code}: population value must be numeric and > 0")
            continue
        resolved += 1
        for field in REQUIRED_POPULATION_FIELDS:
            value = population.get(field)
            if value is None or value == "":
                errors.append(f"{code}: population {field} is required")

    declared = runtime.get("population_coverage")
    if declared != resolved:
        errors.append(
            f"population_coverage declares {declared!r}, but {resolved} canonical countries resolve"
        )
    if resolved != expected:
        errors.append(f"resolved population coverage must be {expected}; found {resolved}")
    return errors
