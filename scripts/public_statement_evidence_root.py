from __future__ import annotations

from copy import deepcopy

_PRECISION_RANK = {"unknown": 0, "date": 1, "minute": 2, "second": 3}


def timestamp_precision(record: dict) -> str:
    value = str(record.get("timestamp_utc") or "").strip()
    if value:
        time_part = value.split("T", 1)[1] if "T" in value else value
        return "second" if time_part.count(":") >= 2 else "minute"
    return "date" if record.get("date") else "unknown"


def _match_key(record: dict):
    status_id = str(record.get("status_id") or "").strip()
    if status_id:
        return ("status_id", status_id)
    date = str(record.get("date") or "").strip()
    quote = record.get("quote")
    if date and isinstance(quote, str):
        return ("date_quote", date, quote)
    return ("record", str(record.get("id") or id(record)))


def _record_order(record: dict) -> tuple:
    return (
        str(record.get("source_record") or ""),
        str(record.get("source_occurrence_id") or ""),
        str(record.get("id") or ""),
    )


def _provenance(record: dict) -> dict:
    return {
        key: record[key]
        for key in (
            "id",
            "source_record",
            "source_occurrence_id",
            "date",
            "timestamp_utc",
            "status_id",
        )
        if record.get(key) not in (None, "")
    }


def _merge_group(records: list[dict], match_basis: str) -> dict:
    ordered = sorted(records, key=_record_order)
    preferred = sorted(
        ordered,
        key=lambda record: (-_PRECISION_RANK[timestamp_precision(record)], _record_order(record)),
    )[0]
    result = deepcopy(preferred)
    result["precision"] = timestamp_precision(preferred)
    result["source_records"] = list(
        dict.fromkeys(str(row.get("source_record")) for row in ordered if row.get("source_record"))
    )
    result["source_occurrence_ids"] = list(
        dict.fromkeys(
            str(row.get("source_occurrence_id"))
            for row in ordered
            if row.get("source_occurrence_id")
        )
    )
    result["provenance"] = [_provenance(row) for row in ordered]
    result["match_basis"] = match_basis

    for row in ordered:
        if not result.get("status_id") and row.get("status_id"):
            result["status_id"] = str(row["status_id"])
        if not result.get("timestamp_utc") and row.get("timestamp_utc"):
            result["timestamp_utc"] = row["timestamp_utc"]
        if not result.get("date") and row.get("date"):
            result["date"] = row["date"]
    return result


def reconcile_records(records: list[dict]) -> list[dict]:
    groups: list[tuple[tuple, list[dict]]] = []
    index: dict[tuple, int] = {}

    for record in records:
        key = _match_key(record)
        group_index = index.get(key)
        if group_index is None:
            index[key] = len(groups)
            groups.append((key, [record]))
        else:
            groups[group_index][1].append(record)

    return [_merge_group(rows, key[0]) for key, rows in groups]
