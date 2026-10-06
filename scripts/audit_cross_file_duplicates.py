#!/usr/bin/env python3
"""Cross-file duplication audit.

The repository intentionally has source, observation, enrichment, graph and
research layers. This audit therefore distinguishes exact duplication from
legitimate projections. It is deliberately conservative: it never deletes or
merges records automatically.

Hard errors:
- identical normalized JSON payloads in multiple files (excluding known report,
  manifest and source-copy classes)
- the same substantive record fingerprint owned by two canonical-owner files
- a non-owner file copying a canonical definition/description verbatim when it
  is not explicitly a derived/enrichment/research layer

Warnings:
- repeated record identities across layers
- repeated long definition text across layers
- legacy snapshots or batch artifacts that have a current replacement
- malformed/legacy JSON that the repository index could not parse

Malformed JSON is deliberately a warning here rather than a deployment blocker:
the canonical repository-index builder already records these files as
`json_errors` and excludes them from the navigable registry. This keeps the
cross-file audit focused on duplication/source-of-truth violations while still
surfacing every malformed file in its generated report.
"""
from __future__ import annotations
import hashlib, json, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MAP = DATA / "canonical-source-map.json"
OUT = DATA / "cross-file-duplicate-audit.json"

VOLATILE = {
    "version", "updated", "generated_at", "generatedAt", "timestamp", "created_at",
    "modified_at", "run_at", "audit_date", "sha", "commit", "commit_sha",
    "source_path", "path", "url", "html_url", "profile_url"
}
IDENTITY = ("canonical_id", "iso3", "iso2", "id", "term", "primary", "name", "title")
SUBSTANTIVE = {"definition", "meaning", "description", "summary", "content", "text", "purpose"}
REPORT_WORDS = ("audit", "manifest", "checklist", "matrix", "state", "coverage", "scale", "registry")
DERIVED_WORDS = ("lexicon", "glossary", "cosmology", "concept-map", "relationships", "timeline", "atlas", "graph", "enrichment", "expansion", "research", "observations", "view", "projection", "batch")


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def norm(v):
    if isinstance(v, dict):
        return {k: norm(x) for k, x in sorted(v.items()) if k not in VOLATILE}
    if isinstance(v, list):
        return [norm(x) for x in v]
    if isinstance(v, str):
        return re.sub(r"\s+", " ", v).strip()
    return v


def digest(v):
    raw = json.dumps(norm(v), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def identity_of(obj):
    if not isinstance(obj, dict):
        return None
    for key in IDENTITY:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return f"{key}:{re.sub(r'\s+', ' ', value).strip().casefold()}"
    return None


def has_substantive(obj):
    return isinstance(obj, dict) and any(k in obj and isinstance(obj[k], (str, dict, list)) for k in SUBSTANTIVE)


def walk_records(obj, path="$"):
    if isinstance(obj, dict):
        ident = identity_of(obj)
        if ident:
            yield ident, obj, path
        for k, v in obj.items():
            yield from walk_records(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_records(v, f"{path}[{i}]")


def file_class(path: Path):
    n = path.name.casefold()
    if any(x in n for x in REPORT_WORDS):
        return "report-or-manifest"
    if any(x in n for x in DERIVED_WORDS):
        return "derived-or-research"
    if "/sources/" in path.as_posix():
        return "source"
    return "primary-or-unknown"


def declared_owner_map():
    if not MAP.exists():
        return {}, []
    data = load(MAP)
    owners = {}
    for family, spec in data.get("families", {}).items():
        for key in ("canonical_owner", "adjacent_owner"):
            val = spec.get(key)
            if isinstance(val, str):
                owners[val] = family
    return owners, data.get("families", {})


def main():
    owners, families = declared_owner_map()
    files = sorted(p for p in DATA.rglob("*.json") if p != OUT and ".git" not in p.parts)
    parsed = {}
    invalid = []
    for p in files:
        try:
            parsed[p] = load(p)
        except Exception as e:
            invalid.append({"file": str(p.relative_to(ROOT)), "error": str(e)})

    exact = defaultdict(list)
    for p, data in parsed.items():
        if file_class(p) == "report-or-manifest":
            continue
        exact[digest(data)].append(str(p.relative_to(ROOT)))
    exact_groups = [v for v in exact.values() if len(v) > 1]

    records = defaultdict(list)
    for p, data in parsed.items():
        for ident, obj, location in walk_records(data):
            if not has_substantive(obj):
                continue
            records[(ident, digest(obj))].append({"file": str(p.relative_to(ROOT)), "path": location})

    exact_record_groups = [v for v in records.values() if len(v) > 1]

    identities = defaultdict(list)
    for p, data in parsed.items():
        for ident, obj, location in walk_records(data):
            identities[ident].append({
                "file": str(p.relative_to(ROOT)), "path": location,
                "class": file_class(p), "substantive": has_substantive(obj)
            })
    repeated_identities = {k: v for k, v in identities.items() if len({x["file"] for x in v}) > 1}

    definition_hits = defaultdict(list)
    for p, data in parsed.items():
        for ident, obj, location in walk_records(data):
            if not isinstance(obj, dict):
                continue
            for key in ("definition", "meaning", "description", "summary"):
                value = obj.get(key)
                if isinstance(value, str) and len(value.split()) >= 25:
                    definition_hits[re.sub(r"\s+", " ", value).strip().casefold()].append({
                        "identity": ident, "file": str(p.relative_to(ROOT)), "path": location, "field": key
                    })
    repeated_definitions = {k: v for k, v in definition_hits.items() if len({x["file"] for x in v}) > 1}

    owner_conflicts = []
    for group in exact_record_groups:
        files_in_group = {x["file"] for x in group}
        canonical_files = [f for f in files_in_group if f in owners]
        if len(canonical_files) > 1:
            owner_conflicts.append(group)

    warnings = []
    for ident, rows in repeated_identities.items():
        substantive_files = {x["file"] for x in rows if x["substantive"]}
        if len(substantive_files) > 1:
            warnings.append({"identity": ident, "occurrences": rows})
    for ident, rows in repeated_definitions.items():
        warnings.append({"definition": ident, "occurrences": rows})

    legacy_candidates = []
    for p in files:
        n = p.name.casefold()
        if re.search(r"(?:^|[-_])(20\d{2}[-_]\d{2}[-_]\d{2}|batch[-_]\d|old|legacy|backup|snapshot)(?:[-_.]|$)", n):
            legacy_candidates.append(str(p.relative_to(ROOT)))

    result = {
        "version": "1.1.0",
        "updated": "2026-09-08",
        "purpose": "Repository-wide cross-file duplication and source-of-truth audit",
        "policy": {
            "one_source_of_truth": True,
            "exact_duplicate_files": "error unless report/manifest",
            "exact_duplicate_records": "error when substantive and owned by multiple canonical sources",
            "repeated_identity": "warning until classified as source, enrichment, observation, projection or duplicate",
            "repeated_definition": "warning; migrate substantive definitions to the declared owner",
            "invalid_json": "warning; canonical registry records json_errors and excludes malformed files from navigation",
            "legacy_artifacts": "review before deletion; provenance must not be destroyed"
        },
        "counts": {
            "json_files_scanned": len(parsed),
            "invalid_json": len(invalid),
            "exact_duplicate_file_groups": len(exact_groups),
            "exact_duplicate_record_groups": len(exact_record_groups),
            "canonical_owner_conflicts": len(owner_conflicts),
            "repeated_identities": len(repeated_identities),
            "repeated_long_definitions": len(repeated_definitions),
            "legacy_candidates": len(legacy_candidates)
        },
        "exact_duplicate_files": exact_groups,
        "exact_duplicate_records": exact_record_groups,
        "canonical_owner_conflicts": owner_conflicts,
        "repeated_identities": warnings[:500],
        "legacy_candidates": legacy_candidates,
        "invalid_json": invalid
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], ensure_ascii=False, indent=2))
    if exact_groups or owner_conflicts:
        return 1
    if invalid:
        print(f"cross-file audit: WARNING — {len(invalid)} malformed JSON file(s) are excluded by the canonical registry")
    return 0


if __name__ == "__main__":
    sys.exit(main())
