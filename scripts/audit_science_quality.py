#!/usr/bin/env python3
"""Semantic quality audit for the Science corpus.

The audit deliberately separates hard publication/maturity failures from advisory
scientific incompleteness. It does not try to force recovery, archaeology,
comparative or T0/T1 records into an empirical-model schema.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCIENCE = ROOT / "knowledge" / "science"
GENERIC_FALLBACK_PREFIX = "Canonical science record for "
MATURITY_LEVEL_RE = re.compile(r"\bT([0-5])\b", re.I)

SUMMARY_KEYS = ("abstract", "summary", "purpose", "importance", "core_thesis", "description", "scope")
OBSERVABLE_TOKENS = ("observable", "measurement", "readout", "output", "prediction")
FAILURE_TOKENS = ("falsifier", "falsification", "failure", "rejection", "null_result", "failure_condition")
CALIBRATION_TOKENS = (
    "calibration", "dataset", "data", "fit", "fitted", "parameter_estimate", "parameter_constraint",
    "likelihood", "posterior", "confidence_interval", "uncertainty", "held_out", "evaluation", "result",
)
MODEL_TOKENS = (
    "model", "theory", "benchmark", "equation", "dynamics", "lagrangian", "hamiltonian", "formalism",
    "simulation", "prediction", "state_space", "reaction_diffusion", "stock_flow",
)
ARCHAEOLOGY_TOKENS = ("recovery", "archaeology", "recovered", "documentary", "source-ledger", "source ledger")
ADMIN_TOKENS = ("master-index", "registry", "inventory", "router", "routing-index", "coverage-index", "completion-matrix")


def flatten_keys(value) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(flatten_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(flatten_keys(child))
    return keys


def flatten_strings(value, limit: int = 200) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        text = " ".join(value.split())
        if text:
            out.append(text)
    elif isinstance(value, dict):
        for child in value.values():
            if len(out) >= limit:
                break
            out.extend(flatten_strings(child, limit - len(out)))
    elif isinstance(value, list):
        for child in value:
            if len(out) >= limit:
                break
            out.extend(flatten_strings(child, limit - len(out)))
    return out[:limit]


def source_summary(data: dict) -> str:
    for key in SUMMARY_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            text = " ".join(value.split())
            if not text.startswith(GENERIC_FALLBACK_PREFIX):
                return text
    return ""


def classify_role(path: Path, data: dict) -> str:
    text = " ".join(
        [path.as_posix(), str(data.get("title", "")), str(data.get("status", "")), str(data.get("document_type", ""))]
    ).lower()
    if any(token in text for token in ADMIN_TOKENS):
        return "administrative"
    if any(token in text for token in ARCHAEOLOGY_TOKENS):
        return "archaeology"
    if any(token in text for token in ("comparative", "symbolic", "metaphor", "myth")):
        return "comparative"
    keys = flatten_keys(data)
    if any(any(token in key for token in MODEL_TOKENS) for key in keys) or any(token in text for token in MODEL_TOKENS):
        return "model"
    return "research_record"


def has_any_key_token(data: dict, tokens: tuple[str, ...]) -> bool:
    keys = flatten_keys(data)
    return any(any(token in key for token in tokens) for key in keys)


def has_empirical_basis(data: dict) -> bool:
    if has_any_key_token(data, CALIBRATION_TOKENS):
        values = " ".join(flatten_strings(data)).lower()
        forward_only = (
            "calibration_path" in flatten_keys(data)
            and not any(token in flatten_keys(data) for token in ("results", "dataset", "fit_results", "parameter_estimates", "evaluation"))
        )
        if not forward_only:
            return True
        if any(phrase in values for phrase in ("fitted", "measured", "estimated", "held-out", "posterior", "confidence interval")):
            return True
    return False


def current_maturity_level(maturity: str) -> int | None:
    """Return the record's currently claimed T-level.

    Maturity strings in this corpus commonly state the current level first and
    then describe a future promotion gate, e.g. ``T2; T3 possible after data``.
    The later target must not be interpreted as a present maturity claim.
    """
    match = MATURITY_LEVEL_RE.search(str(maturity or ""))
    return int(match.group(1)) if match else None


def public_candidate(data: dict, role: str) -> bool:
    if role == "administrative":
        return False
    summary = source_summary(data)
    keys = flatten_keys(data)
    scientific_groups = 0
    for token in ("research_question", "model", "equation", "finding", "observable", "test", "falsification", "reference", "experiment", "mechanism", "prediction", "measurement", "calibration"):
        if any(token in key for key in keys):
            scientific_groups += 1
    if summary:
        if len(summary) >= 80 and scientific_groups >= 1:
            return True
        if len(summary) >= 40 and scientific_groups >= 3:
            return True
    return not summary and scientific_groups >= 2


def issue(code: str, message: str) -> dict:
    return {"code": code, "message": message}


def audit_payload(path: Path, data: dict) -> dict:
    role = classify_role(path, data)
    hard: list[dict] = []
    advisory: list[dict] = []
    summary = source_summary(data)
    candidate = public_candidate(data, role)
    maturity = str(data.get("maturity", ""))
    maturity_level = current_maturity_level(maturity)

    if candidate and not summary:
        advisory.append(issue(
            "public_candidate_missing_substantive_summary",
            "Record has enough scientific structure to look publishable but no substantive source abstract/summary; it must not rely on generated fallback copy if projected publicly.",
        ))

    if role == "model" and maturity_level is not None and maturity_level >= 3 and not has_empirical_basis(data):
        hard.append(issue(
            "maturity_t3_plus_without_empirical_basis",
            "T3+ maturity requires actual calibration, parameter constraints, data or reported evaluation results, not only a future calibration path.",
        ))

    if role == "model":
        if not has_any_key_token(data, OBSERVABLE_TOKENS):
            advisory.append(issue("model_missing_observable", "Model lacks an explicit observable/measurement/readout contract."))
        if not has_any_key_token(data, FAILURE_TOKENS):
            advisory.append(issue("model_missing_failure_condition", "Model lacks an explicit falsifier, failure condition or rejection criterion."))
        if not has_any_key_token(data, ("baseline", "comparator", "null_model", "control")):
            advisory.append(issue("model_missing_baseline", "Model lacks an explicit baseline/comparator/null model."))
        if not has_any_key_token(data, ("provenance", "source", "origin", "authorship")):
            advisory.append(issue("model_missing_provenance", "Model lacks explicit provenance/authorship metadata."))
        if not maturity:
            advisory.append(issue("model_missing_maturity", "Model has no declared T0-T5 maturity or equivalent maturity statement."))

    if role not in ("administrative", "archaeology") and candidate and summary and len(summary) < 80:
        advisory.append(issue("short_public_summary", "Public-facing Science record has only a short substantive summary; consider a denser abstract."))

    return {
        "file": path.as_posix(),
        "id": data.get("id") or path.stem,
        "title": data.get("title") or data.get("name") or path.stem,
        "role": role,
        "maturity": maturity,
        "current_maturity_level": maturity_level,
        "public_candidate": candidate,
        "hard_failures": hard,
        "advisories": advisory,
    }


def audit_tree(root: Path = SCIENCE) -> dict:
    records: list[dict] = []
    parse_failures: list[dict] = []
    for path in sorted(root.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            parse_failures.append(issue("json_parse_failure", f"{path.relative_to(ROOT)}: {exc}"))
            continue
        if not isinstance(data, dict):
            parse_failures.append(issue("science_record_not_object", f"{path.relative_to(ROOT)}: top-level JSON must be an object"))
            continue
        records.append(audit_payload(path.relative_to(root), data))

    hard_count = sum(len(record["hard_failures"]) for record in records) + len(parse_failures)
    advisory_count = sum(len(record["advisories"]) for record in records)
    ranked = sorted(
        [record for record in records if record["advisories"]],
        key=lambda record: (-len(record["advisories"]), record["file"]),
    )
    return {
        "schema": "science-quality-report/v1",
        "records_scanned": len(records),
        "hard_failure_count": hard_count,
        "advisory_count": advisory_count,
        "parse_failures": parse_failures,
        "hard_failures": [record for record in records if record["hard_failures"]],
        "ranked_advisories": ranked,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional path for machine-readable JSON report")
    parser.add_argument("--advisory-limit", type=int, default=25)
    args = parser.parse_args()

    report = audit_tree()
    if args.report:
        report_path = ROOT / args.report if not Path(args.report).is_absolute() else Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Science records scanned: {report['records_scanned']}")
    print(f"Hard failures: {report['hard_failure_count']}")
    print(f"Advisories: {report['advisory_count']}")

    for failure in report["parse_failures"]:
        print("HARD", failure["code"], failure["message"])
    for record in report["hard_failures"]:
        for failure in record["hard_failures"]:
            print("HARD", record["file"], failure["code"], "-", failure["message"])

    print("Highest advisory targets:")
    for record in report["ranked_advisories"][: max(0, args.advisory_limit)]:
        codes = ", ".join(item["code"] for item in record["advisories"])
        print(f" - {record['file']}: {codes}")

    return 1 if report["hard_failure_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
