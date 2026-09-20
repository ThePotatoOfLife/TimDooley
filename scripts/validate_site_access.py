#!/usr/bin/env python3
"""Validate the universal fast-access layer in source assets and the built site."""
from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"_site"
errors=[]

def read(path:Path)->str:
    if not path.exists():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8",errors="replace")

js=read(ROOT/"app/site-access.js")
css=read(ROOT/"app/site-access.css")
patch=read(ROOT/"scripts/patch_public_navigation.py")

for token in (
    "Current World","World Map","CIA / Intelligence","People & Cases",
    "data/house/public-surfaces.json","data/house/room-inhabitants.json",
    "site-access-dock","site-access-panel",
):
    if token not in js and token not in css:
        errors.append(f"quick-access assets missing required marker: {token}")

for token in ("inject_site_access","patch_site_access","app/site-access.css","app/site-access.js"):
    if token not in patch:
        errors.append(f"public navigation projection missing marker: {token}")

if "changed.update(patch_project_compass(OUT))" in patch:
    errors.append("legacy Project Compass must not be injected alongside the quick-access dock")

if OUT.exists():
    required=[
        "index.html","tim-dooley/index.html","world/index.html","news/index.html",
        "house/index.html","rooms/index.html","science/index.html","religion/index.html",
        "shadow-farm/index.html","world-map/index.html"
    ]
    for rel in required:
        text=read(OUT/rel)
        for asset in ("site-access.css","site-access.js"):
            if asset not in text:
                errors.append(f"{rel} missing generated {asset}")
    world=read(OUT/"world/index.html")
    if 'href="../news/">Current World</a>' not in world:
        errors.append("World must expose Current World in first-screen local navigation")
    home=read(OUT/"index.html")
    nav_start=home.find('<nav class="page-nav home-nav"')
    nav_end=home.find("</nav>",nav_start)
    if nav_start>=0 and nav_end>=0:
        first_nav=home[nav_start:nav_end]
        if first_nav.count("<a ")>5:
            errors.append("Home first-screen navigation exceeds compact local-link budget")
    if "/shadow-farm/#intelligence-desk" not in js:
        errors.append("CIA / Intelligence direct route missing from quick access")

if errors:
    print("SITE ACCESS VALIDATION FAILED")
    for e in errors: print("-",e)
    raise SystemExit(1)

print("SITE ACCESS VALIDATION PASSED: fixed dock, direct News/Map/CIA access, compact local nav and generated coverage are aligned.")
