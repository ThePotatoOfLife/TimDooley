import csv
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enrich_world_subdivision_population as enrich


class WorldSubdivisionPopulationTests(unittest.TestCase):
    def test_region_population_rows_map_to_danish_subdivision_ids(self):
        tableinfo = {
            "variables": [
                {"id": "OMRÅDE", "text": "region", "values": [
                    {"id": "01", "text": "Region Hovedstaden"},
                    {"id": "02", "text": "Region Sjælland"},
                    {"id": "03", "text": "Region Syddanmark"},
                    {"id": "04", "text": "Region Midtjylland"},
                    {"id": "05", "text": "Region Nordjylland"},
                ]},
                {"id": "KØN", "text": "sex", "values": [{"id": "TOT", "text": "Total"}]},
                {"id": "ALDER", "text": "age", "values": [{"id": "TOT", "text": "Age, total"}]},
                {"id": "TID", "text": "year", "values": [{"id": "2026", "text": "2026"}]},
            ]
        }
        selection = enrich.statbank_selection(tableinfo, period="2026")
        self.assertEqual(selection["region_values"], ["01", "02", "03", "04", "05"])
        self.assertEqual(selection["sex_total"], "TOT")
        self.assertEqual(selection["age_total"], "TOT")
        self.assertEqual(selection["time_value"], "2026")

        csv_text = "region;sex;age;year;content\nRegion Midtjylland;Total;Age, total;2026;1385000\nRegion Syddanmark;Total;Age, total;2026;1240000\n"
        rows = enrich.parse_statbank_population_csv(csv_text)
        self.assertEqual(rows["Region Midtjylland"], 1385000)
        self.assertEqual(rows["Region Syddanmark"], 1240000)

    def test_enrichment_preserves_unknowns_and_adds_provenance(self):
        payload = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"id": "DK-1082", "name": "Region Midtjylland"}, "geometry": None},
                {"type": "Feature", "properties": {"id": "DK-1083", "name": "Region Syddanmark"}, "geometry": None},
            ],
        }
        enriched = enrich.enrich_denmark_payload(payload, {"Region Midtjylland": 1385000}, period="2026")
        first = enriched["features"][0]["properties"]
        second = enriched["features"][1]["properties"]
        self.assertEqual(first["population"]["value"], 1385000)
        self.assertEqual(first["population"]["unit"], "persons")
        self.assertEqual(first["population"]["period"], "2026")
        self.assertIn("Statistics Denmark", first["population"]["source"])
        self.assertNotIn("population", second)


if __name__ == "__main__":
    unittest.main()
