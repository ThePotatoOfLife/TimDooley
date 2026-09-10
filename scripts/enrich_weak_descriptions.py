#!/usr/bin/env python3
"""Expand weak meta descriptions in the completed static site.

This pass only touches descriptions shorter than 40 characters. It prefers the
first substantial paragraph already present on the page and otherwise derives a
plain, non-promotional description from the page title. Curated descriptions of
reasonable length are left unchanged.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
SITE_NAME = "The Potato of Life"

META_RE = re.compile(r"<meta\b[^>]*>", re.I)
ATTR_RE = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.I | re.S)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
P_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")


def attrs(tag: str) -> dict[str, str]:
    return {m.group(1).lower(): html.unescape(m.group(3)).strip() for m in ATTR_RE.finditer(tag)}


def clean(fragment: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub(" ", fragment)).split())


def clip(value: str, limit: int = 165) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    cut = value[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return (cut or value[:limit]).rstrip() + "…"


def title_for(text: str, page: Path) -> str:
    for regex in (TITLE_RE, H1_RE):
        match = regex.search(text)
        if match:
            value = clean(match.group(1))
            if value:
                return value
    rel = page.parent.relative_to(OUT)
    if rel == Path("."):
        return SITE_NAME
    return " ".join(part.replace("-", " ").title() for part in rel.parts)


def generated_description(text: str, page: Path) -> str:
    for match in P_RE.finditer(text):
        value = clean(match.group(1))
        if len(value) >= 60:
            return clip(value)
    title = title_for(text, page)
    return clip(
        f"Explore {title} in the {SITE_NAME} archive, including connected records, chronology, sources, evidence and related context."
    )


def replace_weak_description(text: str, page: Path) -> tuple[str, bool]:
    for tag in META_RE.findall(text):
        a = attrs(tag)
        if a.get("name", "").lower() != "description":
            continue
        current = a.get("content", "").strip()
        if len(current) >= 40:
            return text, False
        replacement = generated_description(text, page)
        new_tag = re.sub(
            r"\bcontent\s*=\s*([\"']).*?\1",
            f'content="{html.escape(replacement, quote=True)}"',
            tag,
            count=1,
            flags=re.I | re.S,
        )
        if new_tag == tag:
            new_tag = tag[:-1] + f' content="{html.escape(replacement, quote=True)}">'
        return text.replace(tag, new_tag, 1), True
    return text, False


def main() -> None:
    if not OUT.exists():
        raise SystemExit("_site does not exist; run the site builders first")
    changed = []
    for page in sorted(OUT.rglob("index.html")):
        text = page.read_text(encoding="utf-8", errors="replace")
        updated, did_change = replace_weak_description(text, page)
        if did_change:
            page.write_text(updated, encoding="utf-8")
            changed.append(page.relative_to(OUT).as_posix())
    print(f"Enriched {len(changed)} weak meta descriptions")
    for path in changed:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
