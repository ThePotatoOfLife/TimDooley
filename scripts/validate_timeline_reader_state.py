#!/usr/bin/env python3
"""Validate shareable/persistable state for the long Timeline reader."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "app" / "long-chronology.js"
PAGE = ROOT / "timeline" / "index.html"

def main() -> int:
    errors = []
    js = RUNTIME.read_text(encoding="utf-8", errors="replace")
    page = PAGE.read_text(encoding="utf-8", errors="replace")

    required = (
        "const initialParams=new URLSearchParams(location.search)",
        "const requestedSources=parseList('sources',allowedSources)",
        "const requestedEras=parseList('eras',allowedEras)",
        "initialParams.get('domain')",
        "initialParams.get('family')",
        "initialParams.get('clock')",
        "initialParams.get('q')",
        "initialParams.get('detail')==='1'",
        "initialParams.get('sort')==='desc'",
        "function syncUrl()",
        "history.replaceState(null,'',u)",
        "function syncControlValues()",
        "raw==='none'",
        "state.sources.size?[...state.sources].sort().join(','):'none'",
        "state.eras.size?[...state.eras].sort().join(','):'none'",
    )
    for marker in required:
        if marker not in js:
            errors.append(f"Timeline reader lost shareable-state marker: {marker}")

    if "allowedModes=new Set(['arc','road','faith','foundations','project'])" not in js:
        errors.append("Timeline reader lost legacy/current mode compatibility")

    for marker in (
        'id="chronSearch"',
        'id="chronDomain"',
        'id="chronFamily"',
        'id="chronClock"',
        'id="chronDetail"',
        'id="chronSort"',
        'Underlying timeline records',
        '../data/timeline-events.json',
    ):
        if marker not in page:
            errors.append(f"Timeline page lost reader/fallback marker: {marker}")

    if errors:
        print("TIMELINE READER STATE VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("Timeline reader state: PASS · mode/filter/search/detail/sort state is reloadable and shareable")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
