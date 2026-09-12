#!/usr/bin/env python3
"""Evidence-first dependency graph helpers for the World Relational Atlas.

Dependency edges point from the dependent object to what it depends on.
Impact queries therefore traverse incoming explicit causal edges. Generic
connectivity, shared membership, and geographic association are not causality.
"""
from __future__ import annotations

import re
from collections import defaultdict
from copy import deepcopy

DEPENDENCY_TYPES = {"depends-on", "dependency", "strategic-dependency", "import-dependence", "depends_on"}
CAUSAL_STATUSES = {"explicit-dependency"}
IMPORTANCE_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def slug(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "unknown"


def importance_rank(value: object) -> int:
    return IMPORTANCE_ORDER.get(str(value or "").strip().lower(), 4)


def entity_node_id(code: str, canonical_country: bool = True) -> str:
    code = str(code or "").upper()
    return f"{'country' if canonical_country else 'territory'}:{code}"


def _dependency_sources(record: dict):
    yield record.get("dependencies")
    yield record.get("strategic_dependencies")
    yield (record.get("energy_and_resources") or {}).get("import_dependencies")
    yield (record.get("trade_and_value_chains") or {}).get("critical_import_dependencies")


def _fact_from_item(item, source_code: str, ordinal: int) -> dict | None:
    if isinstance(item, (str, int, float)):
        label = str(item).strip()
        if not label:
            return None
        return {"dependency": label, "source_code": source_code, "ordinal": ordinal}
    if not isinstance(item, dict):
        return None
    label = str(item.get("dependency") or item.get("target") or item.get("counterparty") or item.get("label") or "").strip()
    if not label:
        return None
    fact = {"dependency": label, "source_code": source_code, "ordinal": ordinal}
    explicit_code = item.get("code") or item.get("iso3") or item.get("target_code") or item.get("target_iso3")
    if explicit_code:
        fact["target_code"] = str(explicit_code).upper()
    for key in ("mechanism", "importance", "source", "source_url", "confidence"):
        if item.get(key) not in (None, ""):
            fact[key] = item.get(key)
    period = item.get("reference_period") or item.get("period") or item.get("year")
    if period not in (None, ""):
        fact["period"] = period
    return fact


def structured_dependency_facts(record: dict, source_code: str) -> list[dict]:
    """Return explicit dependency facts without guessing unresolved targets."""
    source_code = str(source_code or "").upper()
    facts: list[dict] = []
    ordinal = 0
    for values in _dependency_sources(record):
        if not isinstance(values, list):
            continue
        for item in values:
            ordinal += 1
            fact = _fact_from_item(item, source_code, ordinal)
            if fact:
                facts.append(fact)

    for relation in record.get("relationships", []) or []:
        if not isinstance(relation, dict):
            continue
        relation_type = str(relation.get("type") or relation.get("relationship") or "").strip().lower()
        if relation_type not in DEPENDENCY_TYPES:
            continue
        ordinal += 1
        fact = _fact_from_item(relation, source_code, ordinal)
        if fact:
            fact["relationship_type"] = relation_type
            facts.append(fact)

    # Preserve first occurrence and merge richer metadata from later duplicate labels.
    by_label: dict[str, dict] = {}
    order: list[str] = []
    for fact in facts:
        key = fact["dependency"].casefold()
        if key not in by_label:
            by_label[key] = fact
            order.append(key)
            continue
        current = by_label[key]
        for field, value in fact.items():
            if field not in current and value not in (None, ""):
                current[field] = value
    return [by_label[key] for key in order]


def dependency_labels(record: dict) -> list[str]:
    """Compact labels for the existing System role card, including object records."""
    return [fact["dependency"].replace("-", " ") for fact in structured_dependency_facts(record, "")][:12]


def _exact_lookup(country_rows: list[dict], entities: dict, gateways: dict, chains: dict) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for row in country_rows:
        code = str(row.get("iso3") or "").upper()
        name = str(row.get("name") or "").strip()
        if not code:
            continue
        node_id = entity_node_id(code, True)
        lookup[code.casefold()] = node_id
        if name:
            lookup[name.casefold()] = node_id
    for code, entity in entities.items():
        code = str(code).upper()
        node_id = entity_node_id(code, False)
        lookup[code.casefold()] = node_id
        name = str((entity or {}).get("name") or "").strip()
        if name:
            lookup[name.casefold()] = node_id
    for gateway_id, gateway in gateways.items():
        node_id = f"gateway:{gateway_id}"
        lookup[str(gateway_id).casefold()] = node_id
        label = str((gateway or {}).get("label") or "").strip()
        if label:
            lookup[label.casefold()] = node_id
    for chain_id, chain in chains.items():
        node_id = f"chain:{chain_id}"
        lookup[str(chain_id).casefold()] = node_id
        label = str((chain or {}).get("label") or "").strip()
        if label:
            lookup[label.casefold()] = node_id
    return lookup


def _resolve_dependency_target(fact: dict, source_node_id: str, lookup: dict[str, str]) -> tuple[str, dict | None]:
    explicit_code = str(fact.get("target_code") or "").strip().casefold()
    if explicit_code and explicit_code in lookup:
        return lookup[explicit_code], None
    label = str(fact.get("dependency") or "").strip()
    exact = lookup.get(label.casefold())
    if exact:
        return exact, None
    source_token = source_node_id.split(":", 1)[-1].lower()
    node_id = f"dependency:{source_token}:{slug(label)}"
    return node_id, {"id": node_id, "kind": "dependency-concept", "label": label, "owner": source_node_id}


def build_impact_plane(
    country_rows: list[dict],
    country_records: dict[str, dict],
    entities: dict,
    gateways: dict,
    chains: dict,
) -> dict:
    """Build one generated impact plane from canonical owners."""
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    context_chains: dict[str, list[str]] = {}

    for row in country_rows:
        code = str(row.get("iso3") or "").upper()
        if not code:
            continue
        node_id = entity_node_id(code, True)
        nodes[node_id] = {"id": node_id, "kind": "country", "code": code, "label": row.get("name") or code}

    for code, entity in entities.items():
        code = str(code).upper()
        node_id = entity_node_id(code, False)
        nodes[node_id] = {
            "id": node_id,
            "kind": "territory",
            "code": code,
            "label": (entity or {}).get("name") or code,
            "render_status": (entity or {}).get("render_status"),
        }

    for gateway_id, gateway in gateways.items():
        node_id = f"gateway:{gateway_id}"
        nodes[node_id] = {
            "id": node_id,
            "kind": "gateway",
            "gateway_id": gateway_id,
            "label": gateway.get("label") or gateway_id,
            "gateway_type": gateway.get("type"),
            "coordinates": deepcopy(gateway.get("coordinates")),
        }

    for chain_id, chain in chains.items():
        node_id = f"chain:{chain_id}"
        nodes[node_id] = {
            "id": node_id,
            "kind": "functional-chain",
            "chain_id": chain_id,
            "label": chain.get("label") or chain_id,
            "epistemic_type": chain.get("epistemic_type"),
        }

    lookup = _exact_lookup(country_rows, entities, gateways, chains)

    for row in country_rows:
        code = str(row.get("iso3") or "").upper()
        if not code:
            continue
        source_id = entity_node_id(code, True)
        record = country_records.get(code) or {}
        for fact in structured_dependency_facts(record, code):
            target_id, concept = _resolve_dependency_target(fact, source_id, lookup)
            if concept:
                nodes.setdefault(target_id, concept)
            edge = {
                "source": source_id,
                "target": target_id,
                "relationship": "depends-on",
                "causal_status": "explicit-dependency",
                "evidence_class": "canonical-country-record",
            }
            for key in ("mechanism", "importance", "source", "source_url", "period", "confidence"):
                if fact.get(key) not in (None, ""):
                    edge[key] = fact[key]
            edges.append(edge)

    # Context only: chain membership explains affected objects but never causes impact.
    for chain_id, chain in chains.items():
        chain_node = f"chain:{chain_id}"
        for code in chain.get("members") or []:
            code = str(code).upper()
            member_id = entity_node_id(code, code not in entities)
            if member_id in nodes:
                context_chains.setdefault(member_id, []).append(chain_node)

    # Explicit alternatives are represented separately and never traversed as affected nodes.
    for gateway_id, gateway in gateways.items():
        source_id = f"gateway:{gateway_id}"
        for alternative in gateway.get("alternatives") or []:
            if not isinstance(alternative, dict):
                continue
            target = str(alternative.get("target") or "").strip()
            target_id = f"gateway:{target}"
            if not target or target_id not in nodes:
                continue
            edge = {
                "source": source_id,
                "target": target_id,
                "relationship": alternative.get("relationship") or "alternative-route",
                "causal_status": "explicit-alternative",
                "evidence_class": "gateway-owner",
            }
            for key in ("status", "note", "source", "source_url"):
                if alternative.get(key) not in (None, ""):
                    edge[key] = alternative[key]
            edges.append(edge)

    for node_id, chain_ids in list(context_chains.items()):
        context_chains[node_id] = sorted(set(chain_ids))

    return {
        "version": "1.0.0",
        "policy": {
            "max_browser_depth": 2,
            "score_policy": "no aggregate impact score inferred",
            "missing_policy": "not represented is not no dependency",
            "causal_policy": "generic connectivity, membership and association are not dependency",
        },
        "nodes": nodes,
        "edges": edges,
        "context_chains": context_chains,
    }


def _sort_rows(rows: list[dict]) -> list[dict]:
    return sorted(
        rows,
        key=lambda row: (
            importance_rank((row.get("edge") or {}).get("importance")),
            str((row.get("node") or {}).get("label") or (row.get("node") or {}).get("id") or "").casefold(),
            str((row.get("node") or {}).get("id") or ""),
        ),
    )


def trace_incoming_impact(nodes: dict, edges: list[dict], root_id: str, max_depth: int = 2) -> dict:
    """Return direct and second-order dependents using explicit causal edges only."""
    if root_id not in nodes:
        return {"root": None, "direct": [], "second_order": []}
    depth = min(max(int(max_depth or 0), 0), 2)
    incoming: dict[str, list[dict]] = defaultdict(list)
    for edge in edges:
        if edge.get("causal_status") not in CAUSAL_STATUSES:
            continue
        source = edge.get("source")
        target = edge.get("target")
        if source in nodes and target in nodes:
            incoming[target].append(edge)

    direct: list[dict] = []
    direct_ids: set[str] = set()
    if depth >= 1:
        for edge in incoming.get(root_id, []):
            source = edge["source"]
            if source == root_id or source in direct_ids:
                continue
            direct_ids.add(source)
            direct.append({"node": nodes[source], "edge": deepcopy(edge)})

    second: list[dict] = []
    second_ids: set[str] = set()
    if depth >= 2:
        for direct_row in direct:
            via = direct_row["node"]["id"]
            for edge in incoming.get(via, []):
                source = edge["source"]
                if source == root_id or source in direct_ids or source in second_ids:
                    continue
                second_ids.add(source)
                second.append({"node": nodes[source], "edge": deepcopy(edge), "via": via})

    return {"root": nodes[root_id], "direct": _sort_rows(direct), "second_order": _sort_rows(second)}
