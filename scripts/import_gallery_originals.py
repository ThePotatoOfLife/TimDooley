#!/usr/bin/env python3
"""Import high-quality PNG originals into the chronological art gallery.

Usage:
  python scripts/import_gallery_originals.py /path/to/exported/originals --dry-run
  python scripts/import_gallery_originals.py /path/to/exported/originals --apply

This does not synthesize pixels or upscale existing thumbnails.
Requires Pillow: python -m pip install Pillow
"""
import argparse
import html
import json
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "rooms/inside/visual-art/index.html"
CATALOGUE = ROOT / "knowledge/creative/chatgpt-library-originals-inventory-2026-10-10.json"
DEST = ROOT / "assets/visual-art/originals"
LOOKUP = {
    "majestic king arrival": "majestic-king-arrival",
    "divine gardener with potato": "divine-gardener-with-potato",
    "modern holy portrait": "modern-holy-portrait",
    "god at vending machine": "god-at-vending-machine",
    "royal portrait hallway": "royal-portrait-hallway",
    "divine philosophical contemplation": "divine-philosophical-contemplation",
    "godly robes transformation": "godly-robes-transformation",
    "rising lion revelation": "rising-lion-revelation",
    "farmers brunch delight": "farmers-brunch-delight",
    "royal debate on potatoes": "royal-debate-on-potatoes",
    "royal bartender scene": "royal-bartender-scene",
    "royal grief and vengeance": "royal-grief-and-vengeance",
    "bearded man in car": "bearded-man-in-car",
    "king wizard showdown": "king-wizard-showdown",
    "royal at jesus": "royal-at-jesus-tomb",
}
def clean(s):
    s = s.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, help="Folder containing original PNG exports")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not args.source.is_dir():
        ap.error("Source folder does not exist")
    page = PAGE.read_text(encoding="utf-8")
    imported = []
    seen = set()
    for file in sorted(args.source.rglob("*.png")):
        normalized = clean(file.stem)
        slug = next((v for k, v in LOOKUP.items() if k in normalized), None)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        with Image.open(file) as im:
            im.verify()
        with Image.open(file) as im:
            w, h = im.size
            if w < 1000 or h < 700:
                print(f"SKIP low-resolution: {file.name}: {w}x{h}")
                continue
            dest = DEST / (slug + ".png")
            expected = f"../../../assets/visual-art/originals/{slug}.png"
            # Update ONLY the artwork matched by its existing card ID.
            pattern = re.compile(r'(<figure\\b(?=[^>]*\\bid="art-' + re.escape(slug) + r'")[\\s\\S]*?</figure>)')
            match = pattern.search(page)
            if not match:
                print(f"STAGED (no gallery card yet): {file.name}")
            if args.apply:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(file.read_bytes())
                if match:
                    card = match.group(1)
                    card_new = re.sub(r'(<img\\b[^>]*\\bsrc=")[^"]+(")', lambda m: m.group(1) + html.escape(expected) + m.group(2), card, count=1)
                    page = page[:match.start()] + card_new + page[match.end():]
            imported.append(dict(source=file.name, path=dest.relative_to(ROOT).as_posix(), width=w, height=h, bytes=file.stat().st_size, cardMatched=bool(match)))
            print(f"{'IMPORT' if args.apply else 'WOULD IMPORT'} {file.name} -> {dest.relative_to(ROOT)} ({w}x{h})")
    if args.apply:
        PAGE.write_text(page, encoding="utf-8")
        (ROOT / "knowledge/creative/gallery-import-report.json").write_text(json.dumps(imported, indent=2) + "\\n", encoding="utf-8")
    print(f"Candidates: {len(imported)}. Originals are kept without recompression.")

if __name__ == "__main__":
    main()
