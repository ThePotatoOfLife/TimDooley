import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world_subdivision_canada as canada


class CanadaSubdivisionBuilderTests(unittest.TestCase):
    def test_normalizes_all_thirteen_provinces_and_territories(self):
        features = []
        for pruid, name, abbr in [
            ('10','Newfoundland and Labrador','N.L.'),('11','Prince Edward Island','P.E.I.'),
            ('12','Nova Scotia','N.S.'),('13','New Brunswick','N.B.'),('24','Quebec','Que.'),
            ('35','Ontario','Ont.'),('46','Manitoba','Man.'),('47','Saskatchewan','Sask.'),
            ('48','Alberta','Alta.'),('59','British Columbia','B.C.'),('60','Yukon','Y.T.'),
            ('61','Northwest Territories','N.W.T.'),('62','Nunavut','Nvt.'),
        ]:
            features.append({
                'type':'Feature',
                'properties':{'PRUID':pruid,'PRNAME':name,'PREABBR':abbr,'LANDAREA':123.4},
                'geometry':{'type':'Polygon','coordinates':[[[-100,50],[-99,50],[-99,51],[-100,51],[-100,50]]]},
            })
        result = canada.normalize_canada(features)
        self.assertEqual(len(result['features']), 13)
        by_name = {f['properties']['name']:f['properties'] for f in result['features']}
        self.assertEqual(by_name['Ontario']['id'], 'CA-ON')
        self.assertEqual(by_name['Ontario']['code'], 'ON')
        self.assertEqual(by_name['Ontario']['source_uid'], '35')
        self.assertEqual(by_name['Nunavut']['id'], 'CA-NU')
        self.assertEqual(by_name['Northwest Territories']['subdivision_type'], 'territory')
        self.assertNotIn('population', by_name['Ontario'])

    def test_partial_canada_response_is_rejected(self):
        with self.assertRaises(RuntimeError):
            canada.normalize_canada([{
                'type':'Feature',
                'properties':{'PRUID':'35','PRNAME':'Ontario','PREABBR':'Ont.','LANDAREA':1},
                'geometry':{'type':'Polygon','coordinates':[[[-80,44],[-79,44],[-79,45],[-80,45],[-80,44]]]},
            }])

    def test_index_descriptor_is_geometry_free(self):
        features = []
        for pruid, postal in canada.PRUID_TO_POSTAL.items():
            features.append({'type':'Feature','properties':{'id':f'CA-{postal}','name':postal,'code':postal,'source_uid':pruid,'parent_iso3':'CAN','parent_name':'Canada','subdivision_type':'province'},'geometry':{'type':'Polygon','coordinates':[]}})
        descriptor = canada.canada_descriptor(features)
        self.assertEqual(descriptor['feature_count'], 13)
        self.assertEqual(descriptor['id_prefix'], 'CA-')
        self.assertTrue(all('geometry' not in row for row in descriptor['search_records']))


if __name__ == '__main__':
    unittest.main()
