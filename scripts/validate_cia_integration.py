#!/usr/bin/env python3
"""Validate canonical CIA — Characters, Incidents & Associations integration."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"knowledge/cia/manifest.json"; CABINET=ROOT/"rooms/potatoverse-canon/beings/cia/index.html"
VIEWER=ROOT/"rooms/potatoverse-canon/beings/cia/file/index.html"; COLLECTIONS=ROOT/"data/house/collections.json"
ACCOUNT=ROOT/"knowledge/cia/symbolic-account-contract.json"; SYMBOLS=ROOT/"knowledge/cia/symbolic-image-pool.json"; ACTIVITY=ROOT/"knowledge/cia/activity-index.json"; FBI_MANIFEST=ROOT/"knowledge/fbi/manifest.json"; FBI_ROUTE=ROOT/"rooms/potatoverse-canon/beings/fbi/index.html"
ROUTE="rooms/potatoverse-canon/beings/cia/"
def fail(m): print("FAIL:",m); raise SystemExit(1)
def main():
 m=json.loads(MANIFEST.read_text(encoding="utf-8")); chars=m.get("characters") or []
 if not chars: fail("manifest has no characters")
 if m.get("namespace")!="potatoverse-character-archive": fail("namespace missing")
 if "Central Intelligence Agency" not in (m.get("disclaimer") or ""): fail("CIA collision boundary missing")
 ids=[str(x.get("id") or "").strip() for x in chars]
 if any(not x for x in ids) or len(ids)!=len(set(ids)): fail("character ids missing or duplicated")
 for row in chars:
  cid=row["id"]; expected=f"knowledge/cia/characters/{cid}.json"
  if row.get("path")!=expected: fail(f"{cid} path drift")
  p=ROOT/expected
  if not p.is_file(): fail(f"missing dossier {expected}")
 cabinet=CABINET.read_text(encoding="utf-8")
 for token in ["CIA — Characters, Incidents & Associations","cia-cabinet.js","fbi/"]:
  if token not in cabinet: fail(f"cabinet missing {token!r}")
 cabinet_js=(ROOT/"app/cia-cabinet.js").read_text(encoding="utf-8",errors="replace")
 for token in ["data-character-id","data-activity","file-avatar"]:
  if token not in cabinet_js: fail(f"CIA cabinet runtime missing {token!r}")
 viewer=VIEWER.read_text(encoding="utf-8")
 for p in ["cia-dossier.js","cia-dossier.css","accountStrip","data-panel=\"account\"","data-panel=\"media\""]:
  if p not in viewer: fail(f"viewer missing {p}")
 if not ACCOUNT.is_file(): fail("CIA symbolic account contract missing")
 account=json.loads(ACCOUNT.read_text(encoding="utf-8"))
 if account.get("welfare_rule",{}).get("enabled_by_default") is not False: fail("Dooley welfare must default off")
 if "not money" not in str(account.get("boundary","")).lower(): fail("symbolic account boundary missing")
 for c in chars:
  cp=ROOT/c.get("path","")
  if not cp.is_file(): fail(f"CIA character file missing: {cp}")
  cd=json.loads(cp.read_text(encoding="utf-8"))
  meaning=cd.get("meaning") or {}
  for key in ["why_this_file_matters","known","interpretive","unknown","relationship_arc","confidence_note"]:
   if not meaning.get(key): fail(f"CIA meaning spine missing {key} for {c.get('id')}")
 if not ACTIVITY.is_file(): fail("CIA activity index missing")
 activity=json.loads(ACTIVITY.read_text(encoding="utf-8"))
 if len(activity.get("records",[]))!=len(chars): fail("CIA activity index coverage drift")
 if "moral" not in str((activity.get("rules") or {}).get("boundary","")).lower(): fail("CIA activity opacity boundary missing")
 if not SYMBOLS.is_file(): fail("CIA symbolic image pool missing")
 symbols=json.loads(SYMBOLS.read_text(encoding="utf-8"))
 if symbols.get("storage")!="remote-url-only": fail("symbolic image pool must stay remote-url-only")
 if "not a portrait" not in str(symbols.get("boundary","")).lower(): fail("symbolic image non-likeness boundary missing")
 needed={"dog","footstool","mud","potato","tomato","angel"}
 terms={str(t).lower() for img in symbols.get("images",[]) for t in img.get("role_terms",[])}
 if not needed.issubset(terms): fail("symbolic image pool missing core role symbols")
 for img in symbols.get("images",[]):
  if not str(img.get("image_url","")).startswith("https://"): fail("symbolic image must use https remote URL")
  if not img.get("source_page") or not img.get("license"): fail("symbolic image provenance incomplete")
 fbi=json.loads(FBI_MANIFEST.read_text(encoding="utf-8"))
 if fbi.get("status")!="retired-predecessor": fail("FBI manifest not retired")
 if (fbi.get("successor") or {}).get("path")!="knowledge/cia/manifest.json": fail("FBI successor drift")
 fbi_route=FBI_ROUTE.read_text(encoding="utf-8",errors="replace")
 if "Retired predecessor" not in fbi_route or "location.replace" in fbi_route: fail("FBI route must be visible retired archive, not auto-redirect")
 cols=json.loads(COLLECTIONS.read_text(encoding="utf-8")); c=next((x for x in cols.get("collections",[]) if x.get("id")=="characters-incidents-associations"),None)
 if not c or c.get("public_route")!=ROUTE: fail("House CIA collection route drift")
 actual=sum(1 for p in (ROOT/"knowledge/cia").rglob("*") if p.is_file())
 if c.get("source_file_count")!=actual: fail(f"source count {c.get('source_file_count')} != {actual}")
 if (m.get("coverage_summary") or {}).get("total_characters")!=len(chars): fail("coverage count drift")
 print(f"PASS: CIA integration · {len(chars)} canonical characters · {actual} source files · House/Story routes wired")
 return 0
if __name__=="__main__": sys.exit(main())
