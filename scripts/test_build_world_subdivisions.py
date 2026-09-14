import unittest

import build_world_subdivisions as builder


class WorldSubdivisionBuilderTests(unittest.TestCase):
    def test_parse_census_kml_feature_to_geojson(self):
        kml = b'''<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2"><Document><Folder><Placemark>
          <ExtendedData><SchemaData>
            <SimpleData name="STATEFP">06</SimpleData>
            <SimpleData name="STUSPS">CA</SimpleData>
            <SimpleData name="NAME">California</SimpleData>
            <SimpleData name="ALAND">403673617862</SimpleData>
            <SimpleData name="AWATER">20291712025</SimpleData>
          </SchemaData></ExtendedData>
          <MultiGeometry><Polygon><outerBoundaryIs><LinearRing><coordinates>
            -124,42,0 -114,42,0 -114,32,0 -124,32,0 -124,42,0
          </coordinates></LinearRing></outerBoundaryIs></Polygon></MultiGeometry>
        </Placemark></Folder></Document></kml>'''
        features = builder.parse_state_kml(kml)
        self.assertEqual(len(features), 1)
        feature = features[0]
        self.assertEqual(feature["properties"]["STATE"], "06")
        self.assertEqual(feature["properties"]["STUSAB"], "CA")
        self.assertEqual(feature["properties"]["NAME"], "California")
        self.assertEqual(feature["geometry"]["type"], "Polygon")
        self.assertEqual(feature["geometry"]["coordinates"][0][0], [-124.0, 42.0])

    def test_normalize_us_state_joins_population_and_preserves_provenance(self):
        feature = {
            "type": "Feature",
            "properties": {
                "STATE": "06",
                "STUSAB": "CA",
                "NAME": "California",
                "AREALAND": "403673617862",
                "AREAWATER": "20291712025"
            },
            "geometry": {"type": "Polygon", "coordinates": []}
        }
        population = {"06": 39431263}
        normalized = builder.normalize_us_state(feature, population)
        props = normalized["properties"]
        self.assertEqual(props["id"], "US-CA")
        self.assertEqual(props["parent_iso3"], "USA")
        self.assertEqual(props["subdivision_type"], "state")
        self.assertEqual(props["population"]["value"], 39431263)
        self.assertEqual(props["population"]["period"], 2025)
        self.assertEqual(props["population"]["unit"], "persons")
        self.assertGreater(props["area_km2"], 400000)

    def test_dc_is_typed_as_federal_district(self):
        feature = {
            "type": "Feature",
            "properties": {"STATE": "11", "STUSAB": "DC", "NAME": "District of Columbia", "AREALAND": "158316124", "AREAWATER": "18654647"},
            "geometry": {"type": "Polygon", "coordinates": []}
        }
        normalized = builder.normalize_us_state(feature, {"11": 702250})
        self.assertEqual(normalized["properties"]["subdivision_type"], "federal district")


if __name__ == "__main__":
    unittest.main()
