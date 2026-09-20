#!/usr/bin/env python3
"""Validate CIA character dossiers, public projection, legacy compatibility, and House routing."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "knowledge/fbi/manifest.json"
CABINET = ROOT / "rooms/potatoverse-canon/beings/cia/index.html"
FILE_VIEWER = ROOT / "rooms/potatoverse-canon/beings/cia/file/index.html"
COLLECTIONS = ROOT / "data/house/collections.json"
LEGACY_CABINET = ROOT / "rooms/potatoverse-canon/beings/fbi/index.html"
LEGACY_FILE_VIEWER = ROOT / "rooms/potatoverse-canon/beings/fbi/file/index.html"
EXPECTED_ROUTE = "rooms/potatoverse-canon/beings/cia/"
LEGACY_ROUTE = "rooms/potatoverse-canon/beings/fbi/"


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
        "knowledge/fbi/conversation-recovery.json",
    ]:
        if path not in viewer:
            fail(f"generic dossier viewer no longer loads {path}")

    for token in (
        'data-panel="conversations"',
        'data-panel="patterns"',
        'data-panel="knowledge"',
        'data-panel="witness"',
        "function witnessHtml()",
        "Tim’s character reading",
        "function conversationsHtml()",
        "function patternsHtml()",
        "Archive coverage",
        "Recovery pressure",
    ):
        if token not in viewer:
            fail(f"generic dossier viewer lost rich dossier projection token {token!r}")

    collections = json.loads(COLLECTIONS.read_text(encoding="utf-8"))
    fbi = next((x for x in collections.get("collections", []) if x.get("id") == "figures-bonds-incidents"), None)
    if not fbi:
        fail("House collections registry is missing figures-bonds-incidents")
    if fbi.get("public_route") != EXPECTED_ROUTE:
        fail(f"CIA House collection needs public_route={EXPECTED_ROUTE!r}")

    actual_fbi_files = sum(1 for p in (ROOT / "knowledge/fbi").rglob("*") if p.is_file())
    if fbi.get("source_file_count") != actual_fbi_files:
        fail(
            f"House CIA source_file_count={fbi.get('source_file_count')} "
            f"but knowledge/fbi contains {actual_fbi_files} files"
        )

    conversation_index = (manifest.get("indexes") or {}).get("conversations")
    if conversation_index != "knowledge/fbi/conversation-recovery.json":
        fail("manifest indexes.conversations must point to knowledge/fbi/conversation-recovery.json")
    conversation_path = ROOT / conversation_index
    if not conversation_path.is_file():
        fail("conversation recovery index is missing")
    conversation = json.loads(conversation_path.read_text(encoding="utf-8"))
    if not conversation.get("entries"):
        fail("conversation recovery index has no entries")
    for fid in ("matthew-mtclassic", "mediomu007", "dim"):
        if not any(fid in (row.get("figures") or []) for row in conversation.get("entries", [])):
            fail(f"conversation recovery has no entries for {fid}")

    if "dim" not in ids:
        fail("DIM must remain a first-class FBI manifest figure")
    dim_path = ROOT / "knowledge/fbi/figures/dim.json"
    if not dim_path.is_file():
        fail("DIM dossier is missing")

    if manifest.get("title") != "CIA — Characters, Incidents & Associations":
        fail("public dossier bureau title must remain CIA — Characters, Incidents & Associations")
    public_identity = manifest.get("public_identity") or {}
    if public_identity.get("acronym") != "CIA":
        fail("manifest public_identity.acronym must remain CIA")
    if "Central Intelligence Agency" not in manifest.get("disclaimer", ""):
        fail("CIA non-affiliation disclaimer is missing")
    if "knowledge/fbi/" not in str(public_identity.get("legacy_storage_namespace") or ""):
        fail("legacy FBI storage namespace must remain documented during compatibility migration")

    legacy_cabinet = LEGACY_CABINET.read_text(encoding="utf-8")
    if "../cia/" not in legacy_cabinet or "Compatibility route" not in legacy_cabinet:
        fail("legacy /fbi/ cabinet must remain a compatibility doorway into CIA")
    legacy_file = LEGACY_FILE_VIEWER.read_text(encoding="utf-8")
    if "../../cia/file/" not in legacy_file or "noindex,follow" not in legacy_file:
        fail("legacy FBI file viewer must redirect to CIA and remain noindex")

    surfaces = manifest.get("public_surfaces") or {}
    if surfaces.get("cabinet") != EXPECTED_ROUTE:
        fail("manifest public_surfaces.cabinet does not match canonical CIA route")
    public_identity = manifest.get("public_identity") or {}
    if public_identity.get("canonical_route") != EXPECTED_ROUTE:
        fail("CIA canonical route is not registered")
    if public_identity.get("legacy_route") != LEGACY_ROUTE:
        fail("legacy FBI compatibility route is not registered")

    tim_witness_required = {
        "dim", "txt", "matthew-mtclassic", "mediomu007", "termite", "rahu",
        "marty-biz", "metalorian", "bigtech", "optimistique", "ledgeview", "pondo", "kale",
        "highly-regarded", "darkchild", "jazzy", "barry-bletunick", "duaaaht",
        "supersusi87", "anja", "port-monkey", "sammy", "juice", "rage", "tachy",
        "literally", "anacondasin", "potato-repair-guy", "pkfc", "don-jefe",
        "petty-wappo", "gg"
    }
    for fid in tim_witness_required:
        dossier = json.loads((ROOT / f"knowledge/fbi/figures/{fid}.json").read_text(encoding="utf-8"))
        witness = dossier.get("tim_witness") or {}
        for key in ("character_reading", "fruit", "karma", "placement", "symbols", "repair_path", "boundary"):
            if not witness.get(key):
                fail(f"{fid} Tim-witness layer missing {key}")

    summary = manifest.get("coverage_summary") or {}
    if summary.get("total_figures") != len(figures):
        fail(f"coverage_summary.total_figures={summary.get('total_figures')} but manifest has {len(figures)} figures")

    print(f"PASS: CIA integration · {len(figures)} manifest figures · all dossiers present · CIA cabinet manifest-driven · legacy FBI routes bounded · House route wired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
