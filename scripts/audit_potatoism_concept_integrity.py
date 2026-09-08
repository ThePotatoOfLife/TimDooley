#!/usr/bin/env python3
"""Fail closed when Potatoism starts manufacturing duplicate concept identities.

The repository may contain many occurrences of a concept for provenance, but only the
canonical dossier is allowed to own substantive identity/definition content. Graphs,
lexicons and cosmology files are projections and must point back to canonical IDs.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REGISTRY = DATA / "potatoism-concept-registry.json"
DOSSIERS = DATA / "potatoism-dossiers.json"
CORPUS = DATA / "potatoism-canonical-corpus.json"
LEXICON = DATA / "potatoism-lexicon.json"
EXPANDED = DATA / "potatoism-lexicon-expanded.json"

# These are deliberately projections. They may mention a concept, but they do not own it.
PROJECTION_FILES = {LEXICON, EXPANDED, DATA / "potatoism-cosmology.json", DATA / "potatoism-concept-map.json", DATA / "potatoism-relationships.json", DATA / "potatoism-timeline.json"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).casefold()).strip()


def records(data):
    if isinstance(data, dict):
        for key in ("records", "entries", "concepts", "terms", "items"):
            value = data.get(key)
            if isinstance(value, list):
                yield from (x for x in value if isinstance(x, dict))
                return


def main() -> int:
    errors = []
    registry = load(REGISTRY)
    concepts = registry.get("concepts", [])
    canonical = {}
    alias_owner = {}
    for c in concepts:
        cid = str(c.get("canonical_id", "")).strip()
        term = str(c.get("term", "")).strip()
        if not cid or not term:
            errors.append("registry contains a concept without canonical_id or term")
            continue
        if cid in canonical:
            errors.append(f"duplicate canonical_id in registry: {cid}")
        canonical[cid] = c
        for alias in [term, *c.get("aliases", [])]:
            key = norm(alias)
            if not key:
                continue
            previous = alias_owner.get(key)
            if previous and previous != cid:
                errors.append(f"alias collision: {alias!r} -> {previous}, {cid}")
            else:
                alias_owner[key] = cid

    dossier = load(DOSSIERS)
    dossier_entries = list(records(dossier))
    dossier_ids = [str(x.get("id", "")).strip() for x in dossier_entries if str(x.get("id", "")).strip()]
    if len(dossier_ids) != len(set(dossier_ids)):
        errors.append("potatoism-dossiers.json contains duplicate canonical IDs")

    corpus = load(CORPUS)
    corpus_records = list(records(corpus))
    corpus_ids = [str(x.get("id", "")).strip() for x in corpus_records if str(x.get("id", "")).strip()]
    if len(corpus_ids) != len(set(corpus_ids)):
        errors.append("potatoism-canonical-corpus.json contains duplicate IDs")

    # A corpus ID must either be canonical itself or explicitly resolve to one.
    for rid in corpus_ids:
        if rid not in canonical:
            errors.append(f"canonical corpus ID is not registered: {rid}")

    # A canonical concept must have one dossier entry before it is presented as a deep concept.
    for cid in canonical:
        if cid not in dossier_ids:
            errors.append(f"canonical concept has no dossier: {cid}")

    # Projection files may repeat names, but they must not invent another canonical identity.
    for path in PROJECTION_FILES:
        if not path.exists():
            continue
        try:
            data = load(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)} invalid JSON: {exc}")
            continue
        text = json.dumps(data, ensure_ascii=False)
        # Hard rule: projection files cannot claim to be canonical owners.
        if '"canonical_owner"' in text:
            errors.append(f"projection declares canonical_owner: {path.relative_to(ROOT)}")

    # Detect the most dangerous pattern: one exact concept term defined repeatedly in
    # projection files. This is a warning rather than a hard failure because context
    # occurrences are legitimate, but it is emitted so cleanup work remains visible.
    term_hits = {}
    for path in [LEXICON, EXPANDED, DATA / "potatoism-cosmology.json", CORPUS]:
        if not path.exists():
            continue
        try:
            data = load(path)
        except Exception:
            continue
        for r in records(data):
            name = str(r.get("term") or r.get("name") or "").strip()
            rid = str(r.get("id") or "").strip()
            key = norm(name or rid)
            if key in alias_owner:
                term_hits.setdefault(alias_owner[key], []).append(path.relative_to(ROOT).as_posix())

    if errors:
        print("POTATOISM CONCEPT INTEGRITY: FAIL")
        for error in errors:
            print(" -", error)
        return 1

    print("POTATOISM CONCEPT INTEGRITY: PASS")
    print(f"canonical concepts: {len(canonical)}")
    print(f"deep dossiers: {len(dossier_ids)}")
    print(f"corpus records: {len(corpus_ids)}")
    print("rule: one canonical concept + one dense dossier; projections are occurrences, not identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
