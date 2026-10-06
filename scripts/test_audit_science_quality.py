#!/usr/bin/env python3
"""Focused regression tests for the semantic Science quality gate."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_science_quality.py"
BUILDER = ROOT / "scripts" / "build_science_catalog.py"
VALIDATOR = ROOT / "scripts" / "validate_science_portal.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"{path.name} could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_auditor():
    return load_module("audit_science_quality", SCRIPT)


def load_builder():
    return load_module("build_science_catalog", BUILDER)


def assert_has(items, code: str) -> None:
    assert any(item.get("code") == code for item in items), (code, items)


def assert_lacks(items, code: str) -> None:
    assert not any(item.get("code") == code for item in items), (code, items)


def test_thin_source_record_is_flagged_without_false_hard_failure(auditor) -> None:
    data = {
        "id": "thin-model",
        "title": "Thin Model",
        "status": "candidate model",
        "research_question": "Can this be tested?",
        "equations": ["x'=ax"],
        "observables": ["x"],
    }
    result = auditor.audit_payload(Path("thin-model.json"), data)
    assert result["public_candidate"] is True
    assert_lacks(result["hard_failures"], "public_candidate_missing_substantive_summary")
    assert_has(result["advisories"], "public_candidate_missing_substantive_summary")


def test_t3_requires_calibration_or_data(auditor) -> None:
    data = {
        "id": "overclaimed",
        "title": "Overclaimed Model",
        "abstract": "A sufficiently long scientific abstract describing a model that claims parameter-constrained maturity without showing any actual calibration evidence.",
        "status": "scientific model",
        "maturity": "T3 parameter-constrained",
        "equations": ["y=ax+b"],
        "observables": ["y"],
        "falsifiers": ["held-out prediction fails"],
    }
    result = auditor.audit_payload(Path("overclaimed.json"), data)
    assert_has(result["hard_failures"], "maturity_t3_plus_without_empirical_basis")


def test_future_t3_gate_does_not_raise_current_t2_maturity(auditor) -> None:
    data = {
        "id": "honest-toy",
        "title": "Honest Toy Model",
        "abstract": "A sufficiently long scientific abstract describing a mathematical toy model whose future calibration requirements are stated explicitly without claiming they have been completed.",
        "status": "scientific model",
        "maturity": "T2 general model; T3 possible only after domain-specific calibration and held-out validation",
        "equations": ["dx/dt=f(x)"],
        "observables": ["x"],
        "falsifiers": ["held-out prediction fails after calibration"],
    }
    result = auditor.audit_payload(Path("honest-toy.json"), data)
    assert_lacks(result["hard_failures"], "maturity_t3_plus_without_empirical_basis")


def test_t3_with_explicit_fit_result_is_allowed(auditor) -> None:
    data = {
        "id": "fitted",
        "title": "Fitted Model",
        "abstract": "A sufficiently long scientific abstract describing a fitted model with explicit data provenance, parameter estimates and evaluation results.",
        "status": "scientific model",
        "maturity": "T3 parameter-constrained",
        "calibration": {"dataset": "declared dataset", "method": "least squares"},
        "results": {"parameter_estimates": {"a": 1.2}, "evaluation": "held-out RMSE reported"},
        "equations": ["y=ax+b"],
        "observables": ["y"],
        "falsifiers": ["held-out prediction fails"],
    }
    result = auditor.audit_payload(Path("fitted.json"), data)
    assert_lacks(result["hard_failures"], "maturity_t3_plus_without_empirical_basis")


def test_archaeology_is_not_forced_to_be_empirical_model(auditor) -> None:
    data = {
        "id": "recovery",
        "title": "Equation Recovery",
        "abstract": "A documentary recovery record preserving historical equations, source uncertainty, wording and later interpretation without claiming empirical validation.",
        "status": "recovery / archaeology",
        "source_records": ["primary transcript target"],
        "recovered_equations": ["x=y"],
    }
    result = auditor.audit_payload(Path("equation-recovery.json"), data)
    assert result["role"] == "archaeology"
    assert_lacks(result["hard_failures"], "empirical_model_missing_observable")
    assert_lacks(result["hard_failures"], "empirical_model_missing_failure_condition")


def test_model_gaps_are_advisory_before_t3(auditor) -> None:
    data = {
        "id": "toy",
        "title": "Toy Model",
        "abstract": "A defined mathematical toy model with enough explanation to be useful while remaining honestly incomplete and explicitly below calibrated maturity.",
        "status": "toy model",
        "maturity": "T2",
        "equations": ["dx/dt=f(x)"],
    }
    result = auditor.audit_payload(Path("toy.json"), data)
    assert_lacks(result["hard_failures"], "empirical_model_missing_observable")
    assert_has(result["advisories"], "model_missing_observable")
    assert_has(result["advisories"], "model_missing_failure_condition")


def test_generated_fallback_cannot_qualify_for_public_library(builder) -> None:
    data = {
        "id": "thin-but-keyword-rich-model",
        "title": "Thin But Keyword Rich Model",
        "research_question": "Can this be tested?",
        "model": {"kind": "toy"},
        "equations": ["x'=ax"],
        "observables": ["x"],
    }
    record = {
        "abstract": "Canonical science record for Thin But Keyword Rich Model With A Long Display Title.",
    }
    assert builder.qualifies_for_library(Path("thin-model.json"), data, record) is False


def test_science_portal_validator_invokes_semantic_audit_and_diagnostics() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    assert "audit_science_quality" in text
    assert "generated fallback abstract" in text
    assert "::error file=" in text
    assert "science-portal-report.json" in text


def main() -> int:
    auditor = load_auditor()
    builder = load_builder()
    tests = [
        lambda _: test_generated_fallback_cannot_qualify_for_public_library(builder),
        test_thin_source_record_is_flagged_without_false_hard_failure,
        test_t3_requires_calibration_or_data,
        test_future_t3_gate_does_not_raise_current_t2_maturity,
        test_t3_with_explicit_fit_result_is_allowed,
        test_archaeology_is_not_forced_to_be_empirical_model,
        test_model_gaps_are_advisory_before_t3,
    ]
    for test in tests:
        test(auditor)
        print("PASS", getattr(test, "__name__", "test_generated_fallback_cannot_qualify_for_public_library"))
    test_science_portal_validator_invokes_semantic_audit_and_diagnostics()
    print("PASS test_science_portal_validator_invokes_semantic_audit_and_diagnostics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
