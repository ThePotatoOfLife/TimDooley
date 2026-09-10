#!/usr/bin/env python3
"""Validate FAQ backend volumes for structure and duplicate questions."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAQ_FILES = [
    ROOT / "knowledge/indexes/faq-long-tail-bulk.json",
    ROOT / "knowledge/indexes/faq-long-tail-expansion-2026-09-10.json",
    ROOT / "knowledge/indexes/faq-christianity-jesus-eschatology.json",
]


def norm(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    errors: list[str] = []
    seen: dict[str, str] = {}
    total = 0
    families = 0

    for path in FAQ_FILES:
        if not path.exists():
            errors.append(f"missing FAQ backend file: {path.relative_to(ROOT)}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
            continue

        fams = data.get("families")
        if not isinstance(fams, list) or not fams:
            errors.append(f"{path.relative_to(ROOT)}: missing non-empty families array")
            continue

        family_ids: set[str] = set()
        for family in fams:
            families += 1
            fid = family.get("id")
            title = family.get("title")
            items = family.get("items")
            if not isinstance(fid, str) or not fid.strip():
                errors.append(f"{path.relative_to(ROOT)}: family missing id")
                continue
            if fid in family_ids:
                errors.append(f"{path.relative_to(ROOT)}: duplicate family id {fid}")
            family_ids.add(fid)
            if not isinstance(title, str) or not title.strip():
                errors.append(f"{path.relative_to(ROOT)}:{fid}: missing title")
            if not isinstance(items, list) or not items:
                errors.append(f"{path.relative_to(ROOT)}:{fid}: missing items")
                continue

            for i, item in enumerate(items):
                q = item.get("q") if isinstance(item, dict) else None
                a = item.get("a") if isinstance(item, dict) else None
                if not isinstance(q, str) or not q.strip():
                    errors.append(f"{path.relative_to(ROOT)}:{fid}[{i}]: missing question")
                    continue
                if not isinstance(a, str) or len(a.strip()) < 20:
                    errors.append(f"{path.relative_to(ROOT)}:{fid}[{i}]: answer missing or too short")
                total += 1
                key = norm(q)
                where = f"{path.relative_to(ROOT)}:{fid}"
                if key in seen:
                    errors.append(f"duplicate normalized question: {q!r} in {where}; already in {seen[key]}")
                else:
                    seen[key] = where

    print(f"FAQ backend: {total} questions across {families} families in {len(FAQ_FILES)} volumes")
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1
    print("FAQ backend integrity: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
