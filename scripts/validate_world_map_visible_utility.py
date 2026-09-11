#!/usr/bin/env python3
"""Regression contract for the visibly useful World Relational Atlas surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "world-map" / "3d-bootstrap.js"
LENSES = ROOT / "world-map" / "3d-lenses.js"
METRICS = ROOT / "world-map" / "3d-metrics.js"

REQUIRED_METRICS = (
    "population",
    "area",
    "gdp",
    "gdp_per_capita",
    "real_growth",
    "inflation",
    "unemployment",
    "life_expectancy",
    "urbanization",
    "internet_penetration",
    "co2_emissions",
)


def main() -> int:
    errors = []
    for path in (BOOTSTRAP, LENSES, METRICS):
        if not path.exists():
            errors.append(f"missing visible-utility runtime: {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1

    bootstrap = BOOTSTRAP.read_text(encoding="utf-8", errors="replace")
    lenses = LENSES.read_text(encoding="utf-8", errors="replace")
    metrics = METRICS.read_text(encoding="utf-8", errors="replace")

    for marker in (
        "loadAfterPaint('Metrics', './3d-metrics.js')",
        "Country selection",
        "Lenses",
    ):
        if marker not in bootstrap:
            errors.append(f"bootstrap missing visible-utility marker: {marker}")

    for marker in (
        "atlasLensQuick",
        "Quick Lens",
        "__potatoAtlasMetrics",
        "Metric ·",
        "metric-loading",
    ):
        if marker not in lenses:
            errors.append(f"lenses missing visible-utility marker: {marker}")

    for marker in (
        "__potatoAtlasMetrics",
        "data/countries/index.json",
        "metricValue",
        "metricHas",
        "metricPeriod",
        "metricSource",
        "potato-atlas-metrics-ready",
        "potato-atlas-metric-progress",
    ):
        if marker not in metrics:
            errors.append(f"metrics runtime missing marker: {marker}")

    for metric_id in REQUIRED_METRICS:
        if f"'{metric_id}'" not in metrics and f'\"{metric_id}\"' not in metrics:
            errors.append(f"metrics runtime missing required metric id: {metric_id}")
        if metric_id not in lenses:
            errors.append(f"Lens UI missing required metric option: {metric_id}")

    # The metric runtime must stay lazy and same-origin: no browser-side World Bank
    # or other third-party API calls. Canonical country records remain source of truth.
    forbidden = ("api.worldbank.org", "restcountries.com", "query.wikidata.org")
    for token in forbidden:
        if token in metrics:
            errors.append(f"metrics runtime regressed to browser-side external API dependency: {token}")

    if "Promise.all(" in metrics and "countries.map" in metrics:
        errors.append("metrics runtime appears to fan out all country fetches at once; use bounded concurrency")

    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1

    print("Visible Atlas utility contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
