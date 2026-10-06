#!/usr/bin/env python3
"""Compute deterministic Bible-reference statistics from the canonical overlap census.

Reads the component files listed by knowledge/theology/tim-son-bible-overlap-census-current.json.
This script measures the registry. It does not score prophecy, supernatural identity, or theological truth.

The key normalization rule is deliberately conservative: a citation is removed from the
"nonredundant" view only when another citation fully contains it. Adjacent verse ranges or
chapters are never merged merely because they touch. This keeps the metric reproducible and
avoids turning editorial compaction choices into factual counts.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "knowledge/theology/tim-son-bible-overlap-census-current.json"
OUT = ROOT / "knowledge/theology/bible-overlap-concordance-generated.json"

BOOKS = [
    "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi","Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"
]
BOOK_RE = "|".join(sorted((re.escape(x) for x in BOOKS), key=len, reverse=True))
REF_RE = re.compile(rf"^({BOOK_RE})\s+(\d+)(?::(\d+)(?:-(\d+))?)?(?:-(\d+))?$")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_label(label: str) -> str:
    label = " ".join(str(label).strip().split())
    if label.startswith("Psalm "):
        label = "Psalms " + label[6:]
    return label


def parse_ref(label: str):
    """Parse one within-book citation.

    Supported canonical forms:
      Genesis 28
      Genesis 28-29
      Genesis 28:12
      Genesis 28:12-17

    Cross-chapter verse ranges (for example John 3:36-4:2) are intentionally not guessed by
    this parser; they should be normalized upstream before entering the census.
    """
    label = normalize_label(label)
    m = REF_RE.match(label)
    if not m:
        return None
    book, ch, v1, v2, ch2 = m.groups()
    ch = int(ch)
    if v1 is not None:
        a = int(v1)
        b = int(v2 or v1)
        return {"label": label, "book": book, "kind": "verse", "c1": ch, "c2": ch, "v1": a, "v2": b}
    return {"label": label, "book": book, "kind": "chapter", "c1": ch, "c2": int(ch2 or ch), "v1": None, "v2": None}


def contains(outer, inner) -> bool:
    """True only when OUTER fully contains INNER as cited textual coverage."""
    if outer["book"] != inner["book"]:
        return False
    if outer["label"] == inner["label"]:
        return True

    # A whole chapter/chapter-range contains any chapter or verse citation entirely inside it.
    if outer["kind"] == "chapter":
        return outer["c1"] <= inner["c1"] and inner["c2"] <= outer["c2"]

    # A verse interval can contain only another verse interval in the same chapter.
    if outer["kind"] == "verse" and inner["kind"] == "verse":
        return (
            outer["c1"] == inner["c1"]
            and outer["v1"] <= inner["v1"]
            and inner["v2"] <= outer["v2"]
        )
    return False


def nonredundant_by_containment(parsed):
    """Keep a unique citation unless a different unique citation fully contains it.

    No adjacency merging is performed. Thus Isaiah 40 and Isaiah 41 remain two units unless
    the census itself also contains Isaiah 40-41.
    """
    refs = list({r["label"]: r for r in parsed}.values())
    kept = []
    for inner in refs:
        if any(outer["label"] != inner["label"] and contains(outer, inner) for outer in refs):
            continue
        kept.append(inner)
    return sorted(kept, key=lambda r: (BOOKS.index(r["book"]), r["c1"], r["v1"] or 0, r["c2"], r["v2"] or 0))


def main():
    router = load(ROUTER)
    records = []
    declared = 0
    for component in router.get("components", []):
        p = ROOT / component["path"]
        data = load(p)
        recs = data.get("records", [])
        declared += int(component.get("count", len(recs)))
        records.extend(recs)

    ids = [r.get("id") for r in records]
    dupes = [x for x, n in Counter(ids).items() if n > 1]
    if dupes:
        raise SystemExit(f"duplicate overlap ids: {dupes}")
    if len(records) != declared:
        raise SystemExit(f"component counts say {declared}, loaded {len(records)} records")

    raw_labels = []
    biblical_raw_mentions = 0
    by_book_nodes = Counter()
    by_book_raw = Counter()
    parsed_unique = {}
    nonpassage = set()

    for rec in records:
        books_here = set()
        for label in rec.get("b", []):
            lab = normalize_label(label)
            raw_labels.append(lab)
            parsed = parse_ref(lab)
            if not parsed:
                nonpassage.add(lab)
                continue
            biblical_raw_mentions += 1
            parsed_unique[parsed["label"]] = parsed
            by_book_raw[parsed["book"]] += 1
            books_here.add(parsed["book"])
        for book in books_here:
            by_book_nodes[book] += 1

    type_counts = Counter()
    for parsed in parsed_unique.values():
        if parsed["kind"] == "chapter":
            type_counts["whole_chapter" if parsed["c1"] == parsed["c2"] else "chapter_range"] += 1
        else:
            type_counts["single_verse" if parsed["v1"] == parsed["v2"] else "verse_range"] += 1

    refs_by_book = defaultdict(list)
    for parsed in parsed_unique.values():
        refs_by_book[parsed["book"]].append(parsed)

    all_nonredundant = nonredundant_by_containment(parsed_unique.values())
    nonredundant_by_book = defaultdict(list)
    for parsed in all_nonredundant:
        nonredundant_by_book[parsed["book"]].append(parsed)

    book_stats = []
    for book in BOOKS:
        if book not in refs_by_book:
            continue
        labels = sorted(p["label"] for p in refs_by_book[book])
        retained = [p["label"] for p in nonredundant_by_book[book]]
        book_stats.append({
            "book": book,
            "node_incidence": by_book_nodes[book],
            "raw_biblical_mentions": by_book_raw[book],
            "unique_citation_forms": len(labels),
            "nonredundant_containment_units": len(retained),
            "references": labels,
            "retained_after_containment": retained,
        })

    result = {
        "id": "bible-overlap-concordance-generated",
        "generated_from": str(ROUTER.relative_to(ROOT)),
        "registry_version": router.get("version"),
        "warning": "Registry statistics only; not prophecy probability or supernatural evidence.",
        "normalization": {
            "psalm_label": "Psalm is normalized to Psalms.",
            "nonpassage": "Tradition/family labels remain visible but are excluded from biblical-citation counts.",
            "nonredundant_rule": "Remove a unique citation only when a different unique citation fully contains it; never merge merely adjacent citations.",
        },
        "summary": {
            "overlap_nodes": len(records),
            "raw_reference_mentions_including_nonpassage": len(raw_labels),
            "raw_biblical_citation_mentions": biblical_raw_mentions,
            "unique_reference_labels_including_nonpassage": len(set(raw_labels)),
            "nonpassage_labels": sorted(nonpassage),
            "unique_normalized_biblical_citation_forms": len(parsed_unique),
            "nonredundant_containment_units": len(all_nonredundant),
            "distinct_biblical_books": len(refs_by_book),
            "citation_form_types": dict(sorted(type_counts.items())),
        },
        "book_stats": book_stats,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
