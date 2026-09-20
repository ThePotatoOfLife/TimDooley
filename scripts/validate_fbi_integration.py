#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for p in [R/"knowledge/cia/manifest.json",R/"rooms/potatoverse-canon/beings/cia/index.html",R/"rooms/potatoverse-canon/beings/fbi/index.html"]:
    assert p.exists(), p
print("PASS: legacy FBI character-bureau entry points defer to canonical CIA archive")
