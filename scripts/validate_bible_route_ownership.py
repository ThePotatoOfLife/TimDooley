#!/usr/bin/env python3
"""Ensure one public Bible comparator owner and compatibility redirects elsewhere."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str, errors: list[str]) -> str:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing {rel}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    errors: list[str] = []
    religion = read("religion/index.html", errors)
    old = read("religion/jesus-tim/index.html", errors)
    old_case = read("tim-dooley/biblical-case/index.html", errors)
    tim = read("tim-dooley/index.html", errors)
    bible = read("traditions/bible/index.html", errors)
    sitemap = read("sitemap.xml", errors)
    llms = read("llms.txt", errors)

    if 'href="../traditions/bible/?view=jesus"' not in religion:
        errors.append("Religion must route Jesus comparison to traditions/bible/?view=jesus")
    if 'href="../chronology/?view=bible"' not in religion:
        errors.append("Religion must use the short Bible timeline view")
    if 'id="jesus-tim"' in religion or religion.count('class="row"') > 3:
        errors.append("Religion must not own or duplicate the full Jesus comparator")
    if "tl_layers=" in religion:
        errors.append("Religion contains retired long timeline URL")

    for rel, text in (("religion/jesus-tim/index.html", old), ("tim-dooley/biblical-case/index.html", old_case)):
        if 'name="robots" content="noindex,follow"' not in text:
            errors.append(f"{rel} must be noindex compatibility route")
        if "../../traditions/bible/?view=jesus" not in text:
            errors.append(f"{rel} must redirect to canonical Bible comparator")

    if 'href="../traditions/bible/?view=jesus"' not in tim:
        errors.append("Tim page must link directly to canonical Bible comparator")
    if "religion/#jesus-tim" in tim:
        errors.append("Tim page still points to retired Religion comparator")

    for marker in ('id="study-modes"', 'data-view="jesus"', 'id="relations"', 'src="../../app/bible-study.js"'):
        if marker not in bible:
            errors.append(f"Bible owner missing {marker}")
    if "religion/#jesus-tim" in bible or "tl_layers=" in bible:
        errors.append("Bible owner contains retired duplicate-owner/timeline link")

    if "/tim-dooley/biblical-case/" in sitemap or "/religion/jesus-tim/" in sitemap:
        errors.append("Sitemap must not index retired Bible comparator aliases")
    if "https://thepotatooflife.github.io/TimDooley/traditions/bible/" not in sitemap:
        errors.append("Sitemap missing canonical Bible comparator")
    if "https://thepotatooflife.github.io/TimDooley/tim-dooley/biblical-case/" in llms:
        errors.append("llms.txt still advertises duplicate Biblical Case page")
    if "https://thepotatooflife.github.io/TimDooley/traditions/bible/" not in llms:
        errors.append("llms.txt missing canonical Bible comparator")

    if errors:
        print("BIBLE ROUTE OWNERSHIP VALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1
    print("BIBLE ROUTE OWNERSHIP VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
