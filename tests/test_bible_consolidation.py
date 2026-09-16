from __future__ import annotations

import copy
import random

from scripts.bible_consolidation import (
    build_duplicate_queue,
    build_families,
    classify_pair,
    fingerprint_relation,
)


def make_relation(
    rid: str,
    refs: list[str],
    *,
    anchor: str,
    bible_sequence: list[str] | None = None,
    project_sequence: list[str] | None = None,
    maximum_claim: str = "",
    boundary: str = "",
    counter_text: str = "",
    source_owners: list[str] | None = None,
    motifs: list[str] | None = None,
    operators: list[str] | None = None,
) -> dict:
    row = {
        "id": rid,
        "project_anchor": anchor,
        "biblical_refs": refs,
        "source_direction": "project-first comparator",
        "source_owners": source_owners or [f"knowledge/{rid}.json"],
        "relation_argument": {
            "project_sequence": project_sequence or [anchor],
            "biblical_sequence": bible_sequence or [],
            "maximum_claim": maximum_claim,
            "why_it_matters": anchor,
        },
    }
    if boundary:
        row["boundary"] = boundary
    if counter_text:
        row["counter_text"] = counter_text
    if motifs:
        row["motifs"] = motifs
    if operators:
        row["operators"] = operators
    return row


def test_fingerprint_is_deterministic_and_non_destructive():
    row = {
        "id": "sample",
        "project_anchor": " Door / Gate  access ",
        "biblical_refs": ["Revelation 3:20", "John 10:9"],
        "source_owners": ["b.json", "a.json"],
        "relation_argument": {
            "project_sequence": ["door", "entry"],
            "biblical_sequence": ["knock", "open", "meal"],
            "maximum_claim": "A bounded claim.",
        },
    }
    before = copy.deepcopy(row)
    fp = fingerprint_relation(row)
    assert row == before
    assert fp["relation_id"] == "sample"
    assert fp["biblical_refs"] == ["john 10:9", "revelation 3:20"]
    assert fp["source_owners"] == ["a.json", "b.json"]
    assert fp == fingerprint_relation(copy.deepcopy(row))


def test_same_passage_same_function_is_duplicate_candidate():
    left = make_relation(
        "root-a",
        ["Romans 11:17-18"],
        anchor="root supports branches and branches must not boast",
        bible_sequence=["root supports branches", "branches warned not to boast"],
        maximum_claim="Root support and anti-boasting belong together.",
        motifs=["root", "branches", "anti-boasting"],
    )
    right = make_relation(
        "root-b",
        ["Romans 11:17-18"],
        anchor="branches depend on root with an anti-boasting warning",
        bible_sequence=["root supports branches", "branches warned not to boast"],
        maximum_claim="Root support and anti-boasting belong together.",
        motifs=["root", "branches", "anti-boasting"],
    )
    result = classify_pair(fingerprint_relation(left), fingerprint_relation(right))
    assert result["classification"] == "duplicate_candidate"
    assert "same_scripture" in result["reasons"]


def test_yoke_reversal_is_contrast_not_duplicate():
    learning = make_relation(
        "teaching-yoke",
        ["Matthew 11:28-30"],
        anchor="yoke can teach and give rest",
        bible_sequence=["take yoke", "learn", "find rest"],
        boundary="not slavery",
        motifs=["yoke", "rest", "learning"],
    )
    slavery = make_relation(
        "slavery-yoke",
        ["Galatians 5:1"],
        anchor="yoke can suppress freedom",
        bible_sequence=["freedom", "yoke of slavery"],
        boundary="not every obligation is slavery",
        motifs=["yoke", "slavery", "freedom"],
    )
    result = classify_pair(fingerprint_relation(learning), fingerprint_relation(slavery))
    assert result["classification"] == "contrast_candidate"


def test_shared_generic_word_alone_is_unrelated():
    left = make_relation(
        "house-a",
        ["John 14:2"],
        anchor="house contains rooms",
        bible_sequence=["house", "rooms"],
    )
    right = make_relation(
        "house-b",
        ["Joshua 2:15"],
        anchor="house is located in a city wall",
        bible_sequence=["window", "wall", "escape"],
    )
    result = classify_pair(fingerprint_relation(left), fingerprint_relation(right))
    assert result["classification"] == "unrelated"


def test_family_and_representative_are_order_stable():
    rows = [
        make_relation(
            "mountain-revelation",
            ["Exodus 19:20"],
            anchor="mountain revelation with guarded ascent",
            bible_sequence=["boundary", "ascent", "revelation", "descent"],
            motifs=["mountain", "ascent", "revelation"],
        ),
        make_relation(
            "mountain-assembly",
            ["Hebrews 12:22"],
            anchor="mountain city assembly and access",
            bible_sequence=["zion", "city", "assembly"],
            motifs=["mountain", "city", "assembly"],
        ),
        make_relation(
            "mountain-temptation",
            ["Matthew 4:8-10"],
            anchor="high mountain becomes temptation to possession",
            bible_sequence=["high mountain", "kingdoms shown", "power offered", "refusal"],
            boundary="height does not confer rightful possession",
            motifs=["mountain", "kingdoms", "temptation"],
        ),
    ]
    first = build_families(rows)
    shuffled = rows[:]
    random.Random(7).shuffle(shuffled)
    second = build_families(shuffled)
    assert first == second
    assert len(first) == 1
    assert set(first[0]["member_relation_ids"]) == {r["id"] for r in rows}
    assert "mountain-temptation" in first[0]["contrast_relation_ids"]


def test_duplicate_queue_preserves_unique_evidence():
    left = make_relation(
        "root-a",
        ["Romans 11:17-18"],
        anchor="root supports branches and anti-boasting",
        bible_sequence=["root supports branches", "do not boast"],
        maximum_claim="Root supports branches.",
        boundary="Do not boast.",
        source_owners=["primary-a.json"],
        motifs=["root", "branches"],
    )
    right = make_relation(
        "root-b",
        ["Romans 11:17-18"],
        anchor="branches depend on root and should not boast",
        bible_sequence=["root supports branches", "do not boast"],
        maximum_claim="Root supports branches.",
        counter_text="Branches can be removed.",
        source_owners=["primary-b.json"],
        motifs=["root", "branches"],
    )
    fps = {r["id"]: fingerprint_relation(r) for r in [left, right]}
    pair = classify_pair(fps["root-a"], fps["root-b"])
    queue = build_duplicate_queue([left, right], fps, [pair])
    assert len(queue) == 1
    item = queue[0]
    assert item["unique_evidence"]["root-a"]
    assert item["unique_evidence"]["root-b"]
    assert item["requires_evidence_migration"] is True
    assert item["suggested_action"] == "enrich_existing"
