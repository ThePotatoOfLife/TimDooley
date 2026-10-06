#!/usr/bin/env python3
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cia=R/"knowledge/cia/manifest.json"; fbi=R/"knowledge/fbi/manifest.json"; route=R/"rooms/potatoverse-canon/beings/fbi/index.html"
for p in (cia,fbi,route):
    assert p.exists(), p
legacy=json.loads(fbi.read_text(encoding="utf-8"))
assert legacy.get("status")=="retired-predecessor"
assert (legacy.get("successor") or {}).get("path")=="knowledge/cia/manifest.json"
html=route.read_text(encoding="utf-8",errors="replace")
assert "Retired predecessor" in html
assert "location.replace" not in html
assert "../cia/" in html
print("PASS: FBI is a visible retired predecessor beneath canonical CIA; no competing live bureau")
