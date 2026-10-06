#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def load(rel: str):
    path = ROOT / rel
    if not path.exists():
        errors.append(f"Missing: {rel}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Invalid JSON: {rel}: {exc}")
        return {}


def ids(rows):
    return {str(row.get("id")) for row in rows if isinstance(row, dict) and row.get("id")}


def main():
    atlas_rel = "knowledge/body/whole-brain-neurobiology-atlas.json"
    completion_rel = "knowledge/body/whole-brain-neurobiology-completion.json"
    atlas = load(atlas_rel)
    completion = load(completion_rel)
    routing = load("knowledge/indexes/neurotheology-routing-index.json")

    if atlas.get("id") != "whole-brain-neurobiology-atlas":
        errors.append("whole-brain atlas id must be whole-brain-neurobiology-atlas")
    if atlas.get("repository_root") != "mind" or atlas.get("repository_layer") != "neurobiology":
        errors.append("whole-brain atlas must classify as mind/neurobiology")

    required_sections = {
        "nervous-system-frame", "cerebral-cortex", "white-matter-connectivity",
        "diencephalon", "basal-ganglia", "memory-affect-context", "brainstem",
        "cerebellum", "sensory-systems", "motor-systems", "ventricles-csf-meninges",
        "cellular-chemical-neurobiology", "large-scale-networks", "brain-states-consciousness"
    }
    actual_sections = ids(atlas.get("sections", []))
    missing = required_sections - actual_sections
    if missing:
        errors.append(f"whole-brain atlas missing sections: {sorted(missing)}")

    mappings = {row.get("biology"): row for row in atlas.get("potatoverse_mapping_table", []) if isinstance(row, dict)}
    thalamus = mappings.get("thalamus", {})
    pineal = mappings.get("pineal-gland", {})
    if "Potato" not in str(thalamus.get("project_mapping", "")) or "Father" not in str(thalamus.get("project_mapping", "")):
        errors.append("thalamus mapping must explicitly include Potato and Father's House")
    if "project_canon" not in thalamus.get("status", []):
        errors.append("thalamus mapping must be typed project_canon")
    if not all(term in str(pineal.get("project_mapping", "")) for term in ("Single Eye", "Third Eye")):
        errors.append("pineal mapping must explicitly include Single Eye and Third Eye")
    if "project_canon" not in pineal.get("status", []):
        errors.append("pineal mapping must be typed project_canon")

    boundary_text = json.dumps(atlas.get("boundaries", {}), ensure_ascii=False).lower()
    for phrase in ("seat of soul", "seat of consciousness", "spiritual rank", "established neuroscience"):
        if phrase not in boundary_text:
            errors.append(f"atlas boundaries must address: {phrase}")

    flows = ids(atlas.get("flows", []))
    for flow in ("visual-flow", "thalamocortical-loop", "circadian-scn-pineal-loop", "csf-circulation", "interoceptive-autonomic-loop"):
        if flow not in flows:
            errors.append(f"atlas missing required flow: {flow}")

    owners = {row.get("owner") for row in routing.get("owners", []) if isinstance(row, dict)}
    if atlas_rel not in owners:
        errors.append("neurotheology routing index does not route to whole-brain atlas")

    if completion.get("owner") != atlas_rel:
        errors.append("whole-brain completion sidecar must point to the atlas owner")
    completion_topics = {row.get("topic") for row in completion.get("topics", []) if isinstance(row, dict)}
    for topic in ("Whole-brain hierarchy", "Diencephalon", "Large-scale brain networks", "Dynamic system flows"):
        if topic not in completion_topics:
            errors.append(f"completion sidecar missing topic: {topic}")

    print(f"Whole-brain sections: {len(actual_sections)}")
    print(f"Whole-brain flows: {len(flows)}")
    print(f"Completion topics: {len(completion_topics)}")
    print(f"Errors: {len(errors)}")
    for error in errors:
        print("ERROR:", error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
