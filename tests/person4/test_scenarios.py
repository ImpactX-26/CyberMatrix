import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = ROOT / "data" / "scenarios"
GROUND_TRUTH_PATH = ROOT / "data" / "ground_truth" / "ground_truth.json"


class ScenarioTests(unittest.TestCase):
    def test_expected_number_of_scenarios(self):
        self.assertEqual(len(list((SCENARIOS_DIR / "normal").glob("*.json"))), 5)
        self.assertEqual(len(list((SCENARIOS_DIR / "suspicious").glob("*.json"))), 5)

    def test_scenarios_match_ground_truth(self):
        truth = {
            case["scenario_id"]: case
            for case in json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))
        }
        paths = list((SCENARIOS_DIR / "normal").glob("*.json"))
        paths.extend((SCENARIOS_DIR / "suspicious").glob("*.json"))
        self.assertEqual(len(paths), len(truth))
        for path in paths:
            case = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(scenario=case["scenario_id"]):
                self.assertIn(case["scenario_id"], truth)
                expected = truth[case["scenario_id"]]
                self.assertEqual(case["property_id"], expected["property_id"])
                self.assertEqual(
                    sorted(case["expected_findings"]),
                    sorted(expected["expected_findings"]),
                )

    def test_scenario_classification_matches_folder_and_findings(self):
        for folder, classification in (
            ("normal", "normal"),
            ("suspicious", "suspicious"),
        ):
            for path in (SCENARIOS_DIR / folder).glob("*.json"):
                case = json.loads(path.read_text(encoding="utf-8"))
                with self.subTest(scenario=case["scenario_id"]):
                    self.assertEqual(case["classification"], classification)
                    self.assertEqual(bool(case["expected_findings"]), classification == "suspicious")


if __name__ == "__main__":
    unittest.main()
