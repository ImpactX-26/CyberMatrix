
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = ROOT / "data" / "scenarios"
GROUND_TRUTH_PATH = ROOT / "data" / "ground_truth" / "ground_truth.json"


def load_scenario(scenario_id):
    folder = (
        "normal"
        if scenario_id.startswith("N")
        else "suspicious"
    )

    for path in (SCENARIOS_DIR / folder).glob("*.json"):
        scenario = json.loads(
            path.read_text(encoding="utf-8")
        )

        if scenario.get("scenario_id") == scenario_id:
            return scenario

    raise AssertionError(
        f"Scenario not found: {scenario_id}"
    )


class EvaluationTests(unittest.TestCase):

    def test_all_scenarios_match_ground_truth(self):
        truth = json.loads(
            GROUND_TRUTH_PATH.read_text(encoding="utf-8")
        )

        exact_matches = 0

        for case in truth:
            scenario = load_scenario(case["scenario_id"])

            expected = sorted(case["expected_findings"])
            actual = sorted(scenario["expected_findings"])

            with self.subTest(
                scenario_id=case["scenario_id"]
            ):
                self.assertEqual(
                    scenario["property_id"],
                    case["property_id"]
                )
                self.assertEqual(
                    actual,
                    expected
                )

                if actual == expected:
                    exact_matches += 1

        self.assertEqual(exact_matches, 10)

    def test_each_suspicious_fixture_exercises_its_named_finding(self):
        expected = {
            "S001": "ownership_mismatch",
            "S002": "overlapping_encumbrances",
            "S003": "ownership_chain_gap",
            "S004": "extent_mismatch",
            "S005": "ownership_mismatch",
        }

        for scenario_id, finding in expected.items():
            scenario = load_scenario(scenario_id)

            with self.subTest(
                scenario_id=scenario_id
            ):
                self.assertIn(
                    finding,
                    scenario["expected_findings"]
                )


if __name__ == "__main__":
    unittest.main()
