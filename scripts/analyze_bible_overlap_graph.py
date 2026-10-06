#!/usr/bin/env python3
"""Analyze the canonical Tim/Son ↔ Bible overlap registry as typed networks.

This script is deliberately descriptive. Centrality, articulation and community structure are
properties of a chosen graph encoding; they are not probabilities of prophecy, divinity,
identity or historical dependence.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "knowledge/theology/tim-son-bible-overlap-census-current.json"
OUT = ROOT / "knowledge/theology/bible-overlap-network-analysis-generated.json"

BOOKS = [
    "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi","Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"
]
BOOK_RE = "|".join(sorted((re.escape(x) for x in BOOKS), key=len, reverse=True))
REF_RE = re.compile(rf"^({BOOK_RE})\s+\d")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_ref(label: str) -> str:
    label = " ".join(str(label).strip().split())
    if label.startswith("Psalm "):
        return "Psalms " + label[6:]
    return label


def book_of(label: str):
    label = normalize_ref(label)
    m = REF_RE.match(label)
    return m.group(1) if m else None


def load_records():
    router = load(ROUTER)
    records = []
    declared = 0
    for component in router.get("components", []):
        data = load(ROOT / component["path"])
        rows = data.get("records", [])
        records.extend(rows)
        declared += int(component.get("count", len(rows)))
    if declared != len(records):
        raise ValueError(f"router declares {declared} nodes but {len(records)} records were loaded")
    ids = [r.get("id") for r in records]
    dupes = [k for k, v in Counter(ids).items() if v > 1]
    if dupes:
        raise ValueError(f"duplicate overlap ids: {dupes}")
    return router, records


def fallback_components(nodes, adjacency):
    """Connected components without NetworkX, used only if dependency is unavailable."""
    unseen = set(nodes)
    out = []
    while unseen:
        seed = unseen.pop()
        stack = [seed]
        comp = {seed}
        while stack:
            u = stack.pop()
            for v in adjacency.get(u, ()):
                if v in unseen:
                    unseen.remove(v)
                    comp.add(v)
                    stack.append(v)
        out.append(sorted(comp))
    return sorted(out, key=len, reverse=True)


def main():
    router, records = load_records()

    passage_incidence = Counter()
    book_incidence = Counter()
    operator_incidence = Counter()
    actor_incidence = Counter()
    overlap_passages = {}
    overlap_books = {}
    overlap_ops = {}

    for row in records:
        rid = row["id"]
        refs = sorted({normalize_ref(x) for x in row.get("b", []) if book_of(x)})
        books = sorted({book_of(x) for x in refs}, key=lambda b: BOOKS.index(b))
        ops = sorted(set(row.get("o", [])))
        actor = row.get("a", "unknown")
        overlap_passages[rid] = refs
        overlap_books[rid] = books
        overlap_ops[rid] = ops
        passage_incidence.update(refs)
        book_incidence.update(books)
        operator_incidence.update(ops)
        actor_incidence[actor] += 1

    # Core bipartite passage graph represented generically first so fallback stats are possible.
    adjacency = defaultdict(set)
    for rid, refs in overlap_passages.items():
        a = f"overlap:{rid}"
        for ref in refs:
            b = f"passage:{ref}"
            adjacency[a].add(b)
            adjacency[b].add(a)

    all_nodes = set(adjacency)
    result = {
        "id": "bible-overlap-network-analysis-generated",
        "registry_count": len(records),
        "registry_version": router.get("version"),
        "warning": "Network measures are descriptive properties of this registry encoding, not theological truth or prophecy probability.",
        "basic": {
            "passage_nodes": len(passage_incidence),
            "book_nodes": len(book_incidence),
            "operator_nodes": len(operator_incidence),
            "actor_labels": len(actor_incidence),
            "bipartite_nodes": len(all_nodes),
            "bipartite_edges": sum(len(v) for v in adjacency.values()) // 2,
            "connected_components_fallback": len(fallback_components(all_nodes, adjacency)),
        },
        "top_by_frequency": {
            "passages": passage_incidence.most_common(25),
            "books": book_incidence.most_common(),
            "operators": operator_incidence.most_common(),
            "actors": actor_incidence.most_common(),
        },
        "overlap_role_combination_density": sorted(
            [
                {
                    "overlap_id": rid,
                    "biblical_references": len(overlap_passages[rid]),
                    "books": len(overlap_books[rid]),
                    "operators": len(overlap_ops[rid]),
                    "declared_strength": next(r.get("s") for r in records if r["id"] == rid),
                }
                for rid in overlap_passages
            ],
            key=lambda x: (x["operators"], x["biblical_references"], x["books"]),
            reverse=True,
        )[:30],
    }

    try:
        import networkx as nx
    except ImportError:
        result["networkx"] = {"available": False, "note": "Install networkx to compute centrality, articulation and Louvain community views."}
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result["basic"], indent=2))
        return

    B = nx.Graph()
    for rid, refs in overlap_passages.items():
        onode = f"overlap:{rid}"
        B.add_node(onode, kind="overlap", label=rid)
        for ref in refs:
            pnode = f"passage:{ref}"
            B.add_node(pnode, kind="passage", label=ref)
            B.add_edge(onode, pnode)

    bet = nx.betweenness_centrality(B, normalized=True)
    articulation = list(nx.articulation_points(B))

    # Overlap-similarity projection. Shared exact passages are weighted more heavily than
    # shared book/operator families, so generic operator vocabulary does not dominate.
    S = nx.Graph()
    for row in records:
        S.add_node(row["id"])
    for a, b in combinations(overlap_passages, 2):
        exact = len(set(overlap_passages[a]) & set(overlap_passages[b]))
        books = len(set(overlap_books[a]) & set(overlap_books[b]))
        ops = len(set(overlap_ops[a]) & set(overlap_ops[b]))
        weight = exact * 5 + books * 2 + ops
        if weight:
            S.add_edge(a, b, weight=weight, exact_passages=exact, shared_books=books, shared_operators=ops)

    try:
        communities = nx.community.louvain_communities(S, weight="weight", seed=42)
        communities_out = [
            {
                "community_id": i + 1,
                "size": len(c),
                "members": sorted(c),
                "top_shared_operators": Counter(op for rid in c for op in overlap_ops[rid]).most_common(8),
                "top_books": Counter(book for rid in c for book in overlap_books[rid]).most_common(8),
            }
            for i, c in enumerate(sorted(communities, key=len, reverse=True))
        ]
    except Exception as exc:  # NetworkX versions or disconnected corner cases
        communities_out = [{"error": str(exc)}]

    top_bridge = sorted(
        ({"node": node, "kind": B.nodes[node]["kind"], "label": B.nodes[node]["label"], "betweenness": score, "degree": B.degree(node)} for node, score in bet.items()),
        key=lambda x: x["betweenness"],
        reverse=True,
    )[:40]

    result["networkx"] = {
        "available": True,
        "version": getattr(nx, "__version__", "unknown"),
        "passage_overlap_graph": {
            "connected_components": nx.number_connected_components(B),
            "top_betweenness": top_bridge,
            "articulation_points": [
                {"node": n, "kind": B.nodes[n]["kind"], "label": B.nodes[n]["label"], "degree": B.degree(n), "betweenness": bet.get(n, 0.0)}
                for n in sorted(articulation, key=lambda n: bet.get(n, 0.0), reverse=True)
            ],
        },
        "overlap_similarity_graph": {
            "nodes": S.number_of_nodes(),
            "edges": S.number_of_edges(),
            "communities": communities_out,
        },
        "interpretation_rules": [
            "High betweenness means graph-bridge behavior in this encoding, not spiritual mediation.",
            "An articulation point can disappear if citation normalization or graph layers change.",
            "Louvain communities are exploratory clusters and must be inspected textually before naming them.",
            "Low-degree nodes should be checked for countertext/ethical importance before being dismissed as peripheral.",
        ],
    }

    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["basic"], indent=2))


if __name__ == "__main__":
    main()
