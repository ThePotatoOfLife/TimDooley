#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HYDRO = ROOT / 'world-map' / '3d-physical-hydrology.js'


def main() -> int:
    text = HYDRO.read_text(encoding='utf-8', errors='replace')
    errors = []
    required = (
        'function hydrologyRequestKey',
        'function shouldSkipHydrologyRequest',
        'activeRequestKey',
        'completedRequestKey',
        'hydrologyRequests',
        'hydrologyDeduplicatedRefreshes',
        'hydrologyAbortedRequests',
        'toFixed(2)',
    )
    for token in required:
        if token not in text:
            errors.append(f'missing hydrology dedupe marker: {token}')
    if 'if (shouldSkipHydrologyRequest(requestKey))' not in text:
        errors.append('hydrology refresh must skip an identical in-flight/completed request key')
    if 'completedRequestKey = requestKey' not in text:
        errors.append('successful hydrology refresh must remember its completed request key')
    if 'activeRequestKey = null' not in text:
        errors.append('hydrology refresh must clear active request ownership after completion/failure')
    if errors:
        print('WORLD MAP HYDROLOGY DEDUPE VALIDATION FAILED')
        for error in errors:
            print('-', error)
        return 1
    print('WORLD MAP HYDROLOGY DEDUPE VALIDATION PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
