#!/usr/bin/env python3
"""Deterministic, non-destructive consolidation helpers for the Bible comparator.

The module derives indexes over canonical relations. It never mutates, deletes,
renames, or strengthens the underlying relation records.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import re
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from",
    "in", "into", "is", "it", "later", "not", "of", "on", "or", "project",
    "than", "that", "the", "their", "this", "to", "with",
}
FAMILY_SYMBOLS = {
    "mountain", "valley", "door", "gate", "stone", "yoke", "cord", "root",
    "branch", "branches", "garden", "farm", "temple", "city", "seed", "tree",
    "dog", "cube", "river", "bread", "debt", "release", "anchor", "wheel",
    "grain", "field", "vine", "shepherd", "path", "road", "house",
}
NEGATIVE_CUES = {
    "barrier", "blocked", "confinement", "enslaving", "enslaved", "slavery",
    "temptation", "possession", "obstruction", "obstacle", "judgment", "downward",
    "danger", "predatory", "exclusion", "closed", "harm",
}
POSITIVE_CUES = {
    "access", "invitation", "open", "opening", "rest", "learning", "guidance",
    "revelation", "assembly", "circulation", "foundation", "cornerstone", "repair",
    "healing", "return", "release", "freedom", "support", "growth", "life",
}


def _arr(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def norm_text(value: object) -> str:
    return " ".join(TOKEN_RE.findall(str(value or "").lower()))


def normalize_ref(value: str) -> str:
    return re.sub(
        r"\s+", " ",
        str(value or "").strip().lower().replace("–", "-").replace("—", "-"),
    )


def _tokens(value: object) -> set[str]:
    return {tok for tok in TOKEN_RE.findall(str(value or "").lower()) if tok not in STOPWORDS}


def _sequence_tokens(values: Any) -> set[str]:
    out: set[str] = set()
    for value in _arr(values):
        out.update(_tokens(value))
    return out


def _sorted_strings(values: Any, *, refs: bool = False) -> list[str]:
    normalizer = normalize_ref if refs else lambda x: str(x).strip()
    return sorted({normalizer(v) for v in _arr(values) if str(v).strip()})


def fingerprint_relation(row: dict, assessment: dict | None = None) -> dict:
    """Return a stable normalized projection without mutating *row*."""
    argument = row.get("relation_argument") or {}
    discovery = row.get("discovery_history") or {}
    motifs = _sorted_strings(row.get("motifs"))
    operators = _sorted_strings(row.get("operators"))
    scenes = _sorted_strings(row.get("biblical_scene_ids"))
    anchor_tokens = _tokens(row.get("project_anchor"))
    project_sequence_tokens = _sequence_tokens(argument.get("project_sequence") or row.get("project_sequence"))
    bible_sequence_tokens = _sequence_tokens(argument.get("biblical_sequence") or row.get("biblical_sequence"))
    max_claim = argument.get("maximum_claim") or row.get("maximum_claim") or ""
    boundary_parts = [
        row.get("boundary"), row.get("mismatch"), row.get("counter_text"),
        row.get("difference"), *_arr(row.get("weaknesses")),
    ]
    boundary_text = " ".join(str(x) for x in boundary_parts if x)
    all_text = " ".join(
        str(x)
        for x in [
            row.get("id"), row.get("project_anchor"), max_claim, boundary_text,
            *motifs, *operators,
            *_arr(argument.get("project_sequence")),
            *_arr(argument.get("biblical_sequence")),
        ]
        if x
    )
    explicit_symbols = (
        anchor_tokens
        | _tokens(row.get("id"))
        | set().union(*(_tokens(x) for x in motifs)) if motifs else anchor_tokens | _tokens(row.get("id"))
    ) & FAMILY_SYMBOLS
    return {
        "relation_id": str(row.get("id") or ""),
        "biblical_refs": _sorted_strings(row.get("biblical_refs"), refs=True),
        "source_owners": _sorted_strings(row.get("source_owners") or row.get("source_refs")),
        "scene_ids": scenes,
        "motifs": [norm_text(x) for x in motifs],
        "operators": [norm_text(x) for x in operators],
        "explicit_symbols": sorted(explicit_symbols),
        "anchor_tokens": sorted(anchor_tokens),
        "project_sequence_tokens": sorted(project_sequence_tokens),
        "biblical_sequence_tokens": sorted(bible_sequence_tokens),
        "maximum_claim_tokens": sorted(_tokens(max_claim)),
        "boundary_tokens": sorted(_tokens(boundary_text)),
        "all_tokens": sorted(_tokens(all_text)),
        "source_direction": norm_text(discovery.get("source_direction") or row.get("source_direction")),
        "has_boundary": bool(boundary_text.strip()),
        "has_maximum_claim": bool(str(max_claim).strip()),
        "excavation_level": int((assessment or {}).get("level", 0) or 0),
    }


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _explicit_symbols(fp: dict) -> set[str]:
    return set(fp.get("explicit_symbols", []))


def _contrast_signal(left: dict, right: dict, shared_symbols: set[str]) -> bool:
    if not shared_symbols:
        return False
    lt = set(left.get("all_tokens", [])) | set(left.get("boundary_tokens", []))
    rt = set(right.get("all_tokens", [])) | set(right.get("boundary_tokens", []))
    left_neg, right_neg = bool(lt & NEGATIVE_CUES), bool(rt & NEGATIVE_CUES)
    left_pos, right_pos = bool(lt & POSITIVE_CUES), bool(rt & POSITIVE_CUES)
    return (left_neg and right_pos) or (right_neg and left_pos)


def classify_pair(left: dict, right: dict) -> dict:
    """Classify two relation fingerprints using explainable staged evidence."""
    lid, rid = sorted([left["relation_id"], right["relation_id"]])
    refs_l, refs_r = set(left.get("biblical_refs", [])), set(right.get("biblical_refs", []))
    same_scripture = bool(refs_l) and refs_l == refs_r
    shared_scripture = sorted(refs_l & refs_r)
    shared_scenes = sorted(set(left.get("scene_ids", [])) & set(right.get("scene_ids", [])))
    shared_owners = sorted(set(left.get("source_owners", [])) & set(right.get("source_owners", [])))
    anchor_sim = _jaccard(set(left.get("anchor_tokens", [])), set(right.get("anchor_tokens", [])))
    bible_sim = _jaccard(set(left.get("biblical_sequence_tokens", [])), set(right.get("biblical_sequence_tokens", [])))
    project_sim = _jaccard(set(left.get("project_sequence_tokens", [])), set(right.get("project_sequence_tokens", [])))
    claim_sim = _jaccard(set(left.get("maximum_claim_tokens", [])), set(right.get("maximum_claim_tokens", [])))
    shared_symbols = _explicit_symbols(left) & _explicit_symbols(right)
    shared_operators = sorted(set(left.get("operators", [])) & set(right.get("operators", [])))

    reasons: list[str] = []
    classification = "unrelated"
    strong_equivalence = same_scripture and (
        (bible_sim >= 0.55 and claim_sim >= 0.45)
        or (bible_sim >= 0.75 and anchor_sim >= 0.30)
        or (anchor_sim >= 0.45 and claim_sim >= 0.45 and project_sim >= 0.45)
    )
    corroborated_symbol = bool(shared_symbols) and bool(
        shared_owners
        or shared_scenes
        or shared_operators
        or anchor_sim >= 0.16
        or bible_sim >= 0.20
        or project_sim >= 0.20
        or shared_scripture
    )

    # Strong equivalence outranks incidental polarity vocabulary.
    if strong_equivalence:
        classification = "duplicate_candidate"
        reasons.append("same_scripture")
        if bible_sim >= 0.55:
            reasons.append("same_biblical_sequence")
        if anchor_sim >= 0.45:
            reasons.append("same_project_function")
        if claim_sim >= 0.45:
            reasons.append("same_maximum_claim")
    elif corroborated_symbol and _contrast_signal(left, right, shared_symbols):
        classification = "contrast_candidate"
        reasons.extend(["shared_symbol", "opposing_function_cues"])
        if shared_owners:
            reasons.append("shared_source_owner")
    elif same_scripture and (
        bible_sim >= 0.55
        or (anchor_sim >= 0.45 and claim_sim >= 0.45)
        or (anchor_sim >= 0.45 and project_sim >= 0.45)
    ):
        classification = "duplicate_candidate"
        reasons.append("same_scripture")
        if bible_sim >= 0.55:
            reasons.append("same_biblical_sequence")
        if anchor_sim >= 0.45:
            reasons.append("same_project_function")
        if claim_sim >= 0.45:
            reasons.append("same_maximum_claim")
    elif (
        (shared_scripture and (anchor_sim >= 0.25 or bible_sim >= 0.25 or project_sim >= 0.25))
        or (shared_scenes and (anchor_sim >= 0.20 or bible_sim >= 0.20))
        or corroborated_symbol
    ):
        classification = "overlap_candidate"
        if shared_scripture:
            reasons.append("shared_scripture")
        if shared_scenes:
            reasons.append("shared_scene")
        if shared_symbols:
            reasons.append("shared_symbol")
        if shared_operators:
            reasons.append("shared_operator")
        if shared_owners:
            reasons.append("shared_source_owner")

    return {
        "relation_ids": [lid, rid],
        "classification": classification,
        "reasons": sorted(set(reasons)),
        "shared": {
            "biblical_refs": shared_scripture,
            "scene_ids": shared_scenes,
            "source_owners": shared_owners,
            "symbols": sorted(shared_symbols),
            "operators": shared_operators,
        },
    }


def _quality_key(fp: dict) -> tuple:
    return (
        int(fp.get("excavation_level", 0)),
        int(bool(fp.get("source_owners"))),
        int(bool(fp.get("biblical_refs"))),
        int(bool(fp.get("biblical_sequence_tokens")) and bool(fp.get("project_sequence_tokens"))),
        int(bool(fp.get("has_boundary"))),
        int(bool(fp.get("has_maximum_claim"))),
        int(bool(fp.get("source_direction"))),
        len(fp.get("source_owners", [])),
        len(fp.get("biblical_refs", [])),
    )


def select_representative(member_ids: list[str], fingerprints: dict[str, dict]) -> str:
    return sorted(
        member_ids,
        key=lambda rid: tuple(-x for x in _quality_key(fingerprints[rid])) + (rid,),
    )[0]


def stable_family_id(member_ids: list[str], shared_terms: list[str] | None = None) -> str:
    basis = "|".join(sorted(member_ids)) + "||" + "|".join(sorted(shared_terms or []))
    return "family-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]


def _family_for_symbol(
    symbol: str,
    member_ids: list[str],
    rows_by_id: dict[str, dict],
    fps: dict[str, dict],
    pair_map: dict[tuple[str, str], dict],
) -> dict | None:
    linked: set[str] = set()
    edges: list[dict] = []
    for i, left_id in enumerate(member_ids):
        for right_id in member_ids[i + 1:]:
            pair = pair_map.get(tuple(sorted((left_id, right_id))))
            if not pair or pair["classification"] == "unrelated":
                continue
            if symbol not in pair.get("shared", {}).get("symbols", []):
                continue
            linked.update((left_id, right_id))
            edges.append(pair)
    if len(linked) < 2:
        return None
    members = sorted(linked)
    contrast_ids = sorted({rid for edge in edges if edge["classification"] == "contrast_candidate" for rid in edge["relation_ids"]})
    duplicate_ids = sorted({rid for edge in edges if edge["classification"] == "duplicate_candidate" for rid in edge["relation_ids"]})
    representative = select_representative(members, fps)
    source_owners = sorted({owner for rid in members for owner in fps[rid].get("source_owners", [])})
    ref_counts = Counter(ref for rid in members for ref in fps[rid].get("biblical_refs", []))
    shared_refs = sorted(ref for ref, count in ref_counts.items() if count >= 2)
    member_claims = {
        rid: str((rows_by_id[rid].get("relation_argument") or {}).get("maximum_claim") or rows_by_id[rid].get("maximum_claim") or "")
        for rid in members
    }
    functions = {
        rid: sorted((set(fps[rid].get("anchor_tokens", [])) | {symbol}) - STOPWORDS)[:10]
        for rid in members
    }
    return {
        "id": stable_family_id(members, [symbol]),
        "label": symbol.title(),
        "family_symbol": symbol,
        "member_relation_ids": members,
        "representative_relation_id": representative,
        "supporting_relation_ids": sorted(set(members) - set(contrast_ids)),
        "contrast_relation_ids": contrast_ids,
        "duplicate_candidate_relation_ids": duplicate_ids,
        "member_functions": functions,
        "shared_biblical_refs": shared_refs,
        "source_owners": source_owners,
        "member_maximum_claims": member_claims,
    }


def build_families(relations: list[dict], assessments: dict[str, dict] | None = None) -> list[dict]:
    """Build bounded per-symbol retrieval families over existing relations."""
    assessments = assessments or {}
    rows = sorted((row for row in relations if row.get("id")), key=lambda row: str(row["id"]))
    rows_by_id = {str(row["id"]): row for row in rows}
    fps = {rid: fingerprint_relation(row, assessments.get(rid)) for rid, row in rows_by_id.items()}
    pair_map: dict[tuple[str, str], dict] = {}
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            pair = classify_pair(fps[left["id"]], fps[right["id"]])
            pair_map[tuple(pair["relation_ids"])] = pair

    symbol_members: dict[str, list[str]] = defaultdict(list)
    for rid, fp in fps.items():
        for symbol in fp.get("explicit_symbols", []):
            symbol_members[symbol].append(rid)

    families: list[dict] = []
    for symbol in sorted(symbol_members):
        family = _family_for_symbol(
            symbol,
            sorted(symbol_members[symbol]),
            rows_by_id,
            fps,
            pair_map,
        )
        if family:
            families.append(family)
    return sorted(families, key=lambda family: family["id"])


def _evidence_fields(row: dict) -> dict[str, set[str]]:
    argument = row.get("relation_argument") or {}
    return {
        "source_owners": set(_sorted_strings(row.get("source_owners") or row.get("source_refs"))),
        "biblical_refs": set(_sorted_strings(row.get("biblical_refs"), refs=True)),
        "occurrence_ids": set(_sorted_strings(row.get("occurrence_ids"))),
        "boundary": {norm_text(row.get("boundary") or row.get("mismatch"))} - {""},
        "counter_text": {norm_text(row.get("counter_text"))} - {""},
        "project_sequence": {norm_text(x) for x in _arr(argument.get("project_sequence")) if norm_text(x)},
        "biblical_sequence": {norm_text(x) for x in _arr(argument.get("biblical_sequence")) if norm_text(x)},
        "maximum_claim": {norm_text(argument.get("maximum_claim") or row.get("maximum_claim"))} - {""},
    }


def unique_evidence(left: dict, right: dict) -> dict[str, dict[str, list[str]]]:
    le, re = _evidence_fields(left), _evidence_fields(right)
    out: dict[str, dict[str, list[str]]] = {str(left["id"]): {}, str(right["id"]): {}}
    for field in sorted(set(le) | set(re)):
        only_left = sorted(le.get(field, set()) - re.get(field, set()))
        only_right = sorted(re.get(field, set()) - le.get(field, set()))
        if only_left:
            out[str(left["id"])][field] = only_left
        if only_right:
            out[str(right["id"])][field] = only_right
    return out


def build_duplicate_queue(
    relations: list[dict],
    fingerprints: dict[str, dict],
    pair_results: list[dict],
) -> list[dict]:
    by_id = {str(row.get("id")): row for row in relations if row.get("id")}
    queue: list[dict] = []
    for pair in sorted(pair_results, key=lambda p: tuple(p.get("relation_ids", []))):
        if pair.get("classification") != "duplicate_candidate":
            continue
        left_id, right_id = pair["relation_ids"]
        if left_id not in by_id or right_id not in by_id:
            continue
        unique = unique_evidence(by_id[left_id], by_id[right_id])
        requires_migration = bool(unique[left_id] or unique[right_id])
        queue.append({
            "relation_ids": [left_id, right_id],
            "recommended_representative_id": select_representative([left_id, right_id], fingerprints),
            "reasons": pair.get("reasons", []),
            "unique_evidence": unique,
            "requires_evidence_migration": requires_migration,
            "suggested_action": "enrich_existing" if requires_migration else "alias",
        })
    return queue
