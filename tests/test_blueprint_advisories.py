from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from blueprint_advisories import collect_missing_optional_metadata, format_advisory_summary


def test_advisories_group_missing_fields_instead_of_repeating_files():
    rows = [
        ("data/blueprints/a-blueprint.json", {"status": "active", "entity": "a"}),
        ("data/blueprints/b-blueprint.json", {"entity": "b", "validation_rules": []}),
    ]

    grouped = collect_missing_optional_metadata(rows)

    assert grouped["status"] == ["data/blueprints/b-blueprint.json"]
    assert grouped["implementation_notes"] == [
        "data/blueprints/a-blueprint.json",
        "data/blueprints/b-blueprint.json",
    ]
    assert grouped["validation_rules"] == ["data/blueprints/a-blueprint.json"]
    assert grouped["acquisition_plan"] == [
        "data/blueprints/a-blueprint.json",
        "data/blueprints/b-blueprint.json",
    ]


def test_advisory_summary_reports_counts_and_samples_compactly():
    grouped = {
        "implementation_notes": ["a.json", "b.json", "c.json", "d.json"],
        "validation_rules": ["z.json"],
    }

    lines = format_advisory_summary(grouped, sample_limit=2)

    assert lines == [
        "implementation_notes: missing from 4 blueprints (a.json, b.json, +2 more)",
        "validation_rules: missing from 1 blueprint (z.json)",
    ]
