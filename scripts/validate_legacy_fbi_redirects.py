#!/usr/bin/env python3
"""Prevent the retired Potatoverse FBI namespace from regaining live dossier ownership."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FBI = ROOT / "rooms/potatoverse-canon/beings/fbi"

ALLOWED_FULL_PAGES = {"index.html"}
REDIRECT_SUBTREES = {"file", "incidents", "bonds"}

def main() -> int:
    errors: list[str] = []
    if not FBI.is_dir():
        print("LEGACY FBI VALIDATION FAILED")
        print("- retired FBI namespace missing")
        return 1

    for path in sorted(FBI.rglob("index.html")):
        rel = path.relative_to(FBI)
        parts = rel.parts
        text = path.read_text(encoding="utf-8", errors="replace")

        if len(parts) == 1 and parts[0] in ALLOWED_FULL_PAGES:
            if "Retired predecessor" not in text or "CIA" not in text:
                errors.append("retired FBI landing page lost migration notice")
            continue

        if len(parts) == 2 and parts[0] in REDIRECT_SUBTREES:
            if "location.replace" not in text or "../cia/" not in text:
                errors.append(f"legacy FBI utility route is no longer a redirect: {rel}")
            continue

        # Every old per-person route must now be compatibility-only.
        if len(parts) == 2:
            if "location.replace" not in text or "../../cia/file/?character=" not in text:
                errors.append(f"legacy FBI person route regained live dossier content: {rel}")
            if "noindex" not in text:
                errors.append(f"legacy FBI person redirect should remain noindex: {rel}")
            continue

        errors.append(f"unexpected live route under retired FBI namespace: {rel}")

    if errors:
        print("LEGACY FBI VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("Legacy FBI namespace: PASS · retired landing + compatibility redirects only")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
