#!/usr/bin/env python3
from __future__ import annotations

from atlas_model import build_model, by_id


def main() -> int:
    model = build_model()
    nodes = by_id(model)
    root = model.get("root_id")

    if root not in nodes:
        raise SystemExit("ATLAS MODEL FAILED: root missing from derived model")

    for node_id, node in nodes.items():
        path = node.get("north_path", [])
        if not path or path[0] != root or path[-1] != node_id:
            raise SystemExit(f"ATLAS MODEL FAILED: invalid north_path for {node_id}: {path}")
        if len(path) != len(set(path)):
            raise SystemExit(f"ATLAS MODEL FAILED: repeated node in north_path for {node_id}")

        parent = node.get("north_parent")
        if node_id == root:
            if parent is not None:
                raise SystemExit("ATLAS MODEL FAILED: root has parent")
        else:
            if not isinstance(parent, str) or parent not in nodes:
                raise SystemExit(f"ATLAS MODEL FAILED: invalid parent for {node_id}")
            if node_id not in nodes[parent].get("children", []):
                raise SystemExit(f"ATLAS MODEL FAILED: derived child missing under {parent}")

        for child in node.get("children", []):
            if child not in nodes:
                raise SystemExit(f"ATLAS MODEL FAILED: unresolved child {child}")
            if nodes[child].get("north_parent") != node_id:
                raise SystemExit(f"ATLAS MODEL FAILED: child/parent mismatch {node_id}->{child}")

        if not str(node.get("summary", "")).strip():
            raise SystemExit(f"ATLAS MODEL FAILED: empty summary for {node_id}")
        if not str(node.get("title", "")).strip():
            raise SystemExit(f"ATLAS MODEL FAILED: empty title for {node_id}")

    print(f"ATLAS MODEL PASSED: {len(nodes)} active nodes; root={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
