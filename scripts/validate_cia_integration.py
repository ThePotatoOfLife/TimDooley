#!/usr/bin/env python3
"""Validate canonical CIA — Characters, Incidents & Associations integration."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"knowledge/cia/manifest.json"; CABINET=ROOT/"rooms/potatoverse-canon/beings/cia/index.html"
VIEWER=ROOT/"rooms/potatoverse-canon/beings/cia/file/index.html"; COLLECTIONS=ROOT/"data/house/collections.json"
ACCOUNT=ROOT/"knowledge/cia/symbolic-account-contract.json"; MUD_BANK=ROOT/"knowledge/cia/mud-bank-contract.json"; DEBT_EVIDENCE=ROOT/"knowledge/cia/debt-evidence-ledger.json"; SYMBOLS=ROOT/"knowledge/cia/symbolic-image-pool.json"; ACTIVITY=ROOT/"knowledge/cia/activity-index.json"; CURRENT=ROOT/"knowledge/cia/current-desk.json"; FBI_MANIFEST=ROOT/"knowledge/fbi/manifest.json"; FBI_ROUTE=ROOT/"rooms/potatoverse-canon/beings/fbi/index.html"
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
 if account.get("welfare_rule",{}).get("enabled_by_default") is not True: fail("Dooley welfare must default on")
 if "not money" not in str(account.get("boundary","")).lower(): fail("symbolic account boundary missing")
 if not MUD_BANK.is_file(): fail("Mud Bank contract missing")
 bank=json.loads(MUD_BANK.read_text(encoding="utf-8"))
 if bank.get("welfare",{}).get("rate_per_second_susd")!=0.00000000001: fail("Dooley Welfare rate drift")
 if bank.get("denomination",{}).get("real_currency") is not False: fail("Mud Bank denomination boundary drift")
 pricing=bank.get("debit_pricing") or {}
 categories=pricing.get("categories") or {}
 tiers=pricing.get("evidence_multipliers") or {}
 reps=pricing.get("repetition_multipliers") or []
 required_categories={"destructive-act","breach-of-trust","repeated-harmful-narrative","verified-deception","targeted-harassment-boundary","theft-fraud-cheating","coercive-social-leverage","reciprocal-conflict"}
 if not required_categories.issubset(categories): fail("Mud Bank debit categories incomplete")
 if tiers.get("primary-direct")!=1.0 or tiers.get("contemporaneous-recovered")!=0.8 or tiers.get("chronicle-retelling")!=0.45 or tiers.get("retrospective-interpretation")!=0: fail("Mud Bank evidence multipliers drift")
 if reps[:4]!=[1.0,1.2,1.4,1.5]: fail("Mud Bank repetition multipliers drift")
 if not DEBT_EVIDENCE.is_file(): fail("CIA debt evidence ledger missing")
 debt=json.loads(DEBT_EVIDENCE.read_text(encoding="utf-8"))
 events=debt.get("events") or []
 by_id={e.get("id"):e for e in events}
 for eid in ["debt-txt-2026-06-20-disputed-narrative","debt-port-monkey-2024-tree-trust","debt-marty-2024-12-21-social-leverage"]:
  if eid not in by_id: fail(f"debt evidence event missing: {eid}")
 for e in events:
  for key in ["id","character_id","date","pricing_status","source_ref","source_mode","summary"]:
   if not e.get(key): fail(f"debt evidence {e.get('id')} missing {key}")
  if e.get("pricing_status")=="priced":
   for key in ["category","evidence_tier","repetition_key","occurrence_index","project_adjustment_susd"]:
    if e.get(key) in (None,""): fail(f"priced debt evidence {e.get('id')} missing {key}")
   if e["category"] not in categories or e["evidence_tier"] not in tiers: fail(f"priced debt evidence taxonomy drift: {e.get('id')}")
   idx=max(1,int(e["occurrence_index"]))
   mult=reps[min(idx-1,len(reps)-1)]
   expected=round(float(categories[e["category"]])*float(tiers[e["evidence_tier"]])*float(mult),6)
   if abs(float(e["project_adjustment_susd"])-expected)>1e-9: fail(f"debt pricing formula drift for {e.get('id')}: {e.get('project_adjustment_susd')} != {expected}")
 bank_js=(ROOT/"app/mud-bank.js").read_text(encoding="utf-8",errors="replace")
 if "project_adjustment_susd" not in bank_js: fail("Mud Bank runtime must honor priced per-event adjustments")
 dossier_js=(ROOT/"app/cia-dossier.js").read_text(encoding="utf-8",errors="replace")
 if "evidence_tier" not in dossier_js or "debt_evidence_id" not in dossier_js: fail("CIA dossier account reader must expose debit provenance")
 for cid in ["txt","port-monkey","marty-biz"]:
  cd=json.loads((ROOT/f"knowledge/cia/characters/{cid}.json").read_text(encoding="utf-8"))
  refs={x.get("debt_evidence_id") for x in ((cd.get("symbolic_account") or {}).get("entries") or []) if x.get("type")=="project-debit"}
  if not any((e.get("character_id")==cid and e.get("id") in refs and e.get("pricing_status")=="priced") for e in events): fail(f"{cid} missing priced project-debit link")
 for c in chars:
  cp=ROOT/c.get("path","")
  if not cp.is_file(): fail(f"CIA character file missing: {cp}")
  cd=json.loads(cp.read_text(encoding="utf-8"))
  meaning=cd.get("meaning") or {}
  for key in ["why_this_file_matters","known","interpretive","unknown","relationship_arc","confidence_note"]:
   if not meaning.get(key): fail(f"CIA meaning spine missing {key} for {c.get('id')}")
 if not CURRENT.is_file(): fail("CIA current desk missing")
 current=json.loads(CURRENT.read_text(encoding="utf-8"))
 current_ids={x.get("id") for x in current.get("items",[])}
 if not {"dim","txt","matthew-mtclassic","mediomu007","tim-dooley"}.issubset(current_ids): fail("CIA current desk missing core current files")
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
