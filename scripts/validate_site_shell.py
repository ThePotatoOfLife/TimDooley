#!/usr/bin/env python3
"""Verify the built Pages artifact without duplicating source behavior tests.

Behavior-level Atlas contracts belong to the dedicated source validators. This
post-build gate proves that those validated source modules survived the build,
that generated runtime datasets meet their coverage contracts, and that the
public site shell, links and discovery surfaces are intact.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
REPORT = ROOT / "site-shell-report.txt"


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        try: label = path.relative_to(SITE)
        except ValueError: label = path.relative_to(ROOT)
        errors.append(f"invalid JSON: {label} — {exc}")
        return {}


def require_text(text: str, required: tuple[str, ...], owner: str, errors: list[str]) -> None:
    for marker in required:
        if marker not in text: errors.append(f"{owner} missing required shell marker: {marker}")


def require_build_parity(rel: str, errors: list[str]) -> None:
    source,built=ROOT/rel,SITE/rel
    if not source.exists() or not built.exists(): return
    if source.read_bytes()!=built.read_bytes(): errors.append(f"built runtime/contract drifted from validated source: {rel}")


def main() -> int:
    errors:list[str]=[];warnings:list[str]=[]
    if not SITE.exists(): errors.append("_site does not exist; build_site.py must run first");pages=[]
    else:
        pages=sorted(SITE.rglob("*.html"))
        required_files=("index.html","manifest.json","app/app.js","app/style.css","knowledge/indexes/context-graph.json","knowledge/indexes/core-index.json","world-map/index.html","world-map/3d.html","world-map/3d-app.js","world-map/3d-hover.js","world-map/3d-pathfinder.js","world-map/3d-demography.js","world-map/3d-evidence.js","world-map/3d-time.js","world-map/3d-ui.js","world-map/3d-entity-trace.js","world-map/3d-axis.js","world-map/3d-axis-depth.js","world-map/3d-axis-operators.js","data/world-map-3d-runtime.json","data/world-relational-map.json","data/atlas-projection-contract.json","data/atlas-time-contract.json","data/atlas-mathematical-calibration.json","data/atlas-entity-trace-contract.json","data/world-country-demography.json","data/world-country-facts.json","sitemap.xml","llms.txt")
        for rel in required_files:
            if not (SITE/rel).exists(): errors.append(f"missing required site file: {rel}")

        manifest=load_json(SITE/"manifest.json",errors) if (SITE/"manifest.json").exists() else {}
        branches={b.get("id") for b in manifest.get("branches",[]) if b.get("id")};expected={"tim","son","spirit","transformation","cosmology","body","traditions","north","world","chronology","works","sources"};missing=sorted(expected-branches)
        if missing: errors.append(f"built manifest missing branches: {missing}")

        index=SITE/"index.html"
        if index.exists():
            text=index.read_text(encoding="utf-8",errors="replace");require_text(text,('id="reader"','id="branches"',"app/app.js","app/style.css","application/ld+json","llms.txt","sitemap.xml","POTATO"),"index.html",errors)
            for retired in ('id="root-tree"','id="center-frame"','id="frame-content"',"./root.js"):
                if retired in text: warnings.append(f"index.html still contains retired reader marker: {retired}")
            if "<iframe" in text: errors.append("index.html contains retired iframe dependency")

        app=(SITE/"app/app.js").read_text(encoding="utf-8",errors="replace") if (SITE/"app/app.js").exists() else "";require_text(app,("manifest.json","context-graph.json","showContext","showRecord","renderMarkdown"),"app/app.js",errors)
        atlas_path=SITE/"world-map/3d.html";atlas=atlas_path.read_text(encoding="utf-8",errors="replace") if atlas_path.exists() else ""
        require_text(atlas,("World Relational Atlas",'id="map"','id="compare"','id="relationType"','id="traceDepth"','id="timeMenu"','id="timeMode"','id="atlasTimeState"','src="./3d-hover.js"','src="./3d-pathfinder.js"','src="./3d-demography.js"','src="./3d-evidence.js"','src="./3d-time.js"','src="./3d-ui.js"','src="./3d-axis.js"'),"world-map/3d.html",errors)

        copied=("world-map/3d.html","world-map/3d-app.js","world-map/3d-hover.js","world-map/3d-pathfinder.js","world-map/3d-demography.js","world-map/3d-evidence.js","world-map/3d-time.js","world-map/3d-ui.js","world-map/3d-entity-trace.js","world-map/3d-fields.js","world-map/3d-networks.js","world-map/3d-axis.js","world-map/3d-axis-depth.js","world-map/3d-axis-operators.js","data/world-map-3d-runtime.json","data/world-relational-map.json","data/atlas-projection-contract.json","data/atlas-time-contract.json","data/atlas-mathematical-calibration.json","data/atlas-entity-trace-contract.json")
        for rel in copied: require_build_parity(rel,errors)

        runtime_path=SITE/"data/world-map-3d-runtime.json";runtime=load_json(runtime_path,errors) if runtime_path.exists() else {}
        if runtime and runtime.get("status")!="active renderer contract": errors.append("built world-map-3d-runtime must use current active renderer contract status")
        if runtime and runtime.get("compare_mode",{}).get("status") not in {"implemented","implemented-basic"}: errors.append("built world-map runtime does not preserve implemented Compare status")
        if runtime and runtime.get("trace_mode",{}).get("maximum_depth")!=3: errors.append("built world-map runtime does not preserve Trace depth contract")
        if runtime:
            if runtime.get("projection_contract")!="data/atlas-projection-contract.json": errors.append("built world-map runtime does not point to canonical projection contract")
            if runtime.get("time_contract")!="data/atlas-time-contract.json": errors.append("built world-map runtime does not point to canonical time contract")
            if runtime.get("time_mode",{}).get("status")!="implemented-conservative-foundation": errors.append("built runtime does not preserve conservative Time implementation")
            if runtime.get("interface",{}).get("status")!="implemented-progressive-disclosure": errors.append("built runtime does not preserve progressive disclosure UI contract")
            if "experimental" in str(runtime.get("status","")).lower(): errors.append("built world-map runtime reintroduced retired experimental status wording")

        entity_contract_path=SITE/"data/atlas-entity-trace-contract.json"
        if entity_contract_path.exists():
            entity_contract=load_json(entity_contract_path,errors)
            if entity_contract.get("status")!="implemented-one-hop-inspector": errors.append("built entity Trace contract lost implemented one-hop status")
            if entity_contract.get("runtime")!="world-map/3d-entity-trace.js": errors.append("built entity Trace contract lost runtime ownership")
            if entity_contract.get("scope",{}).get("depth")!=1: errors.append("built entity Trace expanded depth without satisfying growth gate")

        calibration_path=SITE/"data/atlas-mathematical-calibration.json"
        if calibration_path.exists():
            calibration=load_json(calibration_path,errors);invariants=calibration.get("invariants",{})
            if calibration.get("status")!="active design/calibration contract": errors.append("built mathematical calibration contract is not active")
            if invariants.get("north_gate_arc_degrees")!=42: errors.append("built mathematical calibration lost 42-degree North-gate geometry invariant")
            if invariants.get("north_gate_arc_is_level_count") is not False: errors.append("built mathematical calibration reinterpreted 42 degrees as a level count")
            if invariants.get("north_gate_arc_is_fibonacci_derived") is not False: errors.append("built mathematical calibration reinterpreted North gate as Fibonacci-derived")

        facts_path=SITE/"data/world-country-facts.json"
        if facts_path.exists():
            facts=load_json(facts_path,errors);countries=facts.get("countries",{});area=facts.get("area_coverage",0)
            if len(countries)!=195: errors.append("built country-facts snapshot must contain 195 canonical countries")
            if facts.get("capital_coverage",0)<190: errors.append("built country-facts capital coverage fell below 190")
            if area<190: errors.append("built country-facts area coverage fell below 190")
            if facts.get("area_definition_coverage")!=area: errors.append("built country-facts snapshot has area values without explicit area semantics")
            ambiguous=[code for code,row in countries.items() if row.get("area_km2") is not None and not row.get("area_field")]
            if ambiguous: errors.append(f"built country-facts area provenance lacks exact source field for: {ambiguous[:8]}")

        demo_path=SITE/"data/world-country-demography.json"
        if demo_path.exists():
            demo=load_json(demo_path,errors)
            if len(demo.get("countries",{}))!=195: errors.append("built demography snapshot must contain 195 canonical countries")
            if demo.get("population_coverage",0)<190: errors.append("built population coverage fell below 190")
            if demo.get("religion_coverage",0)<150: errors.append("built religion coverage fell below 150")

        topic_pages=list((SITE/"topics").glob("*/index.html")) if (SITE/"topics").exists() else [];context_pages=list((SITE/"context").glob("*/index.html")) if (SITE/"context").exists() else [];record_pages=list((SITE/"records").glob("*/index.html")) if (SITE/"records").exists() else []
        if len(topic_pages)<len(expected): errors.append(f"expected at least {len(expected)} topic pages; found {len(topic_pages)}")
        if not context_pages: errors.append("no generated context pages found")
        if not record_pages: errors.append("no generated record pages found")

        sitemap=(SITE/"sitemap.xml").read_text(encoding="utf-8",errors="replace") if (SITE/"sitemap.xml").exists() else ""
        for fragment in ("/topics/tim/","/topics/son/","/records/tim-dooley/","/context/"):
            if fragment not in sitemap: errors.append(f"sitemap.xml missing expected route fragment: {fragment}")
        llms=(SITE/"llms.txt").read_text(encoding="utf-8",errors="replace") if (SITE/"llms.txt").exists() else "";llms_lower=llms.lower()
        for term in ("tim dooley","potato of life","generated canonical topics","generated contextual constellations"):
            if term not in llms_lower: errors.append(f"llms.txt missing discovery term/section: {term}")

        ref=re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''',re.I);base_ref=re.compile(r'''<base\s+[^>]*href=["']([^"'#?]+)["']''',re.I);bad=[]
        site_root=SITE.resolve()
        for html in pages:
            html_text=html.read_text(encoding="utf-8",errors="replace")
            base_dir=html.parent.resolve()
            base_match=base_ref.search(html_text)
            if base_match:
                base_raw=base_match.group(1)
                if not base_raw.startswith(("http:","https:","mailto:","javascript:","data:")):
                    candidate=(html.parent/base_raw).resolve()
                    try: candidate.relative_to(site_root);base_dir=candidate
                    except ValueError: pass
            for raw in ref.findall(html_text):
                if raw.startswith(("http:","https:","mailto:","javascript:","data:")): continue
                target=(base_dir/raw).resolve()
                try: target.relative_to(site_root)
                except ValueError: continue
                if not target.exists(): bad.append(f"{html.relative_to(SITE)} -> {raw}")
        if bad: errors.append(f"broken local references in built site: {len(bad)}; examples: {bad[:8]}")
        if not pages: errors.append("Pages artifact contains no HTML documents")

    lines=[f"Built HTML pages checked: {len(pages)}",f"Errors: {len(errors)} · Warnings: {len(warnings)}"]+[f"WARNING: {w}" for w in warnings[:50]]
    if errors: lines.append("SITE SHELL VALIDATION FAILED");lines.extend(f"- {e}" for e in errors)
    else: lines.append("SITE SHELL VALIDATION PASSED")
    report="\n".join(lines)+"\n";REPORT.write_text(report,encoding="utf-8");print(report,end="");return 1 if errors else 0

if __name__=="__main__": raise SystemExit(main())