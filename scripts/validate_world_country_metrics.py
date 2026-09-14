#!/usr/bin/env python3
"""Validate the neutral country-metrics World Map contract."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'scripts' / 'build_world_country_metrics.py'
TEST = ROOT / 'scripts' / 'test_world_country_metrics.py'
MODULE = ROOT / 'world-map' / '3d-country-metrics.js'
LIFECYCLE = ROOT / 'world-map' / '3d-panel-lifecycle.js'


def main() -> int:
    errors = []
    for path in (BUILDER, TEST, MODULE, LIFECYCLE):
        if not path.exists():
            errors.append(f'missing country metrics file: {path.relative_to(ROOT)}')
    if not errors:
        builder = BUILDER.read_text(encoding='utf-8')
        module = MODULE.read_text(encoding='utf-8')
        lifecycle = LIFECYCLE.read_text(encoding='utf-8')
        for token in (
            'world-country-metrics-runtime', 'World Bank World Development Indicators',
            'semantic_role', 'dated-observation', 'axis_score', 'Missing is unknown/unavailable, never zero',
            'gdp_per_capita', 'inflation', 'unemployment', 'life_expectancy', 'internet_penetration',
        ):
            if token not in builder:
                errors.append(f'country metrics builder missing marker: {token}')
        for token in (
            'world-country-metrics.json', 'Comparable indicators', 'missing is unknown, never zero',
            'indicators do not determine Axis height or a country score', '__potatoAtlasCountryMetrics',
        ):
            if token not in module:
                errors.append(f'country metrics browser module missing marker: {token}')
        if 'api.worldbank.org' in module:
            errors.append('country metrics browser module must not call World Bank directly')
        if "Country metrics', './3d-country-metrics.js'" not in lifecycle:
            errors.append('country metrics lazy loading is not registered')
        if 'countryMetricsRequested' not in lifecycle or 'potato-atlas-selection-change' not in lifecycle:
            errors.append('country metrics must remain dormant until country selection')

        test = subprocess.run(
            [sys.executable, '-m', 'unittest', 'scripts.test_world_country_metrics', '-v'],
            cwd=ROOT, capture_output=True, text=True,
        )
        if test.returncode:
            errors.append('country metrics unit contract failed: ' + (test.stderr.strip() or test.stdout.strip()))
        node = subprocess.run(['node','--check',str(MODULE)], cwd=ROOT, capture_output=True, text=True)
        if node.returncode:
            errors.append('3d-country-metrics.js syntax failed: ' + (node.stderr.strip() or node.stdout.strip()))

    if errors:
        print('WORLD COUNTRY METRICS VALIDATION FAILED')
        for error in errors:
            print('-', error)
        return 1
    print('WORLD COUNTRY METRICS VALIDATION PASSED · neutral dated observations · same-origin browser runtime · selection-lazy')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
