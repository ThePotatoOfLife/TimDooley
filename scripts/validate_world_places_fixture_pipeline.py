#!/usr/bin/env python3
"""Exercise the World Places builder and data validator end-to-end on checked-in fixtures."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_world_places.py"
VALIDATOR = ROOT / "scripts" / "validate_world_places.py"
FIXTURE = ROOT / "tests" / "fixtures" / "world-places"
COUNTRY_INDEX = ROOT / "data" / "countries" / "index.json"
EXPECTED_COUNTRIES = {"DNK", "DEU"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(errors: list[str]) -> int:
    print("WORLD PLACES FIXTURE PIPELINE VALIDATION FAILED")
    for error in errors:
        print("-", error)
    return 1


def main() -> int:
    errors: list[str] = []
    for path in (BUILDER, VALIDATOR, FIXTURE / "geonames-cities-sample.txt", FIXTURE / "capitals-sample.geo.json", COUNTRY_INDEX):
        if not path.exists():
            errors.append(f"missing fixture-pipeline input: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    with tempfile.TemporaryDirectory(prefix="world-places-fixture-") as tmp:
        out = Path(tmp) / "world-places"
        build = subprocess.run(
            [
                sys.executable, str(BUILDER),
                "--fixture", str(FIXTURE),
                "--country-index", str(COUNTRY_INDEX),
                "--output", str(out),
                "--refresh-date", "2026-09-15-fixture",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if build.returncode:
            errors.append("fixture build failed: " + (build.stderr.strip() or build.stdout.strip()))
            return fail(errors)

        validate = subprocess.run(
            [sys.executable, str(VALIDATOR), "--data-only", "--data-dir", str(out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if validate.returncode:
            errors.append("generated fixture data failed canonical validation: " + (validate.stdout.strip() or validate.stderr.strip()))
            return fail(errors)

        index = load_json(out / "index.json")
        major = load_json(out / "global-major.geo.json")
        countries = index.get("countries") or {}
        if set(countries) != EXPECTED_COUNTRIES:
            errors.append(f"fixture partitions must be {sorted(EXPECTED_COUNTRIES)}; found {sorted(countries)}")
        if index.get("dataset_refresh_date") != "2026-09-15-fixture":
            errors.append("fixture refresh date was not propagated into the generated index")
        if index.get("license") != "CC BY 4.0" or "GeoNames" not in str(index.get("attribution") or ""):
            errors.append("fixture output lost GeoNames license/attribution metadata")

        major_by_id = {
            str((feature.get("properties") or {}).get("id")): feature
            for feature in major.get("features", [])
        }
        for place_id, name in (("gn:2618425", "Copenhagen"), ("gn:2950159", "Berlin")):
            feature = major_by_id.get(place_id)
            props = (feature or {}).get("properties") or {}
            if props.get("name") != name or props.get("is_national_capital") is not True:
                errors.append(f"{name} must survive fixture build as its GeoNames identity and a national capital")

        dnk_path = out / str((countries.get("DNK") or {}).get("path") or "")
        dnk = load_json(dnk_path) if dnk_path.exists() else {}
        dnk_by_id = {
            str((feature.get("properties") or {}).get("id")): feature
            for feature in dnk.get("features", [])
        }
        copenhagen = (dnk_by_id.get("gn:2618425") or {}).get("properties") or {}
        aarhus = (dnk_by_id.get("gn:2624652") or {}).get("properties") or {}
        zero_town = (dnk_by_id.get("gn:9999999") or {}).get("properties") or {}
        if copenhagen.get("population") != 1_153_615 or copenhagen.get("capital_status") != "national":
            errors.append("Copenhagen fixture population/capital semantics changed")
        if aarhus.get("population") != 290_598 or aarhus.get("capital_status") != "admin":
            errors.append("Aarhus fixture population/admin-capital semantics changed")
        if zero_town.get("population") is not None:
            errors.append("zero/missing GeoNames population must normalize to null, never numeric zero")
        if zero_town.get("population_source") is not None:
            errors.append("missing population must not carry a population source")

        for feature in dnk.get("features", []):
            props = feature.get("properties") or {}
            if props.get("dataset_refresh_date") != "2026-09-15-fixture":
                errors.append(f"{props.get('id')}: fixture refresh date was not propagated")

    if errors:
        return fail(errors)
    print("WORLD PLACES FIXTURE PIPELINE VALIDATION PASSED · builder → data contract · DNK/DEU · population null semantics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
