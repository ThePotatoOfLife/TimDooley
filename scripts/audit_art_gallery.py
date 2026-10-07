#!/usr/bin/env python3
"""Audit the built Art Museum without requiring Pillow.

Structure/reference failures are fatal. Resolution and legacy-asset quality debt
are reported so the collection can be repaired progressively without hiding it.
"""
from __future__ import annotations
import json, re, struct
from pathlib import Path

ROOT=Path("_site")
PAGE=ROOT/"rooms/inside/visual-art/index.html"
CSS=ROOT/"app/art-gallery.css"
JS=ROOT/"app/art-gallery.js"
REPORT=Path("art-gallery-audit.json")

fatal=[]
warnings=[]
assets=[]
if not PAGE.is_file(): fatal.append("missing built visual-art page")
if not CSS.is_file(): fatal.append("missing built art-gallery.css")
if not JS.is_file(): fatal.append("missing built art-gallery.js")

html=PAGE.read_text(encoding="utf-8",errors="replace") if PAGE.is_file() else ""
css=CSS.read_text(encoding="utf-8",errors="replace") if CSS.is_file() else ""
js=JS.read_text(encoding="utf-8",errors="replace") if JS.is_file() else ""

for marker,label in [
    ('class="gallery-grid museum-wall"',"museum wall"),
    ('data-date=',"static ISO dates"),
    ('class="museum-stage-shell"',"controlled museum stage"),
    ('The wall moves; the page does not fight you.',"non-hijacking museum copy"),
    ('data-wall-plaque',"active artwork plaque"),
]:
    if marker not in html: fatal.append(f"gallery missing {label}")
for marker,label in [
    ("MUSEUM STAGE V3","museum stage stylesheet"),
    (".gallery-card.is-active","active painting state"),
    ("width:auto!important;height:auto!important","native artwork proportions"),
]:
    if marker not in css: fatal.append(f"gallery CSS missing {label}")
for marker,label in [
    ("Controlled wall rotation. No wheel handler","controlled wall runtime"),
    ("const renderWall","painting-stage renderer"),
    ("data-wall-prev","previous-work runtime"),
]:
    if marker not in js: fatal.append(f"gallery JS missing {label}")
if "addEventListener('wheel'" in js or 'addEventListener("wheel"' in js:
    fatal.append("gallery JS must not hijack page wheel scrolling")

figures=re.findall(r'<figure\b[^>]*class="[^"]*gallery-card[^"]*"[^>]*>[\s\S]*?</figure>',html,re.I)
ids=[]
dates=[]
for fig in figures:
    mid=re.search(r'\bid="([^"]+)"',fig)
    mdate=re.search(r'\bdata-date="(\d{4}-\d{2}-\d{2})"',fig)
    if mid: ids.append(mid.group(1))
    if mdate: dates.append(mdate.group(1))
if len(figures)<15: fatal.append(f"too few gallery works: {len(figures)}")
if len(ids)!=len(set(ids)): fatal.append("duplicate gallery card ids")
if len(dates)!=len(figures): fatal.append(f"not every gallery card has data-date ({len(dates)}/{len(figures)})")
if dates and dates!=sorted(dates): fatal.append("gallery source order is not chronological")

def webp_info(path:Path):
    data=path.read_bytes()
    out={"bytes":len(data),"valid":False,"width":None,"height":None}
    if len(data)<20 or data[:4]!=b"RIFF" or data[8:12]!=b"WEBP":
        out["error"]="not a RIFF WEBP"
        return out
    declared=struct.unpack_from("<I",data,4)[0]+8
    out["declared_bytes"]=declared
    if declared!=len(data):
        out["error"]=f"truncated/mismatched RIFF: declares {declared}, has {len(data)}"
        return out
    chunk=data[12:16]
    try:
        if chunk==b"VP8 ":
            pos=data.find(b"\x9d\x01\x2a",20)
            if pos>=0 and pos+7<=len(data):
                out["width"]=struct.unpack_from("<H",data,pos+3)[0]&0x3fff
                out["height"]=struct.unpack_from("<H",data,pos+5)[0]&0x3fff
        elif chunk==b"VP8X" and len(data)>=30:
            out["width"]=1+int.from_bytes(data[24:27],"little")
            out["height"]=1+int.from_bytes(data[27:30],"little")
        elif chunk==b"VP8L" and len(data)>=25 and data[20]==0x2f:
            bits=int.from_bytes(data[21:25],"little")
            out["width"]=1+(bits&0x3fff)
            out["height"]=1+((bits>>14)&0x3fff)
    except Exception as exc:
        out["dimension_error"]=str(exc)
    out["valid"]=True
    return out

for src in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',html,re.I):
    if src.startswith(("http:","https:","data:")): continue
    clean=src.split("?",1)[0].split("#",1)[0]
    target=(PAGE.parent/clean).resolve()
    try: rel=target.relative_to(ROOT.resolve())
    except ValueError:
        fatal.append(f"image escapes site root: {src}")
        continue
    if not target.is_file():
        fatal.append(f"missing gallery image: {src}")
        continue
    row={"src":src,"path":str(rel),"bytes":target.stat().st_size}
    if target.suffix.lower()==".webp":
        row.update(webp_info(target))
        if not row.get("valid"):
            warnings.append(f"corrupt gallery WEBP: {rel}: {row.get('error')}")
        elif row.get("width") and row.get("height") and max(row["width"],row["height"])<1024:
            warnings.append(f"low-resolution gallery asset: {rel}: {row['width']}x{row['height']}")
    assets.append(row)

dynamic=len(re.findall(r'\bdata-github-blob="',html))
if dynamic:
    warnings.append(f"{dynamic} gallery image(s) still depend on runtime GitHub blob hydration")

payload={
    "schema_version":"1.1.0",
    "gallery_cards":len(figures),
    "static_dates":dates,
    "dynamic_blob_images":dynamic,
    "assets":assets,
    "fatal":fatal,
    "warnings":warnings,
}
REPORT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"gallery_cards":len(figures),"fatal":len(fatal),"warnings":len(warnings)},indent=2))
for item in warnings: print("WARNING:",item)
if fatal:
    for item in fatal: print("ERROR:",item)
    raise SystemExit(1)
