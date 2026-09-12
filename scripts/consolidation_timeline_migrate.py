#!/usr/bin/env python3
"""One-shot migration for recovered content that still uses the retired Chronology name."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".html", ".htm", ".md", ".json", ".txt", ".py", ".js", ".mjs", ".css",
    ".yml", ".yaml", ".xml", ".csv", ".ts", ".tsx", ".jsx", ".toml",
}
SKIP_DIRS = {".git", ".github", "node_modules", "vendor", "_site", "__pycache__", "archive"}
SELF = Path(__file__).resolve()
VALIDATOR = ROOT / "scripts" / "validate_timeline_naming.py"
LEGACY_REDIRECT = ROOT / "chronology" / "index.html"

REPLACEMENTS = (
    ("knowledge/chronology/", "knowledge/timeline/"),
    ("../chronology/", "../timeline/"),
    ("/chronology/", "/timeline/"),
    ("Chronology", "Timeline"),
    ("CHRONOLOGY", "TIMELINE"),
)

changed = []
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        continue
    if path.resolve() in {SELF, VALIDATOR.resolve(), LEGACY_REDIRECT.resolve()}:
        continue
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "CNAME":
        continue
    try:
        old = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    new = old
    for before, after in REPLACEMENTS:
        new = new.replace(before, after)
    if new != old:
        path.write_text(new, encoding="utf-8")
        changed.append(str(rel))

print(f"Migrated {len(changed)} active files to Timeline naming")
for rel in changed:
    print(rel)
