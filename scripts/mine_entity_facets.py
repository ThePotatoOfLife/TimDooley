#!/usr/bin/env python3
"""Mine review-only entity facet candidates from canonical repository sources.

This script NEVER edits entity-facet-ledger.json. It emits candidates for review.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "knowledge/story/entity-facet-ledger.json"
PLAN = ROOT / "data/entity-facet-mining-plan.json"
OUT = ROOT / "knowledge/story/entity-facet-candidates.json"

TITLE_WORDS = ("king", "queen", "doctor", "professor", "sage", "scholar", "guardian", "sentinel", "messenger", "spudologist")
POWER_WORDS = ("wings", "eyes", "levitation", "light", "dimension", "spiral", "fly", "flying", "navigate", "guardian", "watcher")
ROLE_WORDS = ("companion", "student", "challenger", "gardener", "builder", "supporter", "ally", "rival", "witness", "moderator")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean_html(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def candidate(entity_id, ctype, label, source_ref, provenance, strength="established_scene", note=None):
    return {
        "entity_id": entity_id,
        "type": ctype,
        "label": label.strip(),
        "strength_suggestion": strength,
        "source_ref": source_ref,
        "provenance": provenance,
        "review_status": "candidate",
        **({"note": note} if note else {}),
    }


def add_unique(rows, row):
    key = (
        row["entity_id"],
        row["type"],
        row["label"].casefold(),
        row.get("source_ref", ""),
    )
    if key not in add_unique.seen:
        add_unique.seen.add(key)
        rows.append(row)
add_unique.seen = set()


def mine_structured(rows, ledger):
    # Being registry
    path = ROOT / "knowledge/story/being-room-registry.json"
    if path.exists():
        data = load(path)
        by_label = {e["label"].casefold(): eid for eid, e in ledger["entities"].items()}
        for rec in data.get("beings", []):
            eid = rec.get("id") if rec.get("id") in ledger["entities"] else by_label.get(str(rec.get("label", "")).casefold())
            if not eid:
                continue
            for label in rec.get("gifts_or_functions", []):
                add_unique(rows, candidate(eid, "capability", str(label), str(path.relative_to(ROOT)), "being-room-registry", "repeated"))
            for q in rec.get("open_questions", []):
                add_unique(rows, candidate(eid, "open_question", str(q), str(path.relative_to(ROOT)), "being-room-registry", "unresolved"))

    # CIA enhancement index
    path = ROOT / "knowledge/cia/enhancements-index.json"
    if path.exists():
        data = load(path)
        for eid, rec in data.get("created_beings", {}).items():
            if eid not in ledger["entities"]:
                continue
            for label in rec.get("creative", []):
                add_unique(rows, candidate(eid, "capability", str(label), str(path.relative_to(ROOT)), "CIA creative enhancement", "established_scene", rec.get("boundary")))

        for eid, rec in data.get("characters", {}).items():
            if eid not in ledger["entities"]:
                continue
            for label in rec.get("ordinary", []):
                add_unique(rows, candidate(eid, "capability", str(label), str(path.relative_to(ROOT)), "CIA ordinary capability", "established_scene", rec.get("boundary")))
            for label in rec.get("creative", []):
                add_unique(rows, candidate(eid, "role", str(label), str(path.relative_to(ROOT)), "CIA creative/project enhancement", "interpretive", rec.get("boundary")))


def mine_great_book(rows, ledger):
    chapter_root = ROOT / "great-book/chapters"
    if not chapter_root.exists():
        return

    aliases = {}
    for eid, rec in ledger.get("entities", {}).items():
        vals = [rec.get("label", "")] + list(rec.get("aliases", []))
        aliases[eid] = [v for v in vals if isinstance(v, str) and len(v.strip()) >= 4]

    for page in chapter_root.glob("*.html"):
        raw = page.read_text(encoding="utf-8", errors="replace")
        text = clean_html(raw)
        lower = text.casefold()
        for eid, names in aliases.items():
            hit = next((name for name in names if name.casefold() in lower), None)
            if not hit:
                continue
            # Extract compact windows around the first mention.
            pos = lower.find(hit.casefold())
            window = text[max(0, pos - 220): pos + 520]
            sentences = re.split(r"(?<=[.!?])\s+", window)
            for sentence in sentences:
                s_low = sentence.casefold()
                if hit.casefold() not in s_low and eid.replace("-", " ") not in s_low:
                    continue
                for word in TITLE_WORDS:
                    if word in s_low:
                        add_unique(rows, candidate(eid, "title", sentence[:220], str(page.relative_to(ROOT)), "Great Book text", "established_scene", "Machine candidate: review exact title span before promotion."))
                        break
                if any(word in s_low for word in POWER_WORDS):
                    add_unique(rows, candidate(eid, "scene_power", sentence[:260], str(page.relative_to(ROOT)), "Great Book text", "established_scene", "Machine candidate: sentence-level scene power; do not promote to species trait automatically."))
                elif any(word in s_low for word in ROLE_WORDS):
                    add_unique(rows, candidate(eid, "role", sentence[:260], str(page.relative_to(ROOT)), "Great Book text", "established_scene"))


def main() -> int:
    ledger = load(LEDGER)
    plan = load(PLAN)
    rows = []
    mine_structured(rows, ledger)
    mine_great_book(rows, ledger)
    payload = {
        "id": "entity-facet-candidates",
        "version": "1.0.0",
        "generated_from_plan": plan["id"],
        "rule": "Review-only output. Nothing here is canon until manually merged into entity-facet-ledger.json.",
        "candidate_count": len(rows),
        "candidates": sorted(rows, key=lambda r: (r["entity_id"], r["type"], r["label"].casefold())),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} candidates to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
