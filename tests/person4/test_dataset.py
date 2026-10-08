import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "synthetic"

JSON_DATASETS = (
    "properties",
    "rtc_records",
    "registration_records",
    "mutation_records",
    "mortgage_records",
    "encumbrance_records",
)


class DatasetTests(unittest.TestCase):
    def test_json_and_csv_exports_match(self):
        for name in JSON_DATASETS:
            with self.subTest(dataset=name):
                with (DATA_DIR / f"{name}.json").open(
                    encoding="utf-8"
                ) as source:
                    json_rows = json.load(source)

                with (DATA_DIR / f"{name}.csv").open(
                    encoding="utf-8", newline=""
                ) as source:
                    csv_rows = list(csv.DictReader(source))

                self.assertEqual(len(json_rows), len(csv_rows))
                self.assertEqual(list(json_rows[0]), list(csv_rows[0]))

                for json_row, csv_row in zip(json_rows, csv_rows):
                    self.assertEqual(
                        {key: str(value) for key, value in json_row.items()},
                        csv_row,
                    )

    def test_records_reference_known_properties(self):
        properties = json.loads(
            (DATA_DIR / "properties.json").read_text(encoding="utf-8")
        )
        property_ids = {
            record["property_id"]
            for record in properties
        }

        for name in JSON_DATASETS[1:]:
            records = json.loads(
                (DATA_DIR / f"{name}.json").read_text(encoding="utf-8")
            )

            self.assertTrue(records, name)
            self.assertTrue(
                all(
                    record["property_id"] in property_ids
                    for record in records
                ),
                name,
            )

    def test_dataset_has_expected_scale(self):
        properties = json.loads(
            (DATA_DIR / "properties.json").read_text(encoding="utf-8")
        )

        events = json.loads(
            (DATA_DIR / "events.json").read_text(encoding="utf-8")
        )

        self.assertEqual(len(properties), 279)
        self.assertEqual(len(events), 1030)

        property_ids = {
            record["property_id"]
            for record in properties
        }

        self.assertEqual(len(property_ids), 279)


if __name__ == "__main__":
    unittest.main()