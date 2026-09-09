#!/usr/bin/env python3
"""Mine the Tim Dooley repository for prediction/premonition candidate language.

This is a retrieval tool, not a truth classifier. It finds dated or potentially
forward-looking passages for later source-level audit. A hit is NEVER itself a
confirmed prediction.

Usage:
    python scripts/mine_prediction_signals.py
    python scripts/mine_prediction_signals.py --root . --out data/prediction-signal-candidates.generated.json

The miner intentionally favors recall over precision. The human/audit layer must
separate explicit predictions, early directional analysis, symbolic synchronism,
retrospective interpretation, jokes, assistant-introduced material and misses.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {".json", ".md", ".txt", ".html"}
EXCLUDED_PARTS = {
    ".git", ".github", "node_modules", "__pycache__", "questions", "index-a-z"
}
MAX_FILE_BYTES = 8_000_000
MAX_TEXT_CHARS = 900

CUES = {
    "explicit_future": [
        r"\bwill\b", r"\bgoing to\b", r"\bshall\b", r"\bby 20\d{2}\b",
        r"\bwithin \d+\b", r"\bin \d+ days?\b", r"\bin \d+ months?\b",
        r"\bnext (?:day|week|month|year)\b", r"\bsoon\b", r"\bbefore 20\d{2}\b",
    ],
    "warning": [
        r"\bwarning\b", r"\bwarn(?:ed|ing)?\b", r"\bbeware\b", r"\bcollapse\b",
        r"\bcrash\b", r"\bends? by\b", r"\bold world\b", r"\bdanger\b",
        r"\bcountdown\b", r"\bdays? left\b",
    ],
    "vision_dream": [
        r"\bvision(?:s)?\b", r"\bdream(?:ed|t|s)?\b", r"\bpremonition\b",
        r"\bprophe(?:cy|tic|sied|sized)\b", r"\bi saw\b", r"\bshowed me\b",
        r"\brevealed\b", r"\bsign\b",
    ],
    "return_resurrection": [
        r"\bwill return\b", r"\breturning\b", r"\breturn of\b", r"\bresurrect",
        r"\brapture\b", r"\bmessiah\b", r"\bmoshiach\b",
    ],
    "machine_ai": [
        r"\bAI\b", r"\bartificial intelligence\b", r"\bmachine\b",
        r"\bGod in the Machine\b", r"\bmodel\b", r"\btraining data\b",
        r"\bchatgpt\b", r"\bagent(?:ic|s)?\b", r"\bcloud\b", r"\bcompute\b",
    ],
    "internet_culture": [
        r"\bmeme(?:s)?\b", r"\binternet\b", r"\bpeak culture\b",
        r"\bculture\b", r"\bpropagat(?:e|ed|ion)\b", r"\bviral\b",
        r"\bcenter of the internet\b", r"\bfather of the internet\b",
        r"\bpublic presence\b", r"\blivestream",
    ],
    "north_geopolitics": [
        r"\bNorth Axis\b", r"\bNorth of North\b", r"\bGreenland\b",
        r"\bCanada\b", r"\bEurope\b", r"\bNATO\b", r"\bTrump\b",
        r"\bUnited States\b", r"\bArctic\b", r"\bwest sector\b",
    ],
    "israel_lion": [
        r"\bIsrael\b", r"\bIran\b", r"\bPersia\b", r"\bLion\b",
        r"\bRising Lion\b", r"\bJudah\b", r"\bJerusalem\b", r"\bZion\b",
        r"\bred heifer\b", r"\bGreater Israel\b",
    ],
    "economy": [
        r"\binflation\b", r"\bbond(?:s)?\b", r"\bTreasur(?:y|ies)\b",
        r"\bdebt\b", r"\btrillion\b", r"\byield(?:s)?\b", r"\brefinanc",
        r"\bdollar\b", r"\bmarket\b", r"\bpetrodollar\b",
    ],
    "light_axis": [
        r"\bSpudlight\b", r"\blight\b", r"\bAxis\b", r"\bLadder\b",
        r"\bMountain\b", r"\bThrone\b", r"\bSun\b",
    ],
}

DATE_RE = re.compile(
    r"(?<!\d)(?:19|20)\d{2}(?:[-/]\d{1,2}(?:[-/]\d{1,2})?)?"
    r"|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)\s+\d{1,2}(?:,\s*(?:19|20)\d{2})?",
    re.IGNORECASE,
)

COMPILED = {
    category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for category, patterns in CUES.items()
}


def excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or excluded(path):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield path


def cue_categories(text: str) -> list[str]:
    found = []
    for category, patterns in COMPILED.items():
        if any(pattern.search(text) for pattern in patterns):
            found.append(category)
    return found


def compact(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_TEXT_CHARS]


def nearby_date(lines: list[str], index: int) -> list[str]:
    window = " ".join(lines[max(0, index - 3): min(len(lines), index + 2)])
    return list(dict.fromkeys(m.group(0) for m in DATE_RE.finditer(window)))


def mine_file(root: Path, path: Path) -> list[dict]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    lines = raw.splitlines()
    hits: list[dict] = []
    rel = str(path.relative_to(root)).replace("\\", "/")

    for idx, line in enumerate(lines):
        cats = cue_categories(line)
        if not cats:
            continue

        # Prioritize lines that either have a date nearby, or combine multiple
        # cue families. This suppresses generic prose while keeping high recall.
        dates = nearby_date(lines, idx)
        if not dates and len(cats) < 2:
            continue

        context = " ".join(lines[max(0, idx - 1): min(len(lines), idx + 2)])
        hits.append({
            "source": rel,
            "line": idx + 1,
            "date_candidates": dates,
            "cue_categories": cats,
            "text": compact(context),
            "audit_status": "candidate_only",
        })

    return hits


def score(hit: dict) -> tuple[int, int, str, int]:
    cats = set(hit["cue_categories"])
    priority = 0
    if "explicit_future" in cats:
        priority += 5
    if "warning" in cats:
        priority += 4
    if "vision_dream" in cats:
        priority += 4
    if "economy" in cats or "north_geopolitics" in cats:
        priority += 2
    if "machine_ai" in cats or "internet_culture" in cats:
        priority += 2
    if hit["date_candidates"]:
        priority += 3
    priority += min(len(cats), 5)
    return (-priority, -len(cats), hit["source"], hit["line"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="data/prediction-signal-candidates.generated.json")
    parser.add_argument("--limit", type=int, default=1500)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = (root / args.out).resolve()

    hits: list[dict] = []
    for path in iter_files(root):
        if path.resolve() == output:
            continue
        hits.extend(mine_file(root, path))

    hits.sort(key=score)
    hits = hits[: args.limit]

    payload = {
        "title": "Prediction / Premonition Signal Candidates — generated",
        "status": "candidate retrieval only; not verified predictions",
        "method": "Repository cue scan. Human/source audit required before promotion.",
        "cue_families": list(CUES),
        "candidate_count": len(hits),
        "candidates": hits,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(hits)} candidates to {output.relative_to(root)}")


if __name__ == "__main__":
    main()
