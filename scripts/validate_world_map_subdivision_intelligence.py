#!/usr/bin/env python3
"""Validate selectable subdivision intelligence: facts, evidence and contained places."""
from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUB=ROOT/"world-map/3d-subdivisions.js"
PLACES=ROOT/"world-map/3d-places.js"
GEO=ROOT/"world-map/3d-geo-kernel.js"
SPATIAL_UI=ROOT/"world-map/3d-spatial-overlay-ui.js"
BELOW_SPATIAL=ROOT/"data/world-map-spatial/below-us-cases.geojson"
INDEX=ROOT/"data/world-places/index.json"
DNK_PLACES=ROOT/"data/world-places/countries/DNK.geo.json"
DNK_REGIONS=ROOT/"data/world-subdivisions/DNK.geo.json"

def norm(lng: float)->float:
    return ((lng+180)%360+360)%360-180

def unwrap(lng: float, ref: float)->float:
    delta=norm(norm(lng)-norm(ref))
    return ref+delta

def point_in_ring(point, ring):
    lng,lat=norm(float(point[0])),float(point[1])
    pts=[(unwrap(float(p[0]),lng),float(p[1])) for p in ring if isinstance(p,list) and len(p)>=2]
    inside=False
    for i in range(len(pts)):
        j=(i-1)%len(pts)
        xi,yi=pts[i]; xj,yj=pts[j]
        hit=((yi>lat)!=(yj>lat)) and (lng < (xj-xi)*(lat-yi)/((yj-yi) or 1e-15)+xi)
        if hit: inside=not inside
    return inside

def in_polygon(point, coords):
    if not coords or not point_in_ring(point,coords[0]): return False
    return not any(point_in_ring(point,hole) for hole in coords[1:])

def contains(point, geom):
    if geom.get("type")=="Polygon": return in_polygon(point,geom.get("coordinates") or [])
    if geom.get("type")=="MultiPolygon": return any(in_polygon(point,p) for p in geom.get("coordinates") or [])
    return False

def main()->int:
    errors=[]
    for p in (SUB,PLACES,GEO,SPATIAL_UI,BELOW_SPATIAL,INDEX,DNK_PLACES,DNK_REGIONS):
        if not p.is_file(): errors.append(f"missing {p.relative_to(ROOT)}")
    if errors:
        print("WORLD MAP SUBDIVISION INTELLIGENCE FAILED")
        for e in errors: print("-",e)
        return 1

    sub=SUB.read_text(encoding="utf-8",errors="replace")
    places=PLACES.read_text(encoding="utf-8",errors="replace")
    geo=GEO.read_text(encoding="utf-8",errors="replace")
    spatial_ui=SPATIAL_UI.read_text(encoding="utf-8",errors="replace")
    below_spatial=json.loads(BELOW_SPATIAL.read_text(encoding="utf-8"))
    for token in (
        "populationDensity(", "data-subdivision-places", "hydrateSubdivisionPlaces(",
        "Cities and towns", "subdivisionEvidenceHtml(", "Population source:",
    ):
        if token not in sub: errors.append(f"subdivision inspector missing {token!r}")
    for token in ("async function inSubdivision(", "geo.pointInGeometry(", "loadCountry(code)", "inSubdivision,"):
        if token not in places: errors.append(f"Places subdivision query missing {token!r}")
    if "pointInGeometry" not in geo:
        errors.append("Geo kernel missing pointInGeometry")
    for token in ("BELOW_OVERLAY_ID", "belowRowsForSubdivision(", "registerBelowSubdivisionProvider(", "registerEvidenceProvider('spatial:project.below.us-cases'", "project case anchor"):
        if token not in spatial_ui: errors.append(f"canonical Below subdivision projection missing {token!r}")
    below_ids={str((feature.get("properties") or {}).get("subdivision_id") or "") for feature in below_spatial.get("features",[])}
    if not {"US-VA","US-OH"} <= below_ids:
        errors.append("canonical Below spatial anchors must retain US-VA / US-OH subdivision projection ids")

    index=json.loads(INDEX.read_text(encoding="utf-8"))
    for iso3 in ("USA","DNK","CAN"):
        if iso3 not in (index.get("countries") or {}): errors.append(f"Places seed missing {iso3} partition")
    if "GeoNames" not in str(index.get("source") or ""):
        errors.append("Places seed must retain GeoNames provenance")
    limitation=str((index.get("provenance") or {}).get("limitation") or "").lower()
    if "exact upstream refresh date is not known" not in limitation:
        errors.append("seed Places index must expose unknown exact refresh limitation")

    regions=json.loads(DNK_REGIONS.read_text(encoding="utf-8"))
    cities=json.loads(DNK_PLACES.read_text(encoding="utf-8"))
    syddanmark=next((f for f in regions.get("features",[]) if f.get("id")=="DK-1083"),None)
    if not syddanmark:
        errors.append("Region Syddanmark fixture missing")
    else:
        inside=[
            f for f in cities.get("features",[])
            if isinstance((f.get("geometry") or {}).get("coordinates"),list)
            and contains((f.get("geometry") or {}).get("coordinates"), syddanmark.get("geometry") or {})
        ]
        names={str((f.get("properties") or {}).get("name") or "") for f in inside}
        if "Haderslev" not in names:
            errors.append("Region Syddanmark containment must include Haderslev")
        if len(inside)<5:
            errors.append(f"Region Syddanmark should expose several mapped places; got {len(inside)}")

    node=shutil.which("node")
    if node:
        for p in (SUB,PLACES,GEO,SPATIAL_UI):
            result=subprocess.run([node,"--check",str(p)],cwd=ROOT,text=True,capture_output=True,check=False)
            if result.returncode:
                errors.append(f"JavaScript syntax failed for {p.relative_to(ROOT)}: "+(result.stderr.strip() or result.stdout.strip()))
    else:
        errors.append("node executable unavailable; cannot syntax-check subdivision intelligence runtime")

    if errors:
        print("WORLD MAP SUBDIVISION INTELLIGENCE FAILED")
        for e in errors: print("-",e)
        return 1
    print("WORLD MAP SUBDIVISION INTELLIGENCE PASSED · facts + evidence + contained cities · Syddanmark/Haderslev regression")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
