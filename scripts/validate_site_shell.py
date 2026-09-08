#!/usr/bin/env python3
"""Verify the generated Pages artifact has one canonical, consistent site shell."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
HEADER_RE = re.compile(r'<header\b[^>]*data-site-header=["\']canonical["\'][^>]*>.*?</header>', re.I | re.S)
ALL_HEADER_RE = re.compile(r'<header\b[^>]*>', re.I)
NAV_LINK_RE = re.compile(r'<a\b([^>]*)data-nav=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
ROOT_TOKEN_RE = re.compile(r'(?P<root>\.\./)*index\.html')

EXPECTED_NAV = [
    ("home", "index.html", "Home"),
    ("repository", "repository.html", "Repository"),
    ("timeline", "timeline.html", "Timeline"),
    ("world", "nations.html", "World"),
    ("people", "people.html", "People"),
    ("ideas", "belief.html", "Ideas"),
    ("books", "books.html", "Books"),
    ("potatoism", "potatoism.html", "Potatoism"),
    ("movements", "extremism.html", "Movements"),
    ("hawkins", "hawkins.html", "Hawkins"),
]

errors: list[str] = []


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def check_nav(page: Path, header: str) -> None:
    links = NAV_LINK_RE.findall(header)
    actual = [(key, normalize(attrs), normalize(label)) for attrs, key, label in links]
    keys = [key for key, _, _ in actual]
    expected_keys = [key for key, _, _ in EXPECTED_NAV]
    if keys != expected_keys:
        errors.append(f"{page.relative_to(SITE)}: navigation keys differ from canonical order: {keys}")

    for (key, _, label), (_, expected_href, expected_label) in zip(actual, EXPECTED_NAV):
        if label != expected_label:
            errors.append(f"{page.relative_to(SITE)}: {key} label is {label!r}, expected {expected_label!r}")
        match = re.search(r'href=["\']([^"\']+)["\']', actual[expected_keys.index(key)][1], re.I)
        if not match:
            errors.append(f"{page.relative_to(SITE)}: {key} has no href")
        elif not match.group(1).endswith(expected_href):
            errors.append(f"{page.relative_to(SITE)}: {key} href is {match.group(1)!r}, expected suffix {expected_href!r}")


def main() -> int:
    if not SITE.exists():
        errors.append("_site does not exist; build_site.py must run first")
    else:
        pages = sorted(SITE.rglob("*.html"))
        if not pages:
            errors.append("_site contains no HTML pages")
        for page in pages:
            text = page.read_text(encoding="utf-8", errors="replace")
            canonical = HEADER_RE.findall(text)
            all_headers = ALL_HEADER_RE.findall(text)
            legacy_count = len(all_headers) - len(canonical)
            if len(canonical) != 1:
                errors.append(f"{page.relative_to(SITE)}: expected exactly one canonical header, found {len(canonical)}")
                continue
            if legacy_count:
                errors.append(f"{page.relative_to(SITE)}: {legacy_count} legacy/non-canonical header(s) remain")
            check_nav(page, canonical[0])

    count = len(list(SITE.rglob("*.html"))) if SITE.exists() else 0
    print(f"Built HTML pages checked: {count}")
    if errors:
        print("SITE SHELL VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("SITE SHELL VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
