#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def require(path: Path, label: str) -> Path:
    if not path.exists():
        errors.append(f"missing {label}: {path.relative_to(ROOT)}")
    return path


literature = require(ROOT / "literature" / "index.html", "Literature library")
reader = require(ROOT / "literature" / "great-book" / "index.html", "Great Book reader")
manifest_path = require(ROOT / "literature" / "great-book" / "book-manifest.json", "Great Book manifest")
download = require(
    ROOT / "literature" / "great-book" / "The-Great-Book-of-Potato-v1.2.0.0-reader-build.zip",
    "Great Book download",
)
script = require(ROOT / "app" / "great-book-reader.js", "Great Book reader script")
home = require(ROOT / "index.html", "home page")
explore = require(ROOT / "explore" / "index.html", "archive page")

manifest = None
if manifest_path.exists():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid manifest JSON: {exc}")

if reader.exists() and "v1.2.0.0" not in reader.read_text(encoding="utf-8"):
    errors.append("reader does not declare v1.2.0.0")

if manifest:
    chapters = manifest.get("chapters", [])
    parts = manifest.get("parts", [])
    if manifest.get("version") != "1.2.0.0":
        errors.append("manifest version must be 1.2.0.0")
    if len(chapters) != 171:
        errors.append(f"manifest must contain 171 chapter records, found {len(chapters)}")
    if len(parts) != 10:
        errors.append(f"manifest must declare 10 parts, found {len(parts)}")

    anchors = [chapter.get("anchor") for chapter in chapters]
    if any(not anchor for anchor in anchors):
        errors.append("every chapter record must have an anchor")
    if len(set(anchors)) != len(anchors):
        errors.append("chapter anchors must be unique")

    all_parts = []
    for part in parts:
        rel = part.get("path")
        if not rel:
            errors.append("manifest part entry is missing path")
            continue
        part_path = require(manifest_path.parent / rel, f"book part {rel}")
        if part_path.exists():
            all_parts.append(part_path.read_text(encoding="utf-8"))
    merged = "\n".join(all_parts)
    for anchor in anchors:
        if not anchor:
            continue
        count = len(re.findall(rf'\bid=["\']{re.escape(anchor)}["\']', merged))
        if count != 1:
            errors.append(f"chapter anchor {anchor} must appear exactly once across parts, found {count}")

    redirects = manifest.get("legacy_redirects", [])
    chapter20 = [item for item in redirects if str(item.get("number")) == "20"]
    if len(chapter20) != 1 or chapter20[0].get("target") != "chapter-65-5":
        errors.append("legacy Chapter 20 redirect must resolve to chapter-65-5")

if literature.exists():
    text = literature.read_text(encoding="utf-8")
    if "great-book/" not in text or "The-Great-Book-of-Potato-v1.2.0.0-reader-build.zip" not in text:
        errors.append("Literature library must expose Great Book Read and Download actions")

if reader.exists():
    text = reader.read_text(encoding="utf-8")
    for needle in ("book-index", "book-content", "The-Great-Book-of-Potato-v1.2.0.0-reader-build.zip"):
        if needle not in text:
            errors.append(f"reader shell missing required marker: {needle}")

for page, label in ((home, "home"), (explore, "archive")):
    if page.exists() and "literature/" not in page.read_text(encoding="utf-8"):
        errors.append(f"{label} page must expose Literature")

if script.exists():
    js = script.read_text(encoding="utf-8")
    forbidden = [
        r"\.focus\s*\(",
        r"style\.zoom",
        r"document\.body\.style\.zoom",
        r"document\.documentElement\.style\.zoom",
    ]
    for pattern in forbidden:
        if re.search(pattern, js):
            errors.append(f"reader script contains forbidden focus/zoom behavior matching {pattern}")

if errors:
    print("Literature reader validation FAILED:")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print("Literature reader validation passed: 171 chapters, 10 parts, stable anchors, navigation and download present.")
