#!/usr/bin/env python3
"""Protect the paired Hall of Heroes / Hall of Shame reader-room implementation."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HERO_PAGE = ROOT / "rooms/potatoverse-canon/beings/potatoes/index.html"
SHAME_PAGE = ROOT / "below/dogs/index.html"
HERO_CSS = ROOT / "app/potatoes-hall.css"
SHAME_CSS = ROOT / "app/dogs-hall.css"
HERO_ART = ROOT / "app/hall-of-heroes.avif"
SHAME_ART = ROOT / "app/hall-of-shame.avif"
BUILD = ROOT / "scripts/build_site.py"

def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def avif_dimensions(path: Path) -> tuple[int, int] | None:
    """Read AVIF primary image dimensions from the ISO-BMFF ispe box."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 32 or data[4:8] != b"ftyp" or b"avif" not in data[:32]:
        return None
    offset = data.find(b"ispe")
    if offset < 0 or offset + 16 > len(data):
        return None
    width = int.from_bytes(data[offset + 8:offset + 12], "big")
    height = int.from_bytes(data[offset + 12:offset + 16], "big")
    if width <= 0 or height <= 0:
        return None
    return width, height

def main() -> int:
    errors: list[str] = []
    for path in (HERO_PAGE, SHAME_PAGE, HERO_CSS, SHAME_CSS, HERO_ART, SHAME_ART):
        if not path.exists():
            errors.append(f"missing Hall asset: {path.relative_to(ROOT)}")

    hero = text(HERO_PAGE)
    shame = text(SHAME_PAGE)
    hero_css = text(HERO_CSS)
    shame_css = text(SHAME_CSS)
    build = text(BUILD)

    hero_markers = (
        'class="hall-scene hall-scene--heroes"',
        'id="great-table"',
        'id="honor-register"',
        'id="hero-source-desk"',
        'id="angel-hall"',
        'id="hall-doors"',
    )
    shame_markers = (
        'class="hall-scene hall-scene--shame"',
        'id="edge-of-town"',
        'id="notoriety-ledger"',
        'id="dog-source-desk"',
        'id="repair-route"',
        'id="shame-doors"',
    )
    for marker in hero_markers:
        if marker not in hero:
            errors.append(f"Hall of Heroes missing marker: {marker}")
    for marker in shame_markers:
        if marker not in shame:
            errors.append(f"Hall of Shame missing marker: {marker}")

    if 'url("./hall-of-heroes.avif")' not in hero_css:
        errors.append("Hall of Heroes CSS missing approved artwork reference")
    if 'url("./hall-of-shame.avif")' not in shame_css:
        errors.append("Hall of Shame CSS missing approved artwork reference")

    for rel in (
        '"app/hall-of-heroes.avif"',
        '"app/hall-of-shame.avif"',
        '"app/potatoes-hall.css"',
        '"app/dogs-hall.css"',
    ):
        if rel not in build:
            errors.append(f"build fingerprint chain missing {rel}")

    # Delivery AVIFs are aggressively compressed; validate structure and dimensions,
    # not an arbitrary byte count that punishes efficient encoding.
    for path in (HERO_ART, SHAME_ART):
        if not path.exists():
            continue
        size = path.stat().st_size
        dims = avif_dimensions(path)
        if size < 8_000:
            errors.append(f"Hall artwork suspiciously small: {path.relative_to(ROOT)} ({size} bytes)")
        if dims is None:
            errors.append(f"Hall artwork is not a valid AVIF with readable dimensions: {path.relative_to(ROOT)}")
        elif path == SHAME_ART and (dims[0] < 1920 or dims[1] < 1080):
            errors.append(
                f"Hall of Shame artwork below desktop delivery standard: "
                f"{dims[0]}x{dims[1]}; require at least 1920x1080"
            )
        elif path == HERO_ART and (dims[0] < 1000 or dims[1] < 560):
            errors.append(
                f"Hall of Heroes artwork below current delivery floor: "
                f"{dims[0]}x{dims[1]}; require at least 1000x560 until the HQ replacement lands"
            )

    if errors:
        print("HALL ROOMS VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("HALL ROOMS VALIDATION PASSED: paired Hall content, scene art and fingerprint chain are intact.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
