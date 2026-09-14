import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world_country_metrics as metrics


class WorldCountryMetricsTests(unittest.TestCase):
    def test_registry_is_neutral_and_contains_core_dimensions(self):
        required = {
            'population','gdp','gdp_per_capita','real_growth','inflation','unemployment',
            'labor_force_participation','life_expectancy','urbanization','internet_penetration',
            'electricity_access','trade_openness','co2_per_capita','fdi_inflow',
        }
        self.assertTrue(required <= set(metrics.METRICS))
        for metric_id, spec in metrics.METRICS.items():
            self.assertEqual(spec['semantic_role'], 'dated-observation')
            self.assertFalse(spec.get('axis_score', True), f'{metric_id} must never become Axis score')
            self.assertTrue(spec['indicator'])
            self.assertTrue(spec['unit'])

    def test_normalizes_latest_and_previous_without_inventing_zero(self):
        rows = [
            {'countryiso3code':'DNK','indicator':{'id':'NY.GDP.MKTP.CD'},'value':400.0,'date':'2024'},
            {'countryiso3code':'DNK','indicator':{'id':'NY.GDP.MKTP.CD'},'value':390.0,'date':'2023'},
            {'countryiso3code':'DNK','indicator':{'id':'FP.CPI.TOTL.ZG'},'value':None,'date':'2024'},
            {'countryiso3code':'USA','indicator':{'id':'NY.GDP.MKTP.CD'},'value':29000.0,'date':'2024'},
        ]
        grouped = metrics.group_world_bank_rows(rows, {'DNK','USA'})
        denmark = grouped['gdp']['DNK']
        self.assertEqual(denmark[0], {'value':400.0,'year':2024})
        self.assertEqual(denmark[1], {'value':390.0,'year':2023})
        self.assertEqual(grouped['inflation']['DNK'], [])

    def test_country_payload_keeps_source_year_unit_and_change(self):
        series = metrics.empty_series({'DNK'})
        series['gdp']['DNK'] = [{'value':400.0,'year':2024},{'value':390.0,'year':2023}]
        row = metrics.country_metrics_row({'id':'denmark','iso3':'DNK','name':'Denmark'}, series, '2026-09-15T00:00:00+00:00')
        gdp = row['metrics']['gdp']
        self.assertEqual(gdp['value'], 400.0)
        self.assertEqual(gdp['year'], 2024)
        self.assertEqual(gdp['unit'], 'current USD')
        self.assertEqual(gdp['source_id'], 'world-bank-wdi')
        self.assertEqual(gdp['previous']['year'], 2023)
        self.assertAlmostEqual(gdp['change_from_previous']['absolute'], 10.0)
        self.assertNotIn('inflation', row['metrics'])


if __name__ == '__main__':
    unittest.main()
