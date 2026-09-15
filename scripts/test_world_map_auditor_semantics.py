from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_world_map", ROOT / "scripts" / "audit_world_map.py")
auditor = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(auditor)


class AuditorSemanticTests(unittest.TestCase):
    def scan(self, source: str):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            world = root / "world-map"
            world.mkdir()
            path = world / "3d-a.js"
            path.write_text(source, encoding="utf-8")
            return auditor.scan_module(path, root)

    def test_module_version_url_is_not_browser_state(self):
        records = self.scan("""
function versioned(path) {
  const url = new URL(path, import.meta.url);
  url.searchParams.set('v', '123');
  return url.href;
}
""")
        self.assertFalse(any(row["resource"] == "url:v" for row in records))

    def test_history_persisted_url_is_browser_state(self):
        records = self.scan("""
function updateUrl() {
  const url = new URL(location.href);
  url.searchParams.set('country', 'DNK');
  history.replaceState({}, '', url);
}
""")
        self.assertTrue(any(row["resource"] == "url:country" for row in records))

    def test_approved_guarded_style_restorers_do_not_warn_as_collision(self):
        records = []
        modules = {"world-map/3d-a.js", "world-map/3d-b.js"}
        for module in sorted(modules):
            records.append(auditor.record(
                "style_restore", f"style-restore:{module}", module, "styledata", 10,
                guarded=True, deferred=True,
            ))
        contract = {
            "schema_version": "1.0",
            "style_restoration": {
                "allowed_modules": {
                    "world-map/3d-a.js": "Fixture restoration owner.",
                    "world-map/3d-b.js": "Fixture restoration owner."
                }
            }
        }
        findings, _ = auditor.analyze(records, contract, modules)
        self.assertFalse(any(item["code"] == "multiple-style-restorers" for item in findings))

    def test_unapproved_style_restorer_warns(self):
        module = "world-map/3d-a.js"
        records = [auditor.record(
            "style_restore", f"style-restore:{module}", module, "styledata", 10,
            guarded=True, deferred=True,
        )]
        contract = {"schema_version": "1.0", "style_restoration": {"allowed_modules": {}}}
        findings, _ = auditor.analyze(records, contract, {module})
        self.assertTrue(any(item["code"] == "unapproved-style-restorer" for item in findings))


if __name__ == "__main__":
    unittest.main()
