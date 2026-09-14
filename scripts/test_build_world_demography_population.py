import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_world_demography as builder


class DemographyPopulationBuilderTests(unittest.TestCase):
    def test_local_population_normalizes_required_runtime_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "demo.json").write_text(json.dumps({
                "updated": "2025-01-01",
                "observations": {
                    "population": {
                        "value": 123456,
                        "year": 2024,
                        "source": "National statistics office"
                    }
                }
            }), encoding="utf-8")
            with patch.object(builder, "COUNTRIES_DIR", root):
                population = builder.local_population({"id": "demo"})

        self.assertEqual(population["value"], 123456)
        self.assertEqual(population["unit"], "persons")
        self.assertEqual(population["period"], 2024)
        self.assertEqual(population["resolution_tier"], "canonical-observation")

    def test_population_payload_rejects_incomplete_coverage(self):
        index = {"countries": [{"iso3": "AFG"}, {"iso3": "ALB"}]}
        cell = {
            "value": 100,
            "unit": "persons",
            "period": 2023,
            "source": "fixture",
            "resolution_tier": "global-fallback"
        }
        complete = {
            "population_coverage": 2,
            "countries": {
                "AFG": {"population": dict(cell)},
                "ALB": {"population": dict(cell)}
            }
        }
        builder.ensure_population_complete(index, complete, expected=2)
        del complete["countries"]["ALB"]
        complete["population_coverage"] = 1
        with self.assertRaises(RuntimeError):
            builder.ensure_population_complete(index, complete, expected=2)


if __name__ == "__main__":
    unittest.main()
