#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "traditions/bible/index.html"
LOADER = ROOT / "app/bible-mining-loader.js"
ROUTING = ROOT / "knowledge/indexes/biblical-mining-wave23-routing.json"
LEGACY = (
    "bible-mining-wave19-loader.js",
    "bible-mining-wave20-loader.js",
    "bible-mining-wave22-loader.js",
    "bible-mining-wave23-loader.js",
)


def fail(message: str) -> None:
    raise SystemExit(f"BIBLE MINING LOADER FAILED: {message}")


def main() -> int:
    if not LOADER.exists():
        fail("missing app/bible-mining-loader.js")

    page = PAGE.read_text(encoding="utf-8")
    loader = LOADER.read_text(encoding="utf-8")
    routing = ROUTING.read_text(encoding="utf-8")

    marker = 'src="../../app/bible-mining-loader.js"'
    if page.count(marker) != 1:
        fail("Bible page must load exactly one unified mining loader")
    if page.find(marker) > page.find('src="../../app/bible-dossier-loader.js"'):
        fail("mining loader must run before dossier decorator")

    for legacy in LEGACY:
        if legacy in page:
            fail(f"Bible page still references legacy loader {legacy}")
        if legacy in routing:
            fail(f"routing metadata still names legacy loader {legacy}")

    for wave in (19, 20, 22, 23, 24, 25):
        dossier = f"biblical-syncretism-dossiers-wave{wave}.json"
        fragments = f"biblical-passage-fragments-wave{wave}.json"
        if dossier not in loader or fragments not in loader:
            fail(f"unified loader missing wave {wave} dossier/fragment pair")

    if loader.count("window.fetch=") != 1:
        fail("unified loader must install exactly one fetch interceptor")
    for required in ("mergeLayer", "mergeFragments", "Promise.all", "upstreamFetch"):
        if required not in loader:
            fail(f"unified loader missing {required}")

    if '"owner":"app/bible-mining-loader.js"' not in routing:
        fail("wave23 routing metadata must point reader integration at unified loader")

    print("BIBLE MINING LOADER PASSED: one ordered extension pipeline covers waves 19,20,22-25")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
