#!/usr/bin/env python3
"""Collapse exact duplicate public question intents into one canonical answer.

The discovery builder may surface the same human question from multiple source
indexes under different IDs. This pass keeps the richest generated answer
indexable and rewrites weaker duplicate URLs as noindex/follow aliases with a
canonical link to the selected answer. It runs before final SEO sitemap
construction, so aliases remain crawlable for discovery but are excluded from
indexable sitemap coverage.
"""
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = "https://thepotatooflife.github.io/TimDooley"

H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
SCRIPT_RE = re.compile(r"<script\b.*?</script>", re.I | re.S)
STYLE_RE = re.compile(r"<style\b.*?</style>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")


def visible_text(text: str) -> str:
    text = SCRIPT_RE.sub(" ", text)
    text = STYLE_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    return " ".join(html.unescape(text).split())


def question_label(text: str) -> str:
    match = H1_RE.search(text)
    return " ".join(html.unescape(TAG_RE.sub(" ", match.group(1))).split()) if match else ""


def normalize_question(value: str) -> str:
    value = html.unescape(value).casefold().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def content_score(text: str) -> tuple[int, int]:
    visible = visible_text(text)
    full_answer_bonus = 1 if "Full answer" in visible else 0
    return full_answer_bonus, len(visible)


def route_for(path: Path) -> str:
    return path.parent.relative_to(OUT).as_posix().strip("/")


def alias_page(question: str, canonical_url: str) -> str:
    safe_question = html.escape(question)
    safe_url = html.escape(canonical_url, quote=True)
    js_url = json.dumps(canonical_url)
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_question} — Canonical question</title>
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="{safe_url}">
<meta http-equiv="refresh" content="0; url={safe_url}">
</head><body>
<main data-tts-longform><p>This question is indexed at <a href="{safe_url}">{safe_question}</a>.</p></main>
<script>location.replace({js_url})</script>
<script src="https://thepotatooflife.github.io/TimDooley/app/site-tts.js" defer></script>
</body></html>'''


def main() -> int:
    root = OUT / "questions"
    if not root.exists():
        print("No built questions directory; nothing to deduplicate")
        return 0

    groups: defaultdict[str, list[tuple[Path, str, str]]] = defaultdict(list)
    for path in sorted(root.glob("*/index.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if '"@type": "FAQPage"' not in text and '"@type":"FAQPage"' not in text:
            continue
        question = question_label(text)
        key = normalize_question(question)
        if key:
            groups[key].append((path, question, text))

    aliases: list[dict[str, str]] = []
    duplicate_groups = 0
    for rows in groups.values():
        if len(rows) < 2:
            continue
        duplicate_groups += 1
        canonical_path, question, canonical_text = max(rows, key=lambda row: content_score(row[2]))
        canonical_route = route_for(canonical_path)
        canonical_url = f"{BASE_URL}/{canonical_route}/"
        for path, alias_question, _text in rows:
            if path == canonical_path:
                continue
            alias_route = route_for(path)
            path.write_text(alias_page(alias_question or question, canonical_url), encoding="utf-8")
            aliases.append({
                "alias": f"{BASE_URL}/{alias_route}/",
                "canonical": canonical_url,
                "question": question,
            })

    report = {
        "duplicate_question_groups": duplicate_groups,
        "aliases_created": len(aliases),
        "aliases": aliases,
    }
    (OUT / "question-alias-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Question intent dedup: {duplicate_groups} duplicate groups · {len(aliases)} aliases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
