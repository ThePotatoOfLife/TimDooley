from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITOR = ROOT / "scripts" / "audit_world_map.py"


def run_auditor(root: Path, contract: dict | None = None):
    contract_path = root / "data" / "world-map-audit-contract.json"
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(json.dumps(contract or {"schema_version": "1.0"}) + "\n", encoding="utf-8")
    report = root / "world-map-audit-report.json"
    proc = subprocess.run([sys.executable, str(AUDITOR), "--root", str(root), "--contract", str(contract_path), "--report", str(report)], cwd=ROOT, text=True, capture_output=True)
    payload = json.loads(report.read_text(encoding="utf-8")) if report.exists() else None
    return proc, payload


def write_module(root: Path, name: str, source: str) -> None:
    path = root / "world-map" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


class AuditorTests(unittest.TestCase):
    def test_inventory_extracts_literal_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-a.js", """
map.addSource('countries', {type:'geojson'});
map.addLayer({id:'countries-fill', type:'fill', source:'countries'});
map.setFeatureState({source:'countries', id:'DNK'}, {selected:true, active:false});
map.setPaintProperty('countries-line', 'line-width', 2);
map.setLayoutProperty('countries-fill', 'visibility', 'visible');
map.getSource('countries').setData(data);
map.on('click', 'countries-fill', handler);
map.on('styledata', restore);
const popup = new maplibregl.Popup().setHTML('<div class="atlas-hover">Hi</div>');
const url = new URL(location.href); url.searchParams.set('country', 'DNK'); history.replaceState({}, '', url);
window.__potatoAtlasThing = {ready:true};
const node = document.createElement('div'); node.id = 'atlasThing';
""")
            proc, report = run_auditor(root)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            resources = {row["resource"] for rows in report["inventory"].values() for row in rows}
            for resource in ("source:countries", "layer:countries-fill", "feature-state:countries:selected", "feature-state:countries:active", "paint:countries-line:line-width", "layout:countries-fill:visibility", "set-data:countries", "map-event:click:countries-fill", "style-restore:world-map/3d-a.js", "url:country", "api:__potatoAtlasThing", "dom:atlasThing"):
                self.assertIn(resource, resources)

    def test_duplicate_source_and_layer_creation_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-a.js", "map.addSource('dup',{}); map.addLayer({id:'dup-layer',source:'dup',type:'fill'});")
            write_module(root, "3d-b.js", "map.addSource('dup',{}); map.addLayer({id:'dup-layer',source:'dup',type:'fill'});")
            proc, report = run_auditor(root)
            self.assertEqual(proc.returncode, 1)
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("duplicate-source-owner", codes); self.assertIn("duplicate-layer-owner", codes)

    def test_duplicate_feature_state_blocks_unless_shared(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-a.js", "map.setFeatureState({source:'countries',id:'DNK'},{selected:true});")
            write_module(root, "3d-b.js", "map.setFeatureState({source:'countries',id:'DEU'},{selected:false});")
            proc, report = run_auditor(root); self.assertEqual(proc.returncode, 1)
            self.assertTrue(any(f["code"] == "feature-state-owner-collision" for f in report["findings"]))
            contract={"schema_version":"1.0","shared":{"feature-state:countries:selected":{"modules":["world-map/3d-a.js","world-map/3d-b.js"],"rationale":"Fixture intentionally shares selected."}}}
            proc, report=run_auditor(root,contract); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)

    def test_feature_state_parser_does_not_invent_ternary_value_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-a.js","map.setFeatureState({source:'countries',id:code},{atlasScalarHas:Number.isFinite(value),atlasScalarValue:Number.isFinite(value) ? value : 0});")
            proc,report=run_auditor(root); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)
            self.assertEqual({r["resource"] for r in report["inventory"].get("feature_state_write",[])},{"feature-state:countries:atlasScalarHas","feature-state:countries:atlasScalarValue"})

    def test_hover_popup_requires_atlas_hover_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-a.js","map.on('mousemove','countries-fill',e=>popup.setHTML('<b>Country</b>').addTo(map)); const popup=new maplibregl.Popup();")
            proc,report=run_auditor(root); self.assertEqual(proc.returncode,1); self.assertTrue(any(f["code"]=="transient-popup-class-missing" for f in report["findings"]))

    def test_click_popup_is_not_misclassified_by_nearby_mouseenter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-a.js","map.on('mouseenter','points',()=>{}); map.on('click','points',event=>{ const popup = new maplibregl.Popup({closeButton:true}).setHTML('<b>Persistent</b>').addTo(map); });")
            proc,report=run_auditor(root); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout); self.assertFalse(any(f["code"]=="transient-popup-class-missing" for f in report["findings"]))

    def test_template_html_id_is_not_treated_as_literal_dom_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-a.js","const html = `<button id=\"${esc(asset.id)}\">x</button>`; const node=document.createElement('div'); node.id='literalId';")
            proc,report=run_auditor(root); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout); self.assertEqual({r["resource"] for r in report["inventory"].get("dom_id",[])},{"dom:literalId"})

    def test_multiple_styledata_participants_warn(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-a.js","let restoring=false; map.on('styledata',()=>queueMicrotask(restore));"); write_module(root,"3d-b.js","let restoring=false; map.on('styledata',()=>queueMicrotask(restore));")
            proc,report=run_auditor(root); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout); self.assertTrue(any(f["code"]=="multiple-style-restorers" for f in report["findings"]))

    def test_central_style_owner_and_registered_participants_do_not_warn(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            write_module(root,"3d-style-lifecycle.js","function schedule(){queueMicrotask(restore);} map.on('styledata',()=>schedule('styledata'));")
            write_module(root,"3d-a.js","styleLifecycle.register('a',{restore:()=>restoreA()});")
            write_module(root,"3d-b.js","styleLifecycle.register('b',{restore:()=>restoreB()});")
            contract={"schema_version":"1.0","style_restoration":{"owner_module":"world-map/3d-style-lifecycle.js","participants":{"world-map/3d-a.js":"a","world-map/3d-b.js":"b"}}}
            proc,report=run_auditor(root,contract); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)
            codes={f["code"] for f in report["findings"]}
            self.assertNotIn("unapproved-style-restorer",codes)
            self.assertNotIn("stale-style-participant-contract",codes)
            self.assertNotIn("unapproved-style-participant",codes)

    def test_direct_styledata_listener_outside_central_owner_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            write_module(root,"3d-style-lifecycle.js","function schedule(){queueMicrotask(restore);} map.on('styledata',()=>schedule('styledata'));")
            write_module(root,"3d-a.js","map.on('styledata',()=>queueMicrotask(restoreA));")
            contract={"schema_version":"1.0","style_restoration":{"owner_module":"world-map/3d-style-lifecycle.js","participants":{}}}
            proc,report=run_auditor(root,contract); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)
            self.assertTrue(any(f["code"]=="unapproved-style-restorer" for f in report["findings"]))

    def test_style_participant_contract_detects_stale_and_unapproved_registration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            write_module(root,"3d-style-lifecycle.js","function schedule(){queueMicrotask(restore);} map.on('styledata',()=>schedule('styledata'));")
            write_module(root,"3d-a.js","styleLifecycle.register('actual',{restore:()=>restoreA()});")
            write_module(root,"3d-b.js","const x=1;")
            contract={"schema_version":"1.0","style_restoration":{"owner_module":"world-map/3d-style-lifecycle.js","participants":{"world-map/3d-b.js":"expected"}}}
            proc,report=run_auditor(root,contract); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)
            codes={f["code"] for f in report["findings"]}
            self.assertIn("unapproved-style-participant",codes)
            self.assertIn("stale-style-participant-contract",codes)

    def test_module_version_url_is_not_browser_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-a.js","const url=new URL(path,import.meta.url); url.searchParams.set('v','123'); return url.href;")
            proc,report=run_auditor(root); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout); self.assertNotIn("url:v",{r["resource"] for r in report["inventory"].get("url_write",[])})

    def test_history_persisted_url_is_browser_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-a.js","const url=new URL(location.href); url.searchParams.set('country','DNK'); history.replaceState({},'',url);")
            proc,report=run_auditor(root); self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout); self.assertIn("url:country",{r["resource"] for r in report["inventory"].get("url_write",[])})

    def test_missing_declared_owner_blocks_and_stale_shared_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-a.js","map.addSource('countries',{});")
            contract={"schema_version":"1.0","owners":{"source:countries":["world-map/missing.js"]},"shared":{"source:unused":{"modules":["world-map/3d-a.js","world-map/3d-b.js"],"rationale":"stale"}}}; proc,report=run_auditor(root,contract); self.assertEqual(proc.returncode,1)
            codes={(f["code"],f["severity"]) for f in report["findings"]}; self.assertIn(("declared-owner-module-missing","error"),codes); self.assertIn(("stale-contract-entry","warning"),codes)


    def test_findings_include_problem_queue_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            write_module(root,"3d-a.js","map.addSource('dup',{});")
            write_module(root,"3d-b.js","map.addSource('dup',{});")
            proc,report=run_auditor(root)
            self.assertEqual(proc.returncode,1)
            finding=next(f for f in report["findings"] if f["code"]=="duplicate-source-owner")
            self.assertEqual(finding.get("queue_id"),"WM-006")
            self.assertIn("Render Stack",finding.get("owner",""))
            self.assertIn("WM-006",proc.stdout)

    def test_report_order_is_deterministic_ignoring_generated_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_module(root,"3d-b.js","map.addSource('b',{});"); write_module(root,"3d-a.js","map.addSource('a',{});")
            p1,r1=run_auditor(root); p2,r2=run_auditor(root); self.assertEqual(p1.returncode,0); self.assertEqual(p2.returncode,0); r1.pop("generated_at",None); r2.pop("generated_at",None); self.assertEqual(r1,r2)

if __name__ == "__main__": unittest.main()
