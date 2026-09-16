from __future__ import annotations

import copy
from pathlib import Path

from scripts.build_bible_consolidation import build_outputs
from scripts.validate_bible_consolidation import validate_payloads

ROOT = Path(__file__).resolve().parents[1]


def test_validator_accepts_fresh_generated_payloads():
    assert validate_payloads(ROOT, build_outputs(ROOT)) == []


def test_validator_rejects_relation_loss():
    payloads = build_outputs(ROOT)
    payloads = copy.deepcopy(payloads)
    payloads["fingerprints"]["relations"].pop()
    errors = validate_payloads(ROOT, payloads)
    assert any("fingerprint coverage" in error for error in errors)


def test_validator_rejects_unknown_family_member():
    payloads = copy.deepcopy(build_outputs(ROOT))
    if not payloads["families"]["families"]:
        return
    payloads["families"]["families"][0]["member_relation_ids"].append("missing-relation")
    errors = validate_payloads(ROOT, payloads)
    assert any("unknown family member" in error for error in errors)


def test_validator_rejects_representative_outside_family():
    payloads = copy.deepcopy(build_outputs(ROOT))
    if not payloads["families"]["families"]:
        return
    payloads["families"]["families"][0]["representative_relation_id"] = "not-a-member"
    errors = validate_payloads(ROOT, payloads)
    assert any("representative" in error for error in errors)


def test_validator_rejects_manifest_version_drift():
    payloads = copy.deepcopy(build_outputs(ROOT))
    payloads["families"]["manifest_version"] = "stale"
    errors = validate_payloads(ROOT, payloads)
    assert any("manifest version" in error for error in errors)


def test_validator_rejects_synthetic_family_claim():
    payloads = copy.deepcopy(build_outputs(ROOT))
    if not payloads["families"]["families"]:
        return
    payloads["families"]["families"][0]["maximum_claim"] = "A stronger generated claim."
    errors = validate_payloads(ROOT, payloads)
    assert any("family-level maximum_claim" in error for error in errors)


def test_validator_rejects_alias_that_hides_unique_evidence():
    payloads = copy.deepcopy(build_outputs(ROOT))
    if not payloads["duplicates"]["candidates"]:
        return
    item = payloads["duplicates"]["candidates"][0]
    item["requires_evidence_migration"] = True
    item["suggested_action"] = "alias"
    errors = validate_payloads(ROOT, payloads)
    assert any("alias hides unique evidence" in error for error in errors)
