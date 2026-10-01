#!/usr/bin/env python3
"""Run explicit repository contracts with complete failure collection."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / ".quality-logs" / "explicit-contracts"
REPORT = ROOT / "quality-report-explicit-contracts.json"

CHECKS = [
    "scripts/validate_reader_richness.py",
    "scripts/validate_room_holdings.py",
    "scripts/validate_room_inhabitants.py",
    "scripts/validate_room_featured_objects.py",
    "scripts/validate_room_archive_drawers.py",
    "scripts/validate_corpus_surface_coverage.py",
    "scripts/validate_dwelling_featured_objects.py",
    "scripts/validate_public_reader_completeness.py",
    "scripts/validate_room_interfaces.py",
    "scripts/validate_legacy_fbi_redirects.py",
    "scripts/validate_seo_pipeline.py",
    "scripts/validate_repo_hygiene.py",
    "scripts/validate_tradition_routes.py",
    "scripts/validate_entity_facets.py",
]

def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, rel in enumerate(CHECKS, start=1):
        started = time.time()
        log = LOG_DIR / ("%02d-%s.log" % (index, Path(rel).stem))
        proc = subprocess.run(
            ["python", rel],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log.write_text(proc.stdout or "", encoding="utf-8")
        row = {
            "validator": rel,
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "return_code": proc.returncode,
            "seconds": round(time.time() - started, 2),
            "log": log.relative_to(ROOT).as_posix(),
        }
        rows.append(row)
        print("[%s] %s (%.2fs)" % (row["status"], rel, row["seconds"]))
        if proc.returncode:
            print("\n".join((proc.stdout or "").splitlines()[-40:]))
    failures = [row for row in rows if row["status"] == "FAIL"]
    payload = {
        "status": "FAIL" if failures else "PASS",
        "checks": len(rows),
        "failures": len(failures),
        "results": rows,
    }
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Explicit contracts: %s · %d failures / %d checks" % (
        payload["status"], len(failures), len(rows)
    ))
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
