#!/usr/bin/env python3
"""One-time repository migration from Chronology naming to Timeline naming.

The only intentional legacy path after this migration is /chronology/, which is
recreated as a noindex compatibility redirect to /timeline/. Workflow files are
handled separately through the GitHub API because Actions tokens cannot rewrite
workflow files.
"""
from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".html", ".htm", ".md", ".json", ".txt", ".py", ".js", ".mjs", ".css",
    ".yml", ".yaml", ".xml", ".csv", ".ts", ".tsx", ".jsx", ".toml",
}
SKIP_DIRS = {".git", ".github", "node_modules", "vendor", "_site", "__pycache__"}
SELF = Path(__file__).resolve()
VALIDATOR = (ROOT / "scripts" / "validate_timeline_naming.py").resolve()

REPLACEMENTS = (
    ("CHRONOLOGY", "TIMELINE"),
    ("Chronology", "Timeline"),
    ("chronology", "timeline"),
)

REDIRECT_HTML = """<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Timeline moved</title>
<meta name=\"robots\" content=\"noindex,follow\">
<link rel=\"canonical\" href=\"../timeline/\">
<meta http-equiv=\"refresh\" content=\"0; url=../timeline/\">
<script>location.replace('../timeline/' + location.search + location.hash);</script>
</head>
<body><p><a href=\"../timeline/\">Open Timeline</a></p></body>
</html>
"""


def renamed_name(name: str) -> str:
    out = name
    for old, new in REPLACEMENTS:
        out = out.replace(old, new)
    return out


def move_public_owner() -> None:
    legacy = ROOT / "chronology"
    canonical = ROOT / "timeline"
    if legacy.exists() and not canonical.exists():
        legacy.rename(canonical)
    elif legacy.exists() and canonical.exists():
        legacy_index = legacy / "index.html"
        if not legacy_index.exists() or "../timeline/" not in legacy_index.read_text(encoding="utf-8", errors="ignore"):
            raise RuntimeError("Both chronology/ and timeline/ exist as content owners; refusing ambiguous migration")


def rename_paths() -> None:
    paths = []
    for path in ROOT.rglob("*"):
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.parts and rel.parts[0] == "chronology":
            continue
        if path.resolve() in {SELF, VALIDATOR}:
            continue
        new_name = renamed_name(path.name)
        if new_name != path.name:
            paths.append(path)
    for path in sorted(paths, key=lambda p: len(p.parts), reverse=True):
        if not path.exists():
            continue
        target = path.with_name(renamed_name(path.name))
        if target.exists() and target != path:
            raise RuntimeError(f"Refusing to overwrite existing path: {target}")
        path.rename(target)


def rewrite_text() -> int:
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.parts and rel.parts[0] == "chronology":
            continue
        if path.resolve() in {SELF, VALIDATOR}:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"CNAME"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = text
        for old, replacement in REPLACEMENTS:
            new = new.replace(old, replacement)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    return changed


def canonicalize_timeline_page() -> None:
    page = ROOT / "timeline" / "index.html"
    if not page.exists():
        raise RuntimeError("timeline/index.html missing after migration")
    text = page.read_text(encoding="utf-8")
    text = text.replace("https://thepotatooflife.github.io/TimDooley/chronology/", "https://thepotatooflife.github.io/TimDooley/timeline/")
    text = text.replace("../chronology/", "../timeline/")
    text = text.replace("../../chronology/", "../../timeline/")
    page.write_text(text, encoding="utf-8")


def create_legacy_redirect() -> None:
    legacy = ROOT / "chronology"
    if legacy.exists():
        shutil.rmtree(legacy)
    legacy.mkdir(parents=True)
    (legacy / "index.html").write_text(REDIRECT_HTML, encoding="utf-8")


def main() -> None:
    move_public_owner()
    rename_paths()
    changed = rewrite_text()
    canonicalize_timeline_page()
    create_legacy_redirect()
    print(f"Timeline naming migration complete; rewrote {changed} text files")


if __name__ == "__main__":
    main()
