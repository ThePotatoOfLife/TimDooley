import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world_subdivisions as subdivisions


class WorldSubdivisionBuilderTests(unittest.TestCase):
    def test_denmark_regions_normalize_without_invented_population(self):
        payload = {
            'type':'FeatureCollection',
            'features':[
                {
                    'type':'Feature',
                    'properties':{'kode':'1082','navn':'Region Midtjylland','nuts2':'DK04','geo_version':7},
                    'geometry':{'type':'Polygon','coordinates':[[[8.0,55.7],[10.8,55.7],[10.8,57.8],[8.0,57.8],[8.0,55.7]]]},
                },
                {
                    'type':'Feature',
                    'properties':{'kode':'1083','navn':'Region Syddanmark','nuts2':'DK03','geo_version':8},
                    'geometry':{'type':'Polygon','coordinates':[[[8.0,54.7],[10.9,54.7],[10.9,56.0],[8.0,56.0],[8.0,54.7]]]},
                },
            ],
        }
        result = subdivisions.normalize_denmark_regions(payload)
        self.assertEqual(len(result['features']), 2)
        first = result['features'][0]['properties']
        self.assertEqual(first['id'], 'DK-1082')
        self.assertEqual(first['parent_iso3'], 'DNK')
        self.assertEqual(first['parent_name'], 'Denmark')
        self.assertEqual(first['subdivision_type'], 'region')
        self.assertNotIn('population', first, 'missing Statistics Denmark data must remain missing rather than become zero')
        self.assertEqual(first['geometry_source'], 'Danish Agency for Climate Data (DAWA/Dataforsyningen)')

    def test_search_records_are_geometry_free(self):
        features = [{
            'type':'Feature',
            'properties':{'id':'DK-1082','name':'Region Midtjylland','code':'1082','parent_iso3':'DNK','parent_name':'Denmark','subdivision_type':'region'},
            'geometry':{'type':'Polygon','coordinates':[]},
        }]
        records = subdivisions.subdivision_search_records(features, 'Denmark')
        self.assertEqual(records[0]['id'], 'DK-1082')
        self.assertNotIn('geometry', records[0])


if __name__ == '__main__':
    unittest.main()
