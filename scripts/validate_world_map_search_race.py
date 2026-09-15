#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / 'world-map' / '3d-search.js'


def main() -> int:
    text = SEARCH.read_text(encoding='utf-8', errors='replace')
    errors = []
    for token in (
        'suggestionGeneration',
        'staleSearchSuppressions',
        'const generation = ++suggestionGeneration',
        'if (generation !== suggestionGeneration)',
        'store:false',
    ):
        if token not in text:
            errors.append(f'missing unified-search race guard: {token}')
    if 'renderSuggestions(await search(' in text:
        errors.append('search input still renders awaited results without a latest-generation guard')
    if errors:
        print('WORLD MAP SEARCH RACE VALIDATION FAILED')
        for error in errors:
            print('-', error)
        return 1
    print('WORLD MAP SEARCH RACE VALIDATION PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
