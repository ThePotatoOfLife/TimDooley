#!/usr/bin/env python3
"""Regression coverage for scripts/import_world_adm1.py."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "scripts" / "import_world_adm1.py"


def run(args: list[str], expect: int = 0) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [sys.executable, str(IMPORTER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != expect:
        raise AssertionError(
            f"unexpected exit {proc.returncode}, expected {expect}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_raw:
        tmp = Path(tmp_raw)
        source = tmp / "source.geojson"
        out = tmp / "out"
        fixture = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name_en": "Alpha Region",
                        "name_local": "Alfa",
                        "iso_3166_2": "ZZ-A",
                        "kind": "oblast",
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[10, 10], [11, 10], [11, 11], [10, 11], [10, 10]]],
                    },
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name_en": "Beta Region",
                        "name_local": "Beta",
                        "iso_3166_2": "ZZ-B",
                        "kind": "republic",
                    },
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [[[[12, 10], [13, 10], [13, 11], [12, 11], [12, 10]]]],
                    },
                },
            ],
        }
        source_text = json.dumps(fixture, ensure_ascii=False, separators=(",", ":"))
        source.write_text(source_text, encoding="utf-8")
        source_sha = hashlib.sha256(source.read_bytes()).hexdigest()

        base_args = [
            str(source),
            "--iso3", "ZZZ",
            "--parent-name", "Testland",
            "--id-prefix", "ZZ-",
            "--name-field", "name_en",
            "--local-name-field", "name_local",
            "--code-field", "iso_3166_2",
            "--type-field", "kind",
            "--source-label", "Fixture ADM1",
            "--source-ref", "fixture@test",
            "--source-vintage", "2026-test",
            "--representation-note", "Administrative fixture only; not a live control boundary.",
            "--expected-count", "2",
            "--viewport", "9", "14", "9", "12",
            "--out-dir", str(out),
        ]
        proc = run(base_args)
        if "WORLD MAP ADM1 IMPORT PASSED" not in proc.stdout:
            raise AssertionError("success marker missing")

        partition_path = out / "ZZZ.geo.json"
        descriptor_path = out / "ZZZ.partition.json"
        partition = json.loads(partition_path.read_text(encoding="utf-8"))
        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))

        if [row["properties"]["id"] for row in partition["features"]] != ["ZZ-A", "ZZ-B"]:
            raise AssertionError("stable canonical ids drifted")
        if partition["features"][0]["properties"]["local_name"] != "Alfa":
            raise AssertionError("local-name projection missing")
        if partition["metadata"]["source_sha256"] != source_sha:
            raise AssertionError("partition source hash mismatch")
        if descriptor["source_sha256"] != source_sha:
            raise AssertionError("descriptor source hash mismatch")
        if descriptor["bytes"] != partition_path.stat().st_size:
            raise AssertionError("descriptor byte count does not match emitted partition")
        if descriptor["feature_count"] != 2 or len(descriptor["search_records"]) != 2:
            raise AssertionError("descriptor coverage/search records drifted")
        if descriptor["viewport_bounds"] != {"west": 9.0, "east": 14.0, "south": 9.0, "north": 12.0}:
            raise AssertionError("viewport projection drifted")
        if any((row.get("population") or {}).get("value") for row in partition["features"]):
            raise AssertionError("generic geometry-first importer invented population")
        if not all(row["properties"].get("population_status") == "unknown-not-zero" for row in partition["features"]):
            raise AssertionError("unknown population semantics missing")

        # Count drift must fail closed.
        count_args = list(base_args)
        expected_index = count_args.index("--expected-count") + 1
        count_args[expected_index] = "3"
        count_args[-1] = str(tmp / "count-fail")
        count_proc = run(count_args, expect=1)
        if "feature count drift" not in (count_proc.stdout + count_proc.stderr):
            raise AssertionError("count-drift guard failed for the wrong reason")

        # Duplicate canonical IDs must fail closed.
        duplicate = json.loads(source_text)
        duplicate["features"][1]["properties"]["iso_3166_2"] = "ZZ-A"
        duplicate_path = tmp / "duplicate.geojson"
        duplicate_path.write_text(json.dumps(duplicate), encoding="utf-8")
        dup_args = list(base_args)
        dup_args[0] = str(duplicate_path)
        dup_args[-1] = str(tmp / "dup-fail")
        run(dup_args, expect=1)

        # Non-polygon geometry must fail closed.
        point = json.loads(source_text)
        point["features"][0]["geometry"] = {"type": "Point", "coordinates": [10, 10]}
        point_path = tmp / "point.geojson"
        point_path.write_text(json.dumps(point), encoding="utf-8")
        point_args = list(base_args)
        point_args[0] = str(point_path)
        point_args[-1] = str(tmp / "point-fail")
        run(point_args, expect=1)

    print("WORLD MAP ADM1 IMPORT REGRESSION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
