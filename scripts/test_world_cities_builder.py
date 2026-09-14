import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world_cities as cities
import geonames_city_acquisition as geonames


class WorldCitiesBuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.index = self.root / 'index.json'
        self.capitals = self.root / 'capitals.geo.json'
        self.out = self.root / 'cities.geo.json'
        self.index.write_text(json.dumps({'countries': [
            {'iso2':'AA','iso3':'AAA','name':'Alpha'}, {'iso2':'BB','iso3':'BBB','name':'Beta'}
        ]}), encoding='utf-8')
        self.capitals.write_text(json.dumps({'type':'FeatureCollection','features':[
            {'type':'Feature','properties':{'iso3':'AAA','name':'Alpha City','country':'Alpha','primary':True,'scalerank':2,'source':'fixture'},'geometry':{'type':'Point','coordinates':[10,20]}},
            {'type':'Feature','properties':{'iso3':'BBB','name':'Beta City','country':'Beta','primary':True,'scalerank':3,'source':'fixture'},'geometry':{'type':'Point','coordinates':[30,40]}}
        ]}), encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def test_acquisition_failure_keeps_capital_baseline(self):
        payload = cities.build(out_path=self.out,index_path=self.index,capitals_path=self.capitals,acquisition=lambda: (_ for _ in ()).throw(RuntimeError('offline')),expected_country_count=2)
        self.assertEqual(len(payload['features']), 2)
        self.assertEqual({f['properties']['iso3'] for f in payload['features']}, {'AAA','BBB'})
        self.assertIn('offline', payload['acquisition_errors'][0])

    def test_large_city_selection_and_capital_merge_are_bounded(self):
        rows = [
            {'qid':'Q1','name':'Alpha City','iso3':'AAA','coordinates':[10.01,20.01],'population':800000,'population_period':'2025-01-01','admin_region':'A1'},
            {'qid':'Q2','name':'Alpha Metro','iso3':'AAA','coordinates':[11,21],'population':1200000,'population_period':'2024-01-01','admin_region':'A1'},
            {'qid':'Q3','name':'Alpha Town','iso3':'AAA','coordinates':[12,22],'population':300000,'population_period':'2024-01-01','admin_region':'A2'},
            {'qid':'Q4','name':'Tiny Place','iso3':'AAA','coordinates':[13,23],'population':100000,'population_period':'2024-01-01','admin_region':'A2'},
        ]
        payload = cities.build(out_path=self.out,index_path=self.index,capitals_path=self.capitals,acquisition=lambda: rows,expected_country_count=2)
        ids = {f['properties']['id'] for f in payload['features']}
        self.assertIn('wd:Q1', ids)
        self.assertIn('wd:Q2', ids)
        self.assertIn('wd:Q3', ids)
        self.assertNotIn('wd:Q4', ids)
        self.assertLessEqual(len(payload['features']), cities.MAX_FEATURES)
        self.assertLessEqual(self.out.stat().st_size, cities.MAX_BYTES)

    def test_nearby_district_does_not_replace_capital_without_identity_match(self):
        rows = [
            {'source_key':'geonames','source_id':'district','name':'Alpha Inner District','iso3':'AAA','coordinates':[10.01,20.01],'population':26000,'aliases':['Inner Alpha'],'source':'fixture','coordinate_source':'fixture','population_source':'fixture'},
            {'source_key':'geonames','source_id':'capital','name':'Alpha City','iso3':'AAA','coordinates':[10.03,20.03],'population':700000,'aliases':['Alpha Capital'],'source':'fixture','coordinate_source':'fixture','population_source':'fixture'},
        ]
        payload = cities.build(out_path=self.out,index_path=self.index,capitals_path=self.capitals,acquisition=lambda:rows,expected_country_count=2)
        alpha_capital = next(f for f in payload['features'] if f['properties'].get('capital') and f['properties'].get('iso3') == 'AAA')
        self.assertEqual(alpha_capital['properties']['id'], 'gn:capital')
        self.assertEqual(alpha_capital['properties']['name'], 'Alpha City')

    def test_geonames_candidate_preserves_source_and_aliases(self):
        rows = [{
            'source_key':'geonames','source_id':'123','name':'Alpha Metro','iso3':'AAA',
            'coordinates':[11,21],'population':900000,'aliases':['Alpha Metropolis'],
            'source':'GeoNames cities15000','coordinate_source':'GeoNames latitude/longitude',
            'population_source':'GeoNames population field'
        }]
        payload = cities.build(out_path=self.out,index_path=self.index,capitals_path=self.capitals,acquisition=lambda:rows,expected_country_count=2)
        feature = next(f for f in payload['features'] if f['properties']['id'] == 'gn:123')
        self.assertEqual(feature['properties']['source'], 'GeoNames cities15000')
        self.assertEqual(feature['properties']['coordinate_source'], 'GeoNames latitude/longitude')
        self.assertEqual(feature['properties']['population_source'], 'GeoNames population field')
        self.assertIn('Alpha Metropolis', feature['properties']['aliases'])

    def test_geonames_parser_resolves_admin_region(self):
        canonical = {'AAA': {'iso2':'AA','iso3':'AAA','name':'Alpha'}}
        fields = ['123','Alpha Local','Alpha Metro','Alpha Metropolis,Alpha M','21','11','P','PPL','AA','','01','','','','900000','','','Zone/Test','2026-01-01']
        rows = geonames.parse_geonames_text('\t'.join(fields), canonical, {'AA.01':'Alpha Region'})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['admin_region'], 'Alpha Region')
        self.assertIn('Alpha Metropolis', rows[0]['aliases'])

    def test_invalid_identity_or_population_is_rejected(self):
        bad = [{'qid':'Q9','name':'Ghost','iso3':'ZZZ','coordinates':[0,0],'population':1}]
        with self.assertRaisesRegex(RuntimeError, 'noncanonical ISO3'):
            cities.build(out_path=self.out,index_path=self.index,capitals_path=self.capitals,acquisition=lambda:bad,expected_country_count=2)
        bad2 = [{'qid':'Q8','name':'Zero','iso3':'AAA','coordinates':[0,0],'population':0}]
        with self.assertRaisesRegex(RuntimeError, 'invalid population'):
            cities.build(out_path=self.out,index_path=self.index,capitals_path=self.capitals,acquisition=lambda:bad2,expected_country_count=2)


if __name__ == '__main__':
    unittest.main()
