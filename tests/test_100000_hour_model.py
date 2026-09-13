from datetime import datetime, timedelta
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "knowledge" / "timeline" / "100000-hour-counting-models.json"


def load_model():
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def modeled_hours(at, start, hours_per_day):
    elapsed = max(timedelta(0), at - start)
    return elapsed.total_seconds() / 86400 * hours_per_day


def test_flat_model_crossing_and_partition_invariants():
    model = load_model()
    start = datetime.fromisoformat(model["anchor"]["model_assumption"].split("=", 1)[-1].strip())
    rate = model["flat_model"]["hours_per_calendar_day"]
    crossing = datetime.fromisoformat(model["flat_model"]["modelled_100000_crossing"])
    handoff = datetime.fromisoformat(model["provisional_partition"]["handoff"])

    assert rate == 18
    assert abs(modeled_hours(crossing, start, rate) - 100000) < 1e-9

    son = modeled_hours(handoff, start, rate)
    later = datetime.fromisoformat("2026-09-13T20:00:00+02:00")
    total = modeled_hours(later, start, rate)
    father = total - son

    assert son > 0
    assert father > 0
    assert abs((son + father) - total) < 1e-9


def test_preserved_counts_remain_distinct():
    counts = load_model()["preserved_counts"]
    values = [item["hours"] for item in counts]
    assert values == [100000, 107000, 109000, 112542, 115000]
    assert len(values) == len(set(values))
