#!/usr/bin/env python3
"""One-time migration: route every page to app/style.css and remove legacy CSS files."""
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "app" / "style.css"

link_re = re.compile(r'<link\b(?=[^>]*\brel=["\']stylesheet["\'])[^>]*>', re.I)

changed = []
for path in sorted(ROOT.rglob("*.html")):
    if ".git" in path.parts or "_site" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    matches = list(link_re.finditer(text))
    if not matches:
        continue
    rel = os.path.relpath(CANONICAL, path.parent).replace(os.sep, "/")
    canonical_link = f'<link rel="stylesheet" href="{rel}">'
    first = matches[0]
    # Remove all stylesheet links, then insert the one canonical link where the first one was.
    prefix = text[: first.start()]
    suffix = text[first.start():]
    suffix = link_re.sub("", suffix)
    new = prefix + canonical_link + suffix
    if path == ROOT / "science" / "index.html":
        new = new.replace("<body>", '<body class="science-body">', 1)
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

# Generated Science record page must use the same stylesheet and Science body scope.
builder = ROOT / "scripts" / "build_science_catalog.py"
if builder.exists():
    text = builder.read_text(encoding="utf-8")
    new = text.replace(
        "'<link rel=\"stylesheet\" href=\"../../app/style.css\"><link rel=\"stylesheet\" href=\"../science.css?v=20260910d\">'",
        "'<link rel=\"stylesheet\" href=\"../../app/style.css\">'",
    )
    new = new.replace("'</head><body><main class=\"science-page\">'", "'</head><body class=\"science-body\"><main class=\"science-page\">'")
    if new != text:
        builder.write_text(new, encoding="utf-8")
        changed.append(str(builder.relative_to(ROOT)))

# Remove every CSS source except the canonical stylesheet.
removed = []
for path in sorted(ROOT.rglob("*.css")):
    if ".git" in path.parts or "_site" in path.parts or path == CANONICAL:
        continue
    removed.append(str(path.relative_to(ROOT)))
    path.unlink()

print("changed:")
for item in changed:
    print("  ", item)
print("removed CSS:")
for item in removed:
    print("  ", item)
