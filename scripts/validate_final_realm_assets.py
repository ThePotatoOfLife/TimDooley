#!/usr/bin/env python3
"""Validate the final three-realm pixel-art system used by production pages."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FINAL_REALMS = {
    "heaven": ROOT / "app/home-heaven.avif",
    "plane": ROOT / "app/home-plane.avif",
    "below": ROOT / "app/home-below.avif",
}

HALL_ART = {
    "heroes": ROOT / "app/hall-of-heroes.avif",
    "shame": ROOT / "app/hall-of-shame.avif",
}

HALL_SURFACES = {
    "heroes": (
        ROOT / "rooms/potatoverse-canon/beings/potatoes/index.html",
        ROOT / "app/potatoes-hall.css",
    ),
    "shame": (
        ROOT / "below/dogs/index.html",
        ROOT / "app/dogs-hall.css",
    ),
}

LIVE_FILES = [
    ROOT / "app/site-elevator.css",
    ROOT / "index.html",
    ROOT / "app/house-journey.css",
    ROOT / "app/site-elevator.js",
    ROOT / "scripts/build_site.py",
]

RETIRED_SCENES = (
    "site-tree-perspective.svg",
    "site-plane-organic-field.svg",
    "site-below-root-field.svg",
    "home-world-master.webp",
)


def main() -> int:
    errors: list[str] = []

    for floor, path in FINAL_REALMS.items():
        if not path.is_file():
            errors.append(f"{floor}: missing final realm asset {path.relative_to(ROOT)}")
            continue
        size = path.stat().st_size
        if size < 20_000:
            errors.append(f"{floor}: realm asset looks unexpectedly small ({size} bytes)")
        if size > 500_000:
            errors.append(f"{floor}: realm asset exceeds lightweight background budget ({size} bytes)")

    for hall, path in HALL_ART.items():
        if not path.is_file():
            errors.append(f"{hall}: missing Hall artwork {path.relative_to(ROOT)}")
            continue
        size = path.stat().st_size
        if size < 20_000:
            errors.append(f"{hall}: Hall artwork looks unexpectedly small ({size} bytes)")
        if size > 250_000:
            errors.append(f"{hall}: Hall artwork exceeds page-background budget ({size} bytes)")

    texts: dict[Path, str] = {}
    for path in LIVE_FILES:
        if not path.is_file():
            errors.append(f"missing production contract file: {path.relative_to(ROOT)}")
            continue
        texts[path] = path.read_text(encoding="utf-8", errors="replace")

    elevator = texts.get(ROOT / "app/site-elevator.css", "")
    home = texts.get(ROOT / "index.html", "")
    journey = texts.get(ROOT / "app/house-journey.css", "")
    build = texts.get(ROOT / "scripts/build_site.py", "")

    for floor in ("heaven", "plane", "below"):
        asset = f"home-{floor}.avif"
        if asset not in elevator:
            errors.append(f"shared floor renderer missing {asset}")
        if asset not in home:
            errors.append(f"homepage realm stage missing {asset}")
        if asset not in journey:
            errors.append(f"Room preview system missing {asset}")
        if asset not in build:
            errors.append(f"build fingerprint graph missing {asset}")

    for hall, asset_path in HALL_ART.items():
        asset = asset_path.name
        html_path, css_path = HALL_SURFACES[hall]
        if not html_path.is_file():
            errors.append(f"{hall}: missing Hall source page {html_path.relative_to(ROOT)}")
            continue
        if not css_path.is_file():
            errors.append(f"{hall}: missing Hall stylesheet {css_path.relative_to(ROOT)}")
            continue
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
        css_text = css_path.read_text(encoding="utf-8", errors="replace")
        if asset not in html_text:
            errors.append(f"{hall}: Hall source page does not mount {asset}")
        if asset not in css_text:
            errors.append(f"{hall}: Hall stylesheet does not use {asset}")
        if "hall-scene" not in html_text:
            errors.append(f"{hall}: Hall source page missing visible arrival scene")
        if asset not in build:
            errors.append(f"{hall}: build fingerprint graph missing {asset}")

    for retired in RETIRED_SCENES:
        for path, text in texts.items():
            if retired in text:
                errors.append(
                    f"{path.relative_to(ROOT)} still references retired realm art {retired}"
                )

    for floor in ("heaven", "plane", "below"):
        marker = f'html[data-site-floor="{floor}"]{{'
        if elevator.count(marker) != 1:
            errors.append(
                f"site-elevator.css must define {floor} exactly once; found {elevator.count(marker)}"
            )

    if "body:not(.home-body)::before" not in elevator:
        errors.append("shared floor renderer missing canonical non-Home realm canvas")
    if "--site-realm-art" not in elevator:
        errors.append("shared floor renderer missing realm-art variable contract")

    if errors:
        print(f"FINAL REALM ASSET VALIDATION FAILED: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print("FINAL REALM ASSET VALIDATION PASSED")
    for floor, path in FINAL_REALMS.items():
        print(f"- {floor}: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
    for hall, path in HALL_ART.items():
        print(f"- {hall}: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
