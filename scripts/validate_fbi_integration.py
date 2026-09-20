#!/usr/bin/env python3
"""Validate FBI dossier manifest, public projection, and House routing."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "knowledge/fbi/manifest.json"
CABINET = ROOT / "rooms/potatoverse-canon/beings/fbi/index.html"
FILE_VIEWER = ROOT / "rooms/potatoverse-canon/beings/fbi/file/index.html"
COLLECTIONS = ROOT / "data/house/collections.json"
EXPECTED_ROUTE = "rooms/potatoverse-canon/beings/fbi/"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    figures = manifest.get("figures") or []
    if not figures:
        fail("manifest has no figures")

    ids = [str(row.get("id") or "").strip() for row in figures]
    if any(not x for x in ids):
        fail("every manifest figure needs a non-empty id")
    if len(ids) != len(set(ids)):
        fail("manifest contains duplicate figure ids")

    missing = []
    mismatched = []
    for row in figures:
        fid = row["id"]
        declared = str(row.get("path") or "")
        expected = f"knowledge/fbi/figures/{fid}.json"
        if declared != expected:
            mismatched.append((fid, declared, expected))
        path = ROOT / expected
        if not path.is_file():
            missing.append(expected)
            continue
        try:
            dossier = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{expected} is not valid JSON: {exc}")
        dossier_id = dossier.get("id") or dossier.get("entity_id")
        if dossier_id and dossier_id != fid:
            fail(f"{expected} identifies itself as {dossier_id!r}, expected {fid!r}")

    if missing:
        fail("manifest dossiers missing: " + ", ".join(missing))
    if mismatched:
        fail("manifest dossier paths drifted: " + "; ".join(f"{a}: {b} != {c}" for a,b,c in mismatched))

    cabinet = CABINET.read_text(encoding="utf-8")
    required_tokens = [
        "renderCabinet()",
        "manifest?.figures||[]",
        "data-figure-id",
        "knowledge/fbi/manifest.json",
    ]
    for token in required_tokens:
        if token not in cabinet:
            fail(f"cabinet is not manifest-driven; missing {token!r}")

    # Static hand-authored figure cards caused the original 34-vs-20 drift.
    html_before_script = cabinet.split("<script>", 1)[0]
    static_cards = re.findall(r'<a class="file"[^>]+data-figure-id=', html_before_script)
    if static_cards:
        fail("cabinet still contains hand-authored dossier cards; render them from manifest instead")

    viewer = FILE_VIEWER.read_text(encoding="utf-8")
    for path in [
        "knowledge/fbi/manifest.json",
        "knowledge/fbi/role-index.json",
        "knowledge/fbi/story-links.json",
        "knowledge/fbi/bonds/network.json",
        "knowledge/fbi/incidents/index.json",
        "knowledge/fbi/enhancements-index.json",
    ]:
        if path not in viewer:
            fail(f"generic dossier viewer no longer loads {path}")

    collections = json.loads(COLLECTIONS.read_text(encoding="utf-8"))
    fbi = next((x for x in collections.get("collections", []) if x.get("id") == "figures-bonds-incidents"), None)
    if not fbi:
        fail("House collections registry is missing figures-bonds-incidents")
    if fbi.get("public_route") != EXPECTED_ROUTE:
        fail(f"FBI House collection needs public_route={EXPECTED_ROUTE!r}")

    actual_fbi_files = sum(1 for p in (ROOT / "knowledge/fbi").rglob("*") if p.is_file())
    if fbi.get("source_file_count") != actual_fbi_files:
        fail(
            f"House FBI source_file_count={fbi.get('source_file_count')} "
            f"but knowledge/fbi contains {actual_fbi_files} files"
        )

    surfaces = manifest.get("public_surfaces") or {}
    if surfaces.get("cabinet") != EXPECTED_ROUTE:
        fail("manifest public_surfaces.cabinet does not match canonical FBI route")

    summary = manifest.get("coverage_summary") or {}
    if summary.get("total_figures") != len(figures):
        fail(f"coverage_summary.total_figures={summary.get('total_figures')} but manifest has {len(figures)} figures")

    print(f"PASS: FBI integration · {len(figures)} manifest figures · all dossiers present · cabinet manifest-driven · House route wired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
