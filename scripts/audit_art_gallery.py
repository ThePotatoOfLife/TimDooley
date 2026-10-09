#!/usr/bin/env python3
"""Audit the built Art Museum, including binary integrity of every hung image."""
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
    ('data-museum-index',"chronological museum rail"),
    ('data-wall-label',"museum wall label"),
]:
    if marker not in html: fatal.append(f"gallery missing {label}")
for marker,label in [
    ("MUSEUM STAGE V3","museum stage stylesheet"),
    (".gallery-card.is-active","active painting state"),
    ("width:auto!important;height:auto!important","native artwork proportions"),
    ("MUSEUM STAGE V5","orientation-aware museum navigation"),
    ("MUSEUM STAGE V6","broken-image containment"),
]:
    if marker not in css: fatal.append(f"gallery CSS missing {label}")
for marker,label in [
    ("Controlled wall rotation. No wheel handler","controlled wall runtime"),
    ("const renderWall","painting-stage renderer"),
    ("data-wall-prev","previous-work runtime"),
    ("const classifyImage","orientation classifier"),
    ("const rebuildMonthRail","chronological month rail"),
    ("const guardImage","runtime broken-image guard"),
]:
    if marker not in js: fatal.append(f"gallery JS missing {label}")
if "addEventListener('wheel'" in js or 'addEventListener("wheel"' in js:
    fatal.append("gallery JS must not hijack page wheel scrolling")
if 'data-github-blob=' in html or "api.github.com/repos/ThePotatoOfLife/TimDooley/git/blobs" in js:
    fatal.append("gallery must not depend on runtime GitHub blob hydration")

# Guard integration drift: gallery CSS/JS must be versioned together and
# navigation must not eagerly fetch paintings that are no longer active.
for asset,label in [("art-gallery.css","stylesheet"),("art-gallery.js","runtime")]:
    matches=re.findall(r'(?:href|src)="[^"]*/'+re.escape(asset)+r'\?v=([^"]+)"',html)
    if len(matches)!=1 or not matches[0].strip():
        fatal.append(f"gallery {label} needs exactly one versioned reference")
if "img.loading = i === index ? 'eager' : 'lazy'" not in js:
    fatal.append("gallery image scheduling must restore lazy loading for off-stage works")
if "img.fetchPriority = i === index ? 'high' : 'auto'" not in js:
    fatal.append("gallery image scheduling must prioritize only the active painting")
if 'id="art-zombie-puppet-popemobile"' not in html:
    fatal.append("Zombie Puppet Popemobile deep link is missing")

# Interaction contracts: keyboard access and controlled viewer state.
for marker,label in [
    ("event.key === 'Home' || event.key === 'End'","Home/End gallery navigation"),
    ("event.altKey || event.ctrlKey || event.metaKey || event.shiftKey","browser shortcut guard"),
    ("originalLink.removeAttribute('href')","broken viewer download disabled"),
    ("stage.addEventListener('pointercancel'","cancelled swipes cleared"),
    ("pointerStart.id !== event.pointerId","gesture pointer identity"),
]:
    if marker not in js:
        fatal.append(f"gallery runtime missing {label}")
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
mcount=re.search(r'<span><b[^>]*>([0-9]+)</b> works currently hung</span>',html)
if not mcount or int(mcount.group(1))!=len(figures):
    fatal.append(f"displayed hung-work count does not match cards ({mcount.group(1) if mcount else 'missing'} vs {len(figures)})")
if 'data-gallery-hung-count' in html and 'data-gallery-hung-count' not in js:
    fatal.append("dynamic gallery count marker lacks matching JavaScript renderer")

def webp_info(path:Path):
    data=path.read_bytes()
    out={"bytes":len(data),"valid":False,"width":None,"height":None}
    if len(data)<20 or data[:4]!=b"RIFF" or data[8:12]!=b"WEBP":
        out["error"]="not a RIFF WEBP"; return out
    declared=struct.unpack_from("<I",data,4)[0]+8
    out["declared_bytes"]=declared
    if declared!=len(data):
        out["error"]=f"truncated/mismatched RIFF: declares {declared}, has {len(data)}"; return out
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

def avif_info(path:Path):
    data=path.read_bytes()
    out={"bytes":len(data),"valid":False}
    if len(data)<16:
        out["error"]="AVIF too small"; return out
    pos=0
    boxes=[]
    try:
        while pos<len(data):
            if pos+8>len(data): raise ValueError("truncated ISO-BMFF box header")
            size=struct.unpack_from(">I",data,pos)[0]
            typ=data[pos+4:pos+8]
            header=8
            if size==1:
                if pos+16>len(data): raise ValueError("truncated extended box header")
                size=struct.unpack_from(">Q",data,pos+8)[0]; header=16
            elif size==0:
                size=len(data)-pos
            if size<header: raise ValueError(f"invalid {typ!r} box size {size}")
            if pos+size>len(data): raise ValueError(f"truncated {typ!r} box: ends {pos+size}, file has {len(data)}")
            boxes.append(typ.decode("ascii","replace"))
            pos+=size
        if pos!=len(data): raise ValueError("ISO-BMFF parse did not end at EOF")
        if not boxes or boxes[0]!="ftyp": raise ValueError("AVIF missing leading ftyp box")
        ftyp=data[8:min(len(data),64)]
        if b"avif" not in ftyp and b"avis" not in ftyp: raise ValueError("ftyp does not advertise AVIF")
    except Exception as exc:
        out["error"]=str(exc); return out
    out["boxes"]=boxes
    out["valid"]=True
    return out

image_srcs=[]
for fig in figures:
    match=re.search(r'<img\b[^>]*\bsrc="([^"]+)"',fig,re.I)
    if not match:
        fatal.append("gallery card has no local image src")
        continue
    image_srcs.append(match.group(1))

# No corrupt visual-art binary may remain hidden in the public asset tree.
visual_asset_root=ROOT/"assets/visual-art"
referenced_paths=set()
for src in image_srcs:
    if src.startswith(("http:","https:","data:")):
        fatal.append(f"gallery image is not local: {src}"); continue
    clean=src.split("?",1)[0].split("#",1)[0]
    target=(PAGE.parent/clean).resolve()
    try: rel=target.relative_to(ROOT.resolve())
    except ValueError:
        fatal.append(f"image escapes site root: {src}"); continue
    if not target.is_file():
        fatal.append(f"missing gallery image: {src}"); continue
    row={"src":src,"path":str(rel),"bytes":target.stat().st_size}
    suffix=target.suffix.lower()
    if suffix==".webp":
        row.update(webp_info(target))
    elif suffix==".avif":
        row.update(avif_info(target))
    elif suffix==".png":
        data=target.read_bytes()
        signature=bytes.fromhex("89504e470d0a1a0a")
        valid=(len(data)>=45 and data[:8]==signature and data[12:16]==b"IHDR"
               and data[-12:-8]==bytes(4) and data[-8:-4]==b"IEND")
        row["valid"]=valid
        if valid:
            row["width"],row["height"]=struct.unpack_from(">II",data,16)
            if row["width"]<1000 or row["height"]<700:
                warnings.append(f"low-resolution PNG master: {rel}: {row['width']}x{row['height']}")
        else:
            row["error"]="PNG signature, IHDR or IEND invalid"
    else:
        row["valid"]=target.stat().st_size>0
    if row.get("valid") and row["bytes"]<20000:
        warnings.append(f"tiny gallery asset needs original-quality replacement: {rel}: {row['bytes']} bytes")
    if not row.get("valid"):
        fatal.append(f"corrupt/truncated gallery image: {rel}: {row.get('error','invalid payload')}")
    elif suffix==".webp" and row.get("width") and row.get("height") and max(row["width"],row["height"])<1024:
        warnings.append(f"low-resolution gallery asset: {rel}: {row['width']}x{row['height']}")
    assets.append(row)
    referenced_paths.add(str(rel))

asset_tree_corrupt=[]
if visual_asset_root.is_dir():
    for target in sorted(visual_asset_root.rglob("*")):
        if not target.is_file() or target.suffix.lower() not in {".webp",".avif"}:
            continue
        rel=target.relative_to(ROOT)
        if str(rel) in referenced_paths:
            continue
        result=webp_info(target) if target.suffix.lower()==".webp" else avif_info(target)
        if not result.get("valid"):
            msg=f"corrupt/truncated unreferenced visual-art asset: {rel}: {result.get('error','invalid payload')}"
            asset_tree_corrupt.append(msg)
            fatal.append(msg)

payload={
    "schema_version":"2.1.0",
    "gallery_cards":len(figures),
    "static_dates":dates,
    "dynamic_blob_images":0,
    "assets":assets,
    "unreferenced_corrupt_assets":asset_tree_corrupt,
    "fatal":fatal,
    "warnings":warnings,
}
REPORT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"gallery_cards":len(figures),"fatal":len(fatal),"warnings":len(warnings)},indent=2))
for item in warnings: print("WARNING:",item)
if fatal:
    for item in fatal: print("ERROR:",item)
    raise SystemExit(1)
