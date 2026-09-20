#!/usr/bin/env python3
"""Validate canonical CIA — Characters, Incidents & Associations integration."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"knowledge/cia/manifest.json"; CABINET=ROOT/"rooms/potatoverse-canon/beings/cia/index.html"
VIEWER=ROOT/"rooms/potatoverse-canon/beings/cia/file/index.html"; COLLECTIONS=ROOT/"data/house/collections.json"
INCIDENTS=ROOT/"knowledge/cia/incidents/index.json"; ASSOCIATIONS=ROOT/"knowledge/cia/associations/network.json"; DOSSIERS=ROOT/"data/house/room-dossiers.json"
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
 for token in ["manifest?.characters||[]","data-character-id","knowledge/cia/manifest.json","CIA — Characters, Incidents & Associations"]:
  if token not in cabinet: fail(f"cabinet missing {token!r}")
 viewer=VIEWER.read_text(encoding="utf-8")
 for p in ["knowledge/cia/manifest.json","knowledge/cia/role-index.json","knowledge/cia/story-links.json","knowledge/cia/associations/network.json","knowledge/cia/incidents/index.json","knowledge/cia/enhancements-index.json"]:
  if p not in viewer: fail(f"viewer missing {p}")
 cols=json.loads(COLLECTIONS.read_text(encoding="utf-8")); c=next((x for x in cols.get("collections",[]) if x.get("id")=="characters-incidents-associations"),None)
 if not c or c.get("public_route")!=ROUTE: fail("House CIA collection route drift")
 actual=sum(1 for p in (ROOT/"knowledge/cia").rglob("*") if p.is_file())
 if c.get("source_file_count")!=actual: fail(f"source count {c.get('source_file_count')} != {actual}")
 if (m.get("coverage_summary") or {}).get("total_characters")!=len(chars): fail("coverage count drift")
 incidents=json.loads(INCIDENTS.read_text(encoding="utf-8"))
 if incidents.get("id")!="cia-incidents-index": fail("CIA incidents retained stale FBI namespace")
 associations=json.loads(ASSOCIATIONS.read_text(encoding="utf-8"))
 if not str(associations.get("id") or "").startswith("cia-"): fail("CIA association network namespace drift")
 dossiers=json.loads(DOSSIERS.read_text(encoding="utf-8"))
 canon=next((x for x in dossiers.get("dossiers",[]) if x.get("room_id")=="canon-identities"),{})
 featured=(canon.get("knowledge_holdings") or {}).get("featured",[])
 cia_rows=[x for x in featured if str(x.get("path") or "").startswith("knowledge/cia/")]
 stale=[x.get("id") for x in cia_rows if str(x.get("id") or "").startswith("fbi-")]
 if stale: fail("House CIA holdings retain stale FBI ids: "+", ".join(stale))
 expected={"knowledge/cia/incidents/index.json":"cia-incidents","knowledge/cia/associations/network.json":"cia-associations"}
 for path,expected_id in expected.items():
  row=next((x for x in cia_rows if x.get("path")==path),None)
  if not row or row.get("id")!=expected_id: fail(f"House CIA holding id drift for {path}")
 print(f"PASS: CIA integration · {len(chars)} canonical characters · {actual} source files · House/Story routes wired")
 return 0
if __name__=="__main__": sys.exit(main())
