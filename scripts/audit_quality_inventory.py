#!/usr/bin/env python3
"""Inventory repository quality scripts and expose check ownership/drift without deleting historical validators."""
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/"scripts"
WORKFLOWS=ROOT/".github/workflows"
OUT=ROOT/"quality-inventory.json"
CHECK_RE=re.compile(r"scripts/[A-Za-z0-9_.-]+\.(?:py|mjs)")
CHECK_PREFIXES=("validate_","test_","audit_","check_")

def main()->int:
    files=sorted(p for p in SCRIPTS.iterdir() if p.is_file() and p.suffix in {".py",".mjs"})
    checks=[p for p in files if p.stem.startswith(CHECK_PREFIXES)]
    workflow_text="\n".join(p.read_text(encoding="utf-8",errors="replace") for p in sorted(WORKFLOWS.glob("*.y*ml")))
    runner=(SCRIPTS/"run_quality_group.py").read_text(encoding="utf-8",errors="replace")
    direct=set(CHECK_RE.findall(workflow_text+"\n"+runner))

    reverse={p.relative_to(ROOT).as_posix():set() for p in checks}
    all_sources=[p for p in files]+list(WORKFLOWS.glob("*.yml"))+list(WORKFLOWS.glob("*.yaml"))
    for source in all_sources:
        text=source.read_text(encoding="utf-8",errors="replace")
        source_rel=source.relative_to(ROOT).as_posix()
        for ref in CHECK_RE.findall(text):
            if ref in reverse and ref!=source_rel:
                reverse[ref].add(source_rel)

    rows=[]
    for p in checks:
        rel=p.relative_to(ROOT).as_posix()
        refs=sorted(reverse.get(rel,set()))
        if rel in direct:
            status="direct-gate"
        elif refs:
            status="nested-or-support"
        else:
            status="unowned-check"
        rows.append({"path":rel,"status":status,"referenced_by":refs})

    missing=sorted(ref for ref in set(CHECK_RE.findall(workflow_text+"\n"+runner)) if not (ROOT/ref).is_file())
    counts={key:sum(1 for row in rows if row["status"]==key) for key in ("direct-gate","nested-or-support","unowned-check")}
    payload={
        "version":"1.0.0",
        "purpose":"Inventory validation/test/audit/check scripts by quality ownership. Unowned does not mean obsolete; it means the check needs classification before deletion or promotion.",
        "script_files":len(files),
        "check_scripts":len(rows),
        "counts":counts,
        "missing_references":missing,
        "rows":rows,
    }
    OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(f"QUALITY INVENTORY: {len(rows)} checks · {counts['direct-gate']} direct · {counts['nested-or-support']} nested/support · {counts['unowned-check']} unowned")
    if counts["unowned-check"]:
        print("NOTE unowned checks require review, not automatic deletion:")
        for row in [x for x in rows if x["status"]=="unowned-check"][:40]:
            print("-",row["path"])
        if counts["unowned-check"]>40:
            print(f"- ... and {counts['unowned-check']-40} more")
    if missing:
        print("QUALITY INVENTORY FAILED: referenced checks are missing")
        for ref in missing: print("-",ref)
        return 1
    print("Quality inventory reference integrity: PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
