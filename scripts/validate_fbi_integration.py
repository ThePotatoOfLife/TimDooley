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
        "knowledge/fbi/tim-moral-symbolic-taxonomy.json",
        "knowledge/fbi/presence-index.json",
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
        "Karmic debt / obligation",
        "Inherited symbolic states",
        "Episode attributes",
        "Upgrades / handicaps",
        "Potato of Life coordinates",
        "Why Tim assigned the state",
        "State History",
        "Source-derived co-presence",
        "Recorded presence",
        "First recorded:",
        "Last recorded:",
        "Turning points",
    ):
        if token not in viewer:
            fail(f"generic dossier viewer lost rich dossier projection token {token!r}")

    discovery_surfaces = {
        "home": ROOT / "index.html",
        "explore": ROOT / "explore/index.html",
        "rooms": ROOT / "rooms/index.html",
        "house": ROOT / "house/index.html",
        "beings": ROOT / "rooms/potatoverse-canon/beings/index.html",
    }
    canonical_fragment = "rooms/potatoverse-canon/beings/cia/"
    for name, path in discovery_surfaces.items():
        text = path.read_text(encoding="utf-8")
        if canonical_fragment not in text and name != "beings":
            fail(f"{name} no longer exposes a direct CIA doorway")
        if name == "beings" and 'href="cia/"' not in text:
            fail("Beings & Cast no longer exposes the CIA doorway")

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

    taxonomy_index = (manifest.get("indexes") or {}).get("tim_moral_symbolic_taxonomy")
    if taxonomy_index != "knowledge/fbi/tim-moral-symbolic-taxonomy.json":
        fail("manifest must register the CIA Tim moral-symbolic taxonomy")
    taxonomy_path = ROOT / taxonomy_index
    if not taxonomy_path.is_file():
        fail("CIA Tim moral-symbolic taxonomy is missing")
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    dog_rule = (((taxonomy.get("core_role_inheritance") or {}).get("dog") or {}).get("user_canon_rule") or "")
    if "Mud Dweller" not in dog_rule:
        fail("CIA taxonomy lost Dog ⇒ Mud Dweller inheritance")
    mud_rule = (((taxonomy.get("core_role_inheritance") or {}).get("mud_dweller") or {}).get("user_canon_rule") or "")
    if "Tree of Strife" not in mud_rule:
        fail("CIA taxonomy lost Mud Dweller ⇒ Tree of Strife inheritance")
    individual_rule = (((taxonomy.get("debt_model") or {}).get("individual_rule")) or "")
    if "unless Tim explicitly assigned" not in individual_rule:
        fail("CIA taxonomy must forbid invented per-person karmic debt amounts")

    modifiers = taxonomy.get("state_modifiers") or {}
    if not (modifiers.get("upgrades") and modifiers.get("handicaps")):
        fail("CIA taxonomy must define both upgrades and handicaps")

    if not taxonomy.get("transition_model"):
        fail("CIA taxonomy lost symbolic transition model")
    if not taxonomy.get("potato_of_life_topology"):
        fail("CIA taxonomy lost Potato of Life topology model")
    if not taxonomy.get("causal_attribution_model"):
        fail("CIA taxonomy lost causal attribution model")
    if not taxonomy.get("next_state_model"):
        fail("CIA taxonomy lost next-state model")
    if "perpetual_lying" not in (taxonomy.get("attribute_inference_rules") or {}):
        fail("CIA taxonomy lost guarded inference rule for perpetual lying")
    bonds = json.loads((ROOT / "knowledge/fbi/bonds/network.json").read_text(encoding="utf-8"))
    if not bonds.get("flow_model"):
        fail("CIA associations lost relational-flow model")
    if not any((edge.get("flow") or {}).get("types") for edge in bonds.get("edges", [])):
        fail("CIA relational-flow model has no seeded source-bounded edges")

    enhancements = json.loads((ROOT / "knowledge/fbi/enhancements-index.json").read_text(encoding="utf-8"))
    if "state_modifier_model" not in enhancements:
        fail("CIA enhancements index is not linked to the state-modifier taxonomy")
    if "do not create numeric karmic debt" not in str(enhancements.get("debt_rule") or ""):
        fail("CIA enhancements index must forbid debt inference from modifiers")

    presence_index = (manifest.get("indexes") or {}).get("presence")
    if presence_index != "knowledge/fbi/presence-index.json":
        fail("manifest indexes.presence must point to knowledge/fbi/presence-index.json")
    presence_path = ROOT / presence_index
    if not presence_path.is_file():
        fail("CIA presence index is missing")
    presence = json.loads(presence_path.read_text(encoding="utf-8"))
    presence_entries = presence.get("entries") or []
    if len(presence_entries) != len(figures):
        fail(f"CIA presence index has {len(presence_entries)} entries for {len(figures)} figures")
    exact_date = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for row in presence_entries:
        first = row.get("first_recorded")
        last = row.get("last_recorded")
        if first is not None and not exact_date.match(str(first)):
            fail(f"{row.get('id')} presence first_recorded is not an exact YYYY-MM-DD date")
        if last is not None and not exact_date.match(str(last)):
            fail(f"{row.get('id')} presence last_recorded is not an exact YYYY-MM-DD date")
        dates = row.get("exact_recorded_dates") or []
        if dates and (first != dates[0] or last != dates[-1]):
            fail(f"{row.get('id')} presence first/last does not match exact date range")
        if first and last and first > last:
            fail(f"{row.get('id')} presence first_recorded is after last_recorded")

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

        if fid in {"dim", "txt", "matthew-mtclassic", "rahu", "metalorian", "supersusi87", "anja", "tachy", "port-monkey"}:
            if not witness.get("debt_relation"):
                fail(f"{fid} mature CIA file is missing debt_relation")
            if not witness.get("episode_attributes"):
                fail(f"{fid} mature CIA file is missing episode_attributes")

    summary = manifest.get("coverage_summary") or {}
    if summary.get("total_figures") != len(figures):
        fail(f"coverage_summary.total_figures={summary.get('total_figures')} but manifest has {len(figures)} figures")

    print(f"PASS: CIA integration · {len(figures)} manifest figures · all dossiers present · CIA cabinet manifest-driven · legacy FBI routes bounded · House route wired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
