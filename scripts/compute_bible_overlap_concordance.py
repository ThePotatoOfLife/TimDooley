#!/usr/bin/env python3
"""Compute deterministic Bible-reference statistics from the canonical overlap census.

Reads the component files listed by knowledge/theology/tim-son-bible-overlap-census-current.json.
This script measures the registry. It does not score prophecy, supernatural identity, or theological truth.
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
BOOK_SET = set(BOOKS)
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
    label = normalize_label(label)
    m = REF_RE.match(label)
    if not m:
        return None
    book, ch, v1, v2, ch2 = m.groups()
    ch = int(ch)
    if v1 is not None:
        a = int(v1); b = int(v2 or v1)
        return {"label": label, "book": book, "kind": "verse", "c1": ch, "c2": ch, "v1": a, "v2": b}
    return {"label": label, "book": book, "kind": "chapter", "c1": ch, "c2": int(ch2 or ch), "v1": None, "v2": None}


def compact_book(parsed):
    """Return non-redundant chapter/verse coverage units for one book."""
    chapters = []
    verse_by_ch = defaultdict(list)
    for r in parsed:
        if r["kind"] == "chapter":
            chapters.append((r["c1"], r["c2"]))
        else:
            verse_by_ch[r["c1"]].append((r["v1"], r["v2"]))
    # merge overlapping or adjacent chapter ranges
    chapters.sort()
    merged_ch = []
    for a,b in chapters:
        if not merged_ch or a > merged_ch[-1][1] + 1:
            merged_ch.append([a,b])
        else:
            merged_ch[-1][1] = max(merged_ch[-1][1], b)
    def chapter_covered(ch): return any(a <= ch <= b for a,b in merged_ch)
    units = [{"kind":"chapter_range","start_chapter":a,"end_chapter":b} for a,b in merged_ch]
    for ch, intervals in sorted(verse_by_ch.items()):
        if chapter_covered(ch):
            continue
        intervals.sort(); merged=[]
        for a,b in intervals:
            if not merged or a > merged[-1][1] + 1:
                merged.append([a,b])
            else:
                merged[-1][1] = max(merged[-1][1], b)
        units.extend({"kind":"verse_range","chapter":ch,"start_verse":a,"end_verse":b} for a,b in merged)
    return units


def main():
    router = load(ROUTER)
    records=[]
    declared=0
    for component in router.get("components", []):
        p = ROOT / component["path"]
        data = load(p)
        recs = data.get("records", [])
        declared += int(component.get("count", len(recs)))
        records.extend(recs)
    ids=[r.get("id") for r in records]
    dupes=[x for x,n in Counter(ids).items() if n>1]
    if dupes:
        raise SystemExit(f"duplicate overlap ids: {dupes}")
    if len(records) != declared:
        raise SystemExit(f"component counts say {declared}, loaded {len(records)} records")

    raw=[]; by_book_nodes=Counter(); by_book_raw=Counter(); parsed_unique={}
    nonpassage=set(); type_counts=Counter()
    for rec in records:
        books_here=set()
        for label in rec.get("b", []):
            lab=normalize_label(label); raw.append(lab)
            p=parse_ref(lab)
            if not p:
                nonpassage.add(lab); continue
            parsed_unique[p["label"]]=p
            by_book_raw[p["book"]]+=1; books_here.add(p["book"])
            if p["kind"]=="verse": type_counts["single_verse" if p["v1"]==p["v2"] else "verse_range"]+=0
        for b in books_here: by_book_nodes[b]+=1
    # types are counts of unique citation forms, not raw mentions
    type_counts=Counter()
    for p in parsed_unique.values():
        if p["kind"]=="chapter": type_counts["whole_chapter" if p["c1"]==p["c2"] else "chapter_range"]+=1
        else: type_counts["single_verse" if p["v1"]==p["v2"] else "verse_range"]+=1

    refs_by_book=defaultdict(list)
    for p in parsed_unique.values(): refs_by_book[p["book"]].append(p)
    compact={b:compact_book(v) for b,v in refs_by_book.items()}
    compact_count=sum(map(len,compact.values()))
    book_stats=[]
    for b in BOOKS:
        if b not in refs_by_book: continue
        labels=sorted(p["label"] for p in refs_by_book[b])
        book_stats.append({
            "book":b,"node_incidence":by_book_nodes[b],"raw_mentions":by_book_raw[b],
            "unique_citation_forms":len(labels),"compact_coverage_units":len(compact[b]),"references":labels
        })

    result={
        "id":"bible-overlap-concordance-generated",
        "generated_from":str(ROUTER.relative_to(ROOT)),
        "warning":"Registry statistics only; not prophecy probability or supernatural evidence.",
        "summary":{
            "overlap_nodes":len(records),"raw_reference_mentions":len(raw),
            "unique_reference_labels_including_nonpassage":len(set(raw)),
            "nonpassage_labels":sorted(nonpassage),
            "unique_normalized_biblical_citation_forms":len(parsed_unique),
            "compact_nonredundant_coverage_units":compact_count,
            "distinct_biblical_books":len(refs_by_book),
            "citation_form_types":dict(type_counts)
        },
        "book_stats":book_stats
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],indent=2))

if __name__ == "__main__": main()
