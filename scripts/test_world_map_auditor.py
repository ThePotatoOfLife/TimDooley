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
    proc = subprocess.run(
        [sys.executable, str(AUDITOR), "--root", str(root), "--contract", str(contract_path), "--report", str(report)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
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
url.searchParams.set('country', 'DNK');
window.__potatoAtlasThing = {ready:true};
const node = document.createElement('div'); node.id = 'atlasThing';
""")
            proc, report = run_auditor(root)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            resources = {row["resource"] for rows in report["inventory"].values() for row in rows}
            for resource in (
                "source:countries", "layer:countries-fill", "feature-state:countries:selected",
                "feature-state:countries:active", "paint:countries-line:line-width",
                "layout:countries-fill:visibility", "set-data:countries",
                "map-event:click:countries-fill", "style-restore:world-map/3d-a.js",
                "url:country", "api:__potatoAtlasThing", "dom:atlasThing",
            ):
                self.assertIn(resource, resources)

    def test_duplicate_source_and_layer_creation_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-a.js", "map.addSource('dup',{}); map.addLayer({id:'dup-layer',source:'dup',type:'fill'});")
            write_module(root, "3d-b.js", "map.addSource('dup',{}); map.addLayer({id:'dup-layer',source:'dup',type:'fill'});")
            proc, report = run_auditor(root)
            self.assertEqual(proc.returncode, 1)
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("duplicate-source-owner", codes)
            self.assertIn("duplicate-layer-owner", codes)

    def test_duplicate_feature_state_blocks_unless_shared(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-a.js", "map.setFeatureState({source:'countries',id:'DNK'},{selected:true});")
            write_module(root, "3d-b.js", "map.setFeatureState({source:'countries',id:'DEU'},{selected:false});")
            proc, report = run_auditor(root)
            self.assertEqual(proc.returncode, 1)
            self.assertTrue(any(f["code"] == "feature-state-owner-collision" for f in report["findings"]))
            contract = {
                "schema_version": "1.0",
                "shared": {
                    "feature-state:countries:selected": {
                        "modules": ["world-map/3d-a.js", "world-map/3d-b.js"],
                        "rationale": "Fixture intentionally shares the selected state key."
                    }
                }
            }
            proc, report = run_auditor(root, contract)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_hover_popup_requires_atlas_hover_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-a.js", "map.on('mousemove','countries-fill',e=>popup.setHTML('<b>Country</b>').addTo(map)); const popup=new maplibregl.Popup();")
            proc, report = run_auditor(root)
            self.assertEqual(proc.returncode, 1)
            self.assertTrue(any(f["code"] == "transient-popup-class-missing" for f in report["findings"]))

    def test_multiple_styledata_participants_warn(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-a.js", "let restoring=false; map.on('styledata',()=>queueMicrotask(restore));")
            write_module(root, "3d-b.js", "let restoring=false; map.on('styledata',()=>queueMicrotask(restore));")
            proc, report = run_auditor(root)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue(any(f["code"] == "multiple-style-restorers" and f["severity"] == "warning" for f in report["findings"]))

    def test_missing_declared_owner_blocks_and_stale_shared_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-a.js", "map.addSource('countries',{});")
            contract = {
                "schema_version": "1.0",
                "owners": {"source:countries": ["world-map/missing.js"]},
                "shared": {"source:unused": {"modules": ["world-map/3d-a.js", "world-map/3d-b.js"], "rationale": "Fixture stale share."}}
            }
            proc, report = run_auditor(root, contract)
            self.assertEqual(proc.returncode, 1)
            codes = {(f["code"], f["severity"]) for f in report["findings"]}
            self.assertIn(("declared-owner-module-missing", "error"), codes)
            self.assertIn(("stale-contract-entry", "warning"), codes)

    def test_report_order_is_deterministic_ignoring_generated_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_module(root, "3d-b.js", "map.addSource('b',{});")
            write_module(root, "3d-a.js", "map.addSource('a',{});")
            proc1, report1 = run_auditor(root)
            proc2, report2 = run_auditor(root)
            self.assertEqual(proc1.returncode, 0)
            self.assertEqual(proc2.returncode, 0)
            report1.pop("generated_at", None)
            report2.pop("generated_at", None)
            self.assertEqual(report1, report2)


if __name__ == "__main__":
    unittest.main()
