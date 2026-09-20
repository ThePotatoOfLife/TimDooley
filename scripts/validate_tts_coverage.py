#!/usr/bin/env python3
"""Validate project-wide TTS coverage and long-form reader contracts."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SURFACES = ROOT / "data/house/public-surfaces.json"

GENERATED = {"questions", "index-a-z"}
QUIET = {"world-map", "inhabitants"}
SPECIALIST = {"tim", "story", "religion", "philosophy", "axis", "north", "bible"}
LONGFORM_REQUIRED = {"tim", "story", "religion", "philosophy", "axis", "north"}

DIRECT_MARKERS = ("app/site-tts.js", "data-tts-longform", "tts-drawer.js")
INHERITED_MARKER = "app/house-journey.js"

def route_to_path(route: str) -> Path:
    route = route.strip("/")
    if not route:
        return ROOT / "index.html"
    if route.endswith(".html"):
        return ROOT / route
    return ROOT / route / "index.html"

def covered(text: str) -> bool:
    return any(marker in text for marker in DIRECT_MARKERS) or INHERITED_MARKER in text

def validate_built_site(errors: list[str], notes: list[str]) -> None:
    out = ROOT / "_site"
    if not out.exists():
        notes.append("_site not present; built-site TTS audit skipped")
        return
    quiet_prefixes = ("world-map/", "rooms/objects/", "index-a-z/", "tools/tts/")
    checked = 0
    for path in out.rglob("*.html"):
        rel = path.relative_to(out).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if not ("<html" in text.lower() and "<main" in text.lower()):
            continue
        if rel.startswith(quiet_prefixes):
            continue
        checked += 1
        if not (
            "site-tts.js" in text
            or "data-tts-longform" in text
            or "tts-drawer.js" in text
        ):
            errors.append(f"built page missing TTS coverage: {rel}")
    notes.append(f"built-site TTS documents checked: {checked}")

def main() -> int:
    errors: list[str] = []
    notes: list[str] = []
    if not SURFACES.exists():
        print("missing public surface registry")
        return 1

    data = json.loads(SURFACES.read_text(encoding="utf-8"))
    active = [s for s in data.get("surfaces", []) if s.get("status") == "active"]

    for surface in active:
        sid = surface["id"]
        path = route_to_path(surface["route"])
        if sid in GENERATED and not path.exists():
            notes.append(f"{sid}: generated at build time")
            continue
        if not path.exists():
            errors.append(f"{sid}: missing public HTML at {path.relative_to(ROOT)}")
            continue

        text = path.read_text(encoding="utf-8")
        if sid in QUIET:
            notes.append(f"{sid}: intentionally quiet explorer; use selected-content TTS")
            continue

        if not covered(text):
            errors.append(
                f"{sid}: no direct site TTS, declarative/specialist TTS, or inherited house-journey TTS"
            )

        if sid in LONGFORM_REQUIRED and "data-tts-longform" not in text:
            errors.append(f"{sid}: expected explicit long-form TTS contract")

    site_tts = ROOT / "app/site-tts.js"
    if not site_tts.exists():
        errors.append("missing app/site-tts.js")
    else:
        text = site_tts.read_text(encoding="utf-8")
        for marker in ("QUIET_ROUTES", "INTERACTIVE_EXCLUDE", "data-tts-longform", "PotatoLongformTTS"):
            if marker not in text:
                errors.append(f"app/site-tts.js missing {marker}")

    journey = ROOT / "app/house-journey.js"
    if not journey.exists() or "site-tts.js" not in journey.read_text(encoding="utf-8"):
        errors.append("app/house-journey.js must load app/site-tts.js")

    longform = ROOT / "app/longform-tts-adapter.js"
    if not longform.exists():
        errors.append("missing long-form TTS adapter")
    else:
        text = longform.read_text(encoding="utf-8")
        for marker in ("MutationObserver", "potato:tts-prepare", "mountSelectionAction", "createPageHighlighter"):
            if marker not in text:
                errors.append(f"long-form adapter missing {marker}")

    gb = ROOT / "app/great-book-reader.js"
    if not gb.exists():
        errors.append("missing Great Book reader")
    else:
        text = gb.read_text(encoding="utf-8")
        if "potato:tts-prepare" not in text or "loadAllSlots" not in text:
            errors.append("Great Book reader must prepare all lazy chapters for whole-book TTS")

    drawer = ROOT / "app/tts-drawer.js"
    if not drawer.exists():
        errors.append("missing TTS drawer")
    else:
        text = drawer.read_text(encoding="utf-8")
        for marker in ("followReading", "voiceIdentity", "mountSelectionAction", "createPageHighlighter"):
            if marker not in text:
                errors.append(f"TTS drawer missing {marker}")

    engine = ROOT / "app/tts-reader.js"
    if not engine.exists():
        errors.append("missing TTS speech engine")
    else:
        text = engine.read_text(encoding="utf-8")
        for marker in ("nextChunk", "watchdog", "autoRecover", "SpeechSynthesis"):
            if marker not in text:
                errors.append(f"TTS engine missing {marker}")

    validate_built_site(errors, notes)

    print(f"checked {len(active)} active public surfaces")
    for note in notes:
        print("NOTE", note)
    if errors:
        for error in errors:
            print("ERROR", error)
        return 1
    print("TTS coverage OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
