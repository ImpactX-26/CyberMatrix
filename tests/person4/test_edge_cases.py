import copy
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_person4 import findings_for_property, load_records


class EdgeCaseTests(unittest.TestCase):

    def test_extent_tolerance_avoids_rounding_noise(self):
        records = load_records()

        original = records["rtc_records"][0]["extent_acres"]

        records["rtc_records"][0]["extent_acres"] = original + 0.005

        findings = findings_for_property(
            records["rtc_records"][0]["property_id"],
            records
        )

        self.assertNotIn("extent_mismatch", findings)

    def test_missing_or_duplicate_rtc_is_an_explicit_error(self):
        records = load_records()

        property_id = records["rtc_records"][0]["property_id"]

        duplicate = copy.deepcopy(records["rtc_records"][0])
        records["rtc_records"].append(duplicate)

        with self.assertRaisesRegex(
            ValueError,
            "Expected one RTC record"
        ):
            findings_for_property(property_id, records)

    def test_released_encumbrances_do_not_contribute_to_overlap(self):
        records = load_records()

        property_id = records["rtc_records"][0]["property_id"]

        for record in records["encumbrance_records"]:
            if record["property_id"] == property_id:
                record["status"] = "RELEASED"

        findings = findings_for_property(
            property_id,
            records
        )

        self.assertNotIn(
            "overlapping_encumbrances",
            findings
        )

    def test_unknown_property_is_an_explicit_error(self):
        records = load_records()

        with self.assertRaisesRegex(
            ValueError,
            "Unknown property_id"
        ):
            findings_for_property(
                "PROP-DOES-NOT-EXIST",
                records
            )


if __name__ == "__main__":
    unittest.main()
