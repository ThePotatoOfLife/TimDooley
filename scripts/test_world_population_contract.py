import unittest
from world_population_contract import validate_population_runtime


class PopulationContractTests(unittest.TestCase):
    def test_complete_rows_pass_and_missing_row_fails(self):
        index = {"countries": [{"iso3": "AFG"}, {"iso3": "ALB"}]}
        population = {"value": 1, "unit": "persons", "period": 2023, "source": "fixture", "resolution_tier": "global-fallback"}
        runtime = {"population_coverage": 2, "countries": {"AFG": {"population": dict(population)}, "ALB": {"population": dict(population)}}}
        self.assertEqual(validate_population_runtime(index, runtime, expected=2), [])
        del runtime["countries"]["ALB"]
        runtime["population_coverage"] = 1
        self.assertTrue(validate_population_runtime(index, runtime, expected=2))


if __name__ == "__main__":
    unittest.main()
