import json
from pathlib import Path

from scripts.public_statement_evidence_root import reconcile_records


FIXTURE = Path(__file__).parent / "fixtures" / "public-statement-evidence-sources.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_more_precise_duplicate_keeps_second_timestamp_and_both_sources():
    rows = load_fixture()["precision_upgrade"]
    result = reconcile_records(rows)
    assert len(result) == 1
    assert result[0]["timestamp_utc"] == "2026-04-29T20:05:28Z"
    assert result[0]["precision"] == "second"
    assert result[0]["source_records"] == ["date-ledger", "timestamp-ledger"]


def test_same_second_different_quotes_remain_distinct():
    rows = load_fixture()["same_second_distinct"]
    result = reconcile_records(rows)
    assert len(result) == 2
    assert len({row["id"] for row in result}) == 2


def test_status_id_is_stronger_than_quote_date_matching():
    rows = load_fixture()["status_id_merge"]
    result = reconcile_records(rows)
    assert len(result) == 1
    assert result[0]["status_id"] == "1234567890"
    assert result[0]["precision"] == "second"


def test_quote_is_never_rewritten_during_reconciliation():
    rows = load_fixture()["precision_upgrade"]
    result = reconcile_records(rows)
    assert result[0]["quote"] == rows[1]["quote"]


def test_provenance_keeps_each_contributing_source_occurrence():
    rows = load_fixture()["precision_upgrade"]
    result = reconcile_records(rows)
    assert result[0]["source_occurrence_ids"] == ["old-1", "new-1"]
    assert len(result[0]["provenance"]) == 2
