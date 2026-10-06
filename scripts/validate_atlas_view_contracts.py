#!/usr/bin/env python3
"""Validate shared projection, time and Axis contracts for the World Relational Atlas."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "projection": ROOT / "data" / "atlas-projection-contract.json",
    "time": ROOT / "data" / "atlas-time-contract.json",
    "stack": ROOT / "knowledge" / "core" / "world-atlas-integrated-layer-stack.json",
    "depths": ROOT / "data" / "axis-depths.json",
    "operators": ROOT / "data" / "axis-operators.json",
    "formal": ROOT / "data" / "axis-formal-lenses.json",
    "placement": ROOT / "data" / "map-layer-placement-matrix.json",
}


def load(name: str, errors: list[str]):
    path = FILES[name]
    if not path.exists():
        errors.append(f"missing required Atlas contract: {path.relative_to(ROOT)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    docs = {name: load(name, errors) for name in FILES}
    projection = docs["projection"]
    time = docs["time"]
    stack = docs["stack"]
    depths = docs["depths"]

    coords = projection.get("state_vector", {}).get("coordinates", {})
    expected_coords = {"G", "T", "R", "E", "A", "F", "C"}
    if set(coords) != expected_coords:
        errors.append(f"projection state coordinates must be exactly {sorted(expected_coords)}; got {sorted(coords)}")

    invariant = projection.get("state_vector", {}).get("identity_invariant", "")
    if "canonical object ID" not in invariant:
        errors.append("projection contract must preserve canonical object identity")
    after = projection.get("projection_contract", {}).get("after", [])
    if "information_loss" not in after:
        errors.append("projection contract must disclose information loss after nontrivial projection")
    if "source_path_back" not in after:
        errors.append("projection contract must preserve a route back to source owners")

    date_fields = set(time.get("date_fields", {}))
    for field in ("valid_from", "valid_to", "observed_at", "first_attested", "last_verified"):
        if field not in date_fields:
            errors.append(f"time contract missing required field: {field}")
    filter_modes = set(time.get("filter_modes", {}))
    for mode in ("current", "as_of", "changed_between"):
        if mode not in filter_modes:
            errors.append(f"time contract missing required filter mode: {mode}")
    if time.get("unknown_date_policy", {}).get("default") not in {"flag", "exclude", "include_context"}:
        errors.append("time contract has invalid unknown-date default")
    if "orthogonal" not in time.get("core_rule", "").lower():
        errors.append("time contract must explicitly keep Time orthogonal to the Axis")

    if stack.get("projection_contract") != "data/atlas-projection-contract.json":
        errors.append("canonical World Atlas stack does not point to the shared projection contract")
    if set(stack.get("shared_state", {}).get("coordinates", {})) != expected_coords:
        errors.append("canonical World Atlas stack is out of sync with projection-state coordinates")

    dim_obj = depths.get("dimensions", depths.get("levels", depths.get("depths", {})))
    found_dims: set[int] = set()
    if isinstance(dim_obj, dict):
        for key in dim_obj:
            try:
                found_dims.add(int(str(key).lstrip("Dd")))
            except ValueError:
                pass
    elif isinstance(dim_obj, list):
        for row in dim_obj:
            value = row.get("dimension", row.get("level", row.get("d"))) if isinstance(row, dict) else None
            try:
                found_dims.add(int(value))
            except (TypeError, ValueError):
                pass
    if found_dims and found_dims != set(range(1, 12)):
        errors.append(f"Axis depth contract should expose D1-D11; found {sorted(found_dims)}")
    elif not found_dims:
        warnings.append("could not structurally enumerate D1-D11 from axis-depths.json; semantic validators remain authoritative")

    # Operators deliberately have different canonical owners: D-level transformation
    # semantics live in axis-operators, while cross-layer operations such as Eye and
    # Mountain are also formalized in axis-formal-lenses/projection contract. Validate
    # the combined architecture instead of forcing every term into one file.
    operator_text = "\n".join(json.dumps(docs[name], ensure_ascii=False).lower() for name in ("operators", "formal", "projection", "placement"))
    for name in ("eye", "door", "spiral", "tree", "mountain", "swamp"):
        if name not in operator_text:
            errors.append(f"combined Atlas operator architecture missing core operator: {name}")

    print("Atlas view contract: G/T/R/E/A/F/C · canonical identity · information-loss disclosure")
    print("Time contract: Current · As of · Compare dates · unknown-date policy")
    print("Operator contract: validated across Axis + formal + projection + placement owners")
    print(f"Errors: {len(errors)} · Warnings: {len(warnings)}")
    for warning in warnings:
        print("WARNING:", warning)
    if errors:
        print("ATLAS VIEW CONTRACT VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("ATLAS VIEW CONTRACT VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
