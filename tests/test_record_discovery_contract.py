from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_generated_outputs_are_excluded_from_record_discovery(tmp_path):
    contract = importlib.import_module("record_discovery_contract")
    for name in (
        "domain.json",
        "canonical-record-registry.json",
        "repository-index.json",
        "depth-audit-live.json",
        "source-of-truth-audit.json",
    ):
        (tmp_path / name).write_text("{}\n", encoding="utf-8")

    discovered = [path.name for path in contract.iter_discovery_json(tmp_path)]

    assert discovered == ["domain.json"]


def test_registry_and_repository_index_share_discovery_contract():
    contract = importlib.import_module("record_discovery_contract")
    registry = importlib.import_module("build_canonical_record_registry")
    repository_index = importlib.import_module("build_repository_index")

    assert registry.iter_discovery_json is contract.iter_discovery_json
    assert repository_index.iter_discovery_json is contract.iter_discovery_json


def test_registry_index_delta_explains_consolidated_and_synthesized_ids():
    audit = importlib.import_module("audit_source_of_truth")
    registry = {
        "records": [
            {"id": "door"},
            {"id": "the-door"},
            {"id": "ordinary"},
        ]
    }
    index = {
        "records": [
            {
                "id": "door",
                "canonical_concept": True,
                "occurrences": [{"id": "door"}, {"id": "the-door"}],
            },
            {"id": "ordinary"},
            {
                "id": "axis",
                "canonical_concept": True,
                "occurrence_count": 0,
                "occurrences": [],
                "classification_basis": "canonical-concept-registry",
            },
        ]
    }

    delta = audit.explain_registry_index_delta(registry, index)

    assert delta["registry_only"] == ["the-door"]
    assert delta["index_only"] == ["axis"]
    assert delta["consolidated_source_ids"] == {"the-door": "door"}
    assert delta["canonicalized_concept_ids"] == []
    assert delta["synthesized_canonical_ids"] == ["axis"]
    assert delta["unexplained_registry_only"] == []
    assert delta["unexplained_index_only"] == []


def test_registry_index_delta_explains_canonical_slug_created_from_raw_label():
    audit = importlib.import_module("audit_source_of_truth")
    registry = {"records": [{"id": "Blood"}]}
    index = {
        "records": [
            {
                "id": "blood",
                "canonical_concept": True,
                "occurrence_count": 1,
                "occurrences": [{"id": "Blood"}],
            }
        ]
    }

    delta = audit.explain_registry_index_delta(registry, index)

    assert delta["consolidated_source_ids"] == {"Blood": "blood"}
    assert delta["canonicalized_concept_ids"] == ["blood"]
    assert delta["synthesized_canonical_ids"] == []
    assert delta["unexplained_registry_only"] == []
    assert delta["unexplained_index_only"] == []


def test_registry_index_delta_keeps_unexplained_drift_visible():
    audit = importlib.import_module("audit_source_of_truth")
    registry = {"records": [{"id": "orphan-source"}]}
    index = {"records": [{"id": "orphan-index"}]}

    delta = audit.explain_registry_index_delta(registry, index)

    assert delta["unexplained_registry_only"] == ["orphan-source"]
    assert delta["unexplained_index_only"] == ["orphan-index"]
