#!/usr/bin/env python3
"""Import an ADL H.E.A.T. CSV export into canonical World Map evidence artifacts.

Usage:
    python scripts/import_adl_heat.py /path/to/adl-heat.csv

The importer never downloads data on its own. Download the official CSV from the
ADL H.E.A.T. Map, then pass the local file here so the generated snapshot is
reviewable and reproducible.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "world-incidents" / "adl-heat"

STATE_NAMES = {
    "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia",
    "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas",
    "KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan",
    "MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada",
    "NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont",
    "VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming",
}
NAME_TO_STATE = {name.lower(): code for code, name in STATE_NAMES.items()}

ALIASES = {
    "id": ("id", "incident id", "incident_id", "record id", "record_id"),
    "date": ("date", "incident date", "incident_date"),
    "city": ("city", "municipality"),
    "state": ("state", "state abbreviation", "state_abbreviation"),
    "type": ("type", "incident type", "incident_type", "incident"),
    "ideology": ("ideology",),
    "subideology": ("subideology", "sub-ideology", "sub ideology"),
    "group": ("group", "associated group", "associated_group"),
    "description": ("description", "summary", "incident description", "incident_description"),
    "latitude": ("latitude", "lat"),
    "longitude": ("longitude", "lon", "lng"),
}

def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()

def find_column(headers: list[str], logical: str) -> str | None:
    by_norm = {norm(h): h for h in headers}
    for alias in ALIASES[logical]:
        hit = by_norm.get(norm(alias))
        if hit:
            return hit
    return None

def parse_date(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%m-%d-%Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass
    return raw

def exact_date_or_none(value: str):
    parsed = parse_date(value)
    if not parsed:
        return None
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", parsed):
        return None
    try:
        return datetime.strptime(parsed, "%Y-%m-%d").date()
    except ValueError:
        return None

def state_code(value: str) -> str:
    raw = str(value or "").strip()
    upper = raw.upper()
    if upper in STATE_NAMES:
        return upper
    return NAME_TO_STATE.get(raw.lower(), "")

def float_or_none(value: str) -> float | None:
    try:
        result = float(str(value).strip())
        return result if result == result else None
    except (TypeError, ValueError):
        return None

def row_value(row: dict[str, str], columns: dict[str, str | None], key: str) -> str:
    column = columns.get(key)
    return str(row.get(column, "") if column else "").strip()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--dataset-label", default="ADL H.E.A.T. records")
    parser.add_argument("--retrieved", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--out-dir", type=Path, default=OUT, help="Output directory; defaults to the canonical committed snapshot directory.")
    parser.add_argument(
        "--confirm-official-export",
        action="store_true",
        help="Required acknowledgement that the input file was downloaded from the official ADL H.E.A.T. Map export.",
    )
    args = parser.parse_args()

    if not args.confirm_official_export:
        raise SystemExit("Refusing import without --confirm-official-export. Use only a reviewed download from the official ADL H.E.A.T. Map.")
    retrieved_date = exact_date_or_none(args.retrieved)
    if retrieved_date is None:
        raise SystemExit("--retrieved must be an exact YYYY-MM-DD date")

    raw = args.csv_path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8-sig")

    reader = csv.DictReader(text.splitlines())
    if not reader.fieldnames:
        raise SystemExit("CSV has no header row")
    headers = list(reader.fieldnames)
    columns = {key: find_column(headers, key) for key in ALIASES}
    for required in ("date", "state", "type"):
        if not columns[required]:
            raise SystemExit(f"Could not identify required {required!r} column. Headers: {headers}")

    features: list[dict] = []
    state_rows: dict[str, dict] = {
        f"US-{code}": {
            "id": f"US-{code}", "code": code, "name": name, "total": 0,
            "by_year": Counter(), "by_type": Counter(), "by_type_token": Counter(),
            "by_year_type_token": defaultdict(Counter), "by_ideology": Counter(),
        }
        for code, name in STATE_NAMES.items()
    }
    source_rows = 0
    state_known_rows = 0
    missing_geometry = 0
    unsupported_state_rows = 0
    invalid_dates: list[tuple[int, str]] = []
    invalid_coordinates: list[tuple[int, str, str]] = []
    duplicate_source_ids: list[str] = []
    seen_source_ids: set[str] = set()

    for ordinal, row in enumerate(reader, start=1):
        if not any(str(v or "").strip() for v in row.values()):
            continue
        source_rows += 1
        state_raw = row_value(row, columns, "state")
        state = state_code(state_raw)
        if state_raw and not state:
            unsupported_state_rows += 1
        raw_date = row_value(row, columns, "date")
        date_obj = exact_date_or_none(raw_date)
        if raw_date and date_obj is None:
            invalid_dates.append((ordinal, raw_date))
        date = date_obj.isoformat() if date_obj else ""
        if date_obj and date_obj > retrieved_date:
            invalid_dates.append((ordinal, raw_date))
        year = date_obj.year if date_obj else None
        incident_type = row_value(row, columns, "type") or "Unknown"
        ideology = row_value(row, columns, "ideology") or "Unknown"
        subdivision = f"US-{state}" if state else ""

        if subdivision in state_rows:
            state_known_rows += 1
            summary = state_rows[subdivision]
            summary["total"] += 1
            if year:
                summary["by_year"][str(year)] += 1
            summary["by_type"][incident_type] += 1
            type_tokens = [token.strip() for token in incident_type.split(";") if token.strip()]
            for token in type_tokens:
                summary["by_type_token"][token] += 1
                if year:
                    summary["by_year_type_token"][str(year)][token] += 1
            summary["by_ideology"][ideology] += 1

        source_id = row_value(row, columns, "id") or str(ordinal)
        if source_id in seen_source_ids:
            duplicate_source_ids.append(source_id)
            continue
        seen_source_ids.add(source_id)

        lat_raw = row_value(row, columns, "latitude")
        lon_raw = row_value(row, columns, "longitude")
        lat = float_or_none(lat_raw)
        lon = float_or_none(lon_raw)
        malformed_coordinate = (bool(lat_raw) and lat is None) or (bool(lon_raw) and lon is None)
        out_of_range = (lat is not None and not -90 <= lat <= 90) or (lon is not None and not -180 <= lon <= 180)
        if malformed_coordinate or out_of_range:
            invalid_coordinates.append((ordinal, lat_raw, lon_raw))
            continue
        if lat is None or lon is None or not state:
            missing_geometry += 1
            continue
        features.append({
            "type": "Feature",
            "id": f"adl-{source_id}",
            "properties": {
                "id": f"adl-{source_id}",
                "source_id": source_id,
                "date": date,
                "year": year,
                "city": row_value(row, columns, "city"),
                "state": state,
                "state_name": STATE_NAMES[state],
                "subdivision_id": subdivision,
                "incident_type": incident_type,
                "ideology": row_value(row, columns, "ideology"),
                "subideology": row_value(row, columns, "subideology"),
                "group": row_value(row, columns, "group"),
                "description": row_value(row, columns, "description"),
                "dataset": args.dataset_label,
                "source_owner": "Anti-Defamation League / Center on Extremism",
                "source_status": "official ADL H.E.A.T. CSV import",
            },
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
        })

    if source_rows == 0:
        raise SystemExit("ADL export contains no data rows")
    if invalid_dates:
        examples = ", ".join(f"row {row}: {value!r}" for row, value in invalid_dates[:5])
        raise SystemExit(f"Invalid ADL export dates or dates after retrieval date: {examples}")
    if invalid_coordinates:
        examples = ", ".join(f"row {row}: ({lat!r}, {lon!r})" for row, lat, lon in invalid_coordinates[:5])
        raise SystemExit(f"Invalid ADL export coordinates: {examples}")
    if duplicate_source_ids:
        raise SystemExit("Duplicate ADL source IDs: " + ", ".join(sorted(set(duplicate_source_ids))[:10]))

    for row in state_rows.values():
        row["by_year"] = dict(sorted(row["by_year"].items()))
        row["by_type"] = dict(sorted(row["by_type"].items()))
        row["by_type_token"] = dict(sorted(row["by_type_token"].items()))
        row["by_year_type_token"] = {
            year: dict(sorted(counter.items()))
            for year, counter in sorted(row["by_year_type_token"].items())
        }
        row["by_ideology"] = dict(sorted(row["by_ideology"].items()))

    dated = sorted(
        f["properties"]["date"] for f in features
        if re.match(r"^\d{4}-\d{2}-\d{2}$", f["properties"]["date"])
    )
    years = sorted({f["properties"]["year"] for f in features if f["properties"]["year"]})

    metadata = {
        "version": "1.0.0",
        "record_type": "world-incident-dataset",
        "id": "adl-heat",
        "title": "ADL H.E.A.T. Map — U.S. incident evidence layer",
        "source_organization": "Anti-Defamation League (ADL), Center on Extremism",
        "official_source_url": "https://www.adl.org/resources/tools-to-track-hate/heat-map",
        "official_app_url": "https://www.adl.org/apps/heatmap/",
        "official_update_cadence": "monthly",
        "official_access_note": "ADL states that H.E.A.T. Map users can download raw incident data as CSV.",
        "snapshot": {
            "status": "official-export",
            "dataset": args.dataset_label,
            "record_count": source_rows,
            "state_known_record_count": state_known_rows,
            "geocoded_record_count": len(features),
            "missing_geometry_count": missing_geometry,
            "exact_min_date": dated[0] if dated else None,
            "exact_max_date": dated[-1] if dated else None,
            "years": years,
            "source_filename": args.csv_path.name,
            "source_sha256": sha256,
            "project_retrieved": args.retrieved,
            "official_export_confirmed": True,
        },
        "import_diagnostics": {
            "headers": headers,
            "resolved_columns": columns,
            "source_rows": source_rows,
            "state_known_rows": state_known_rows,
            "unsupported_state_rows": unsupported_state_rows,
            "geocoded_rows": len(features),
            "missing_geometry_rows": missing_geometry,
            "invalid_date_rows": 0,
            "invalid_coordinate_rows": 0,
            "duplicate_source_ids": 0,
        },
        "methodology": {
            "display_semantics": "Counts represent records in this ADL H.E.A.T. export. They are not a general hate score, crime rate, population-normalized risk measure, or characterization of a state or its residents.",
            "overlap_rule": "One source record is counted once in total counts even when its incident-type field contains multiple semicolon-delimited labels.",
            "missing_geometry": "Records without trustworthy coordinates remain in state aggregation when a state can be resolved, but are omitted from the point layer.",
            "state_filtering": "State shading/filter totals use geometry-independent state aggregates, including state-known records that lack point geometry.",
            "source_boundary": "ADL classifications are presented as ADL classifications with source and snapshot status visible.",
        },
        "refresh": {
            "canonical_input": "official ADL H.E.A.T. CSV export",
            "importer": "scripts/import_adl_heat.py",
            "output_geojson": "data/world-incidents/adl-heat/incidents.geo.json",
            "output_state_summary": "data/world-incidents/adl-heat/state-summary.json",
        },
    }

    summary_doc = {
        "version": "1.0.0",
        "record_type": "adl-heat-state-summary",
        "dataset_id": "adl-heat",
        "snapshot_status": "official-export",
        "dataset": args.dataset_label,
        "total_records": source_rows,
        "total_geocoded_records": len(features),
        "years": years,
        "states": state_rows,
    }
    geo = {
        "type": "FeatureCollection",
        "metadata": {
            "dataset_id": "adl-heat",
            "snapshot_status": "official-export",
            "dataset": args.dataset_label,
            "source_owner": "Anti-Defamation League / Center on Extremism",
            "date_start": dated[0] if dated else None,
            "date_end": dated[-1] if dated else None,
        },
        "features": features,
    }

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (out_dir / "state-summary.json").write_text(json.dumps(summary_doc, indent=2) + "\n", encoding="utf-8")
    (out_dir / "incidents.geo.json").write_text(json.dumps(geo, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {source_rows} rows · {len(features)} geocoded · {missing_geometry} without point geometry")
    print(f"Snapshot: {dated[0] if dated else 'undated'} → {dated[-1] if dated else 'undated'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
