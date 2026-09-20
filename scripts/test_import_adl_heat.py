#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "scripts" / "import_adl_heat.py"

HEADERS = ["Incident ID","Incident Date","City","State","Incident Type","Ideology","Latitude","Longitude","Description"]

def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADERS)
        writer.writerows(rows)

def run_import(rows: list[list[str]], *, retrieved="2026-09-20", confirm=True):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    source = root / "official-adl-heat.csv"
    out = root / "out"
    write_csv(source, rows)
    cmd = [sys.executable, str(IMPORTER), str(source), "--retrieved", retrieved, "--out-dir", str(out)]
    if confirm:
        cmd.append("--confirm-official-export")
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return tmp, out, proc

def assert_failure(rows, needle: str, **kwargs):
    tmp, _, proc = run_import(rows, **kwargs)
    try:
        assert proc.returncode != 0, proc.stdout + proc.stderr
        assert needle.lower() in (proc.stdout + proc.stderr).lower(), proc.stdout + proc.stderr
    finally:
        tmp.cleanup()

def main() -> int:
    valid = [
        ["1","09/19/2026","Haderslev","Denmark","Example","Example","55.25","9.49","Unsupported geography should remain diagnostic only"],
        ["2","09/18/2026","Austin","TX","Extremist event","Example","30.2672","-97.7431","Valid U.S. row"],
        ["3","09/17/2026","Boston","MA","Extremist event; Other","Example","42.3601","-71.0589","Second valid U.S. row"],
        ["4","09/16/2026","Chicago","IL","Extremist event","Example","","","State aggregate without point geometry"],
    ]
    # Replace deliberately unsupported non-U.S. state value with an unknown token;
    # importer should diagnose it rather than invent a U.S. mapping.
    valid[0][3] = "XX"

    tmp, out, proc = run_import(valid)
    try:
        assert proc.returncode == 0, proc.stdout + proc.stderr
        meta = json.loads((out / "metadata.json").read_text(encoding="utf-8"))
        summary = json.loads((out / "state-summary.json").read_text(encoding="utf-8"))
        geo = json.loads((out / "incidents.geo.json").read_text(encoding="utf-8"))
        snap = meta["snapshot"]
        diag = meta["import_diagnostics"]
        assert snap["status"] == "official-export"
        assert snap["official_export_confirmed"] is True
        assert snap["source_sha256"]
        assert snap["record_count"] == 4
        assert diag["unsupported_state_rows"] == 1
        assert diag["missing_geometry_rows"] == 2
        assert diag["invalid_date_rows"] == 0
        assert diag["invalid_coordinate_rows"] == 0
        assert len(geo["features"]) == 2
        assert summary["states"]["US-TX"]["total"] == 1
        assert summary["states"]["US-MA"]["by_type_token"]["Other"] == 1
        assert summary["states"]["US-IL"]["total"] == 1
    finally:
        tmp.cleanup()

    assert_failure(valid, "confirm-official-export", confirm=False)

    duplicate = [
        ["dup","09/18/2026","Austin","TX","Event","Example","30","-97","a"],
        ["dup","09/17/2026","Boston","MA","Event","Example","","","b"],
    ]
    assert_failure(duplicate, "duplicate adl source ids")

    bad_coord = [["1","09/18/2026","Austin","TX","Event","Example","north","-97","bad"]]
    assert_failure(bad_coord, "invalid adl export coordinates")

    out_of_range = [["1","09/18/2026","Austin","TX","Event","Example","95","-97","bad"]]
    assert_failure(out_of_range, "invalid adl export coordinates")

    bad_date = [["1","not-a-date","Austin","TX","Event","Example","30","-97","bad"]]
    assert_failure(bad_date, "invalid adl export dates")

    future = [["1","09/21/2026","Austin","TX","Event","Example","30","-97","future"]]
    assert_failure(future, "dates after retrieval date", retrieved="2026-09-20")

    print("ADL H.E.A.T. IMPORTER REGRESSION PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
