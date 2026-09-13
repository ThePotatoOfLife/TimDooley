#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "atlas-constitution.json"


def validate(data: dict) -> list[str]:
    errors = []
    if data.get("schema_version") != "1.0.0": errors.append("schema_version")
    if data.get("root_id") != "potato-of-life": errors.append("root_id")
    if not {"node","relation","artifact","view"} <= set(data.get("object_roles", [])): errors.append("object_roles")
    north = data.get("north", {})
    if north.get("parent_cardinality") != "exactly_one_for_active_non_root": errors.append("north.parent_cardinality")
    if north.get("root_parent") is not None: errors.append("north.root_parent")
    if north.get("acyclic") is not True: errors.append("north.acyclic")
    if north.get("all_active_paths_terminate_at_root") is not True: errors.append("north.root_termination")
    if north.get("children_derived_from_parent") is not True: errors.append("north.children_derived")
    routes = data.get("routes", {})
    if routes.get("node") != "/atlas/{id}/": errors.append("routes.node")
    if not {"root","atlas","node","archive"} <= set(routes): errors.append("routes")
    if not {"active","candidate","legacy","archive_only"} <= set(data.get("migration_states", [])): errors.append("migration_states")
    web = data.get("web", {})
    if not {"site","page","record","archive","timeline","map","u"} <= set(web.get("css_namespaces", [])): errors.append("web.css_namespaces")
    if web.get("static_html_owns_meaning") is not True: errors.append("web.static_html_owns_meaning")
    if web.get("javascript_role") != "progressive_enhancement": errors.append("web.javascript_role")
    if web.get("validators_may_mutate_output") is not False: errors.append("web.validators_may_mutate_output")
    firewall = set(data.get("epistemic_firewall", []))
    needed = {"project_canon_not_empirical_fact","analogy_not_identity","comparison_not_transmission","symbolic_mapping_not_literal_science","altitude_not_truth_rank"}
    if not needed <= firewall: errors.append("epistemic_firewall")
    return errors


def main() -> int:
    if not PATH.exists():
        print("ATLAS CONSTITUTION VALIDATION FAILED: missing data/atlas-constitution.json")
        return 1
    try:
        data = json.loads(PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ATLAS CONSTITUTION VALIDATION FAILED: {exc}")
        return 1
    errors = validate(data)
    if errors:
        print("ATLAS CONSTITUTION VALIDATION FAILED: " + ", ".join(errors))
        return 1
    print(f"ATLAS CONSTITUTION VALIDATION PASSED: root={data['root_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
