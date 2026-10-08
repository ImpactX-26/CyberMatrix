
import json
import csv
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from generate_events import build_event_stream


class EventTests(unittest.TestCase):

    def test_saved_events_match_generator_output(self):
        generated = build_event_stream()

        saved = json.loads(
            (
                ROOT
                / "data"
                / "synthetic"
                / "normalized_events.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(saved, generated)

    def test_csv_and_json_events_have_the_same_rows(self):
        events_path = ROOT / "data" / "synthetic" / "events.csv"

        with events_path.open(
            encoding="utf-8",
            newline=""
        ) as source:
            csv_events = list(csv.DictReader(source))

        json_events = json.loads(
            (
                ROOT
                / "data"
                / "synthetic"
                / "events.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(len(csv_events), len(json_events))

        # CSV contains additional optional columns.
        # Compare only fields represented by the JSON event objects.
        for csv_row, json_row in zip(csv_events, json_events):
            for key, value in json_row.items():
                self.assertEqual(
                    csv_row.get(key, ""),
                    str(value),
                    f"Mismatch in field {key}"
                )

    def test_events_are_chronological_and_have_unique_ids(self):
        events = build_event_stream()

        dates = [
            datetime.strptime(
                event["event_date"],
                "%Y-%m-%d"
            )
            for event in events
        ]

        self.assertEqual(dates, sorted(dates))

        event_ids = {
            event["event_id"]
            for event in events
        }

        self.assertEqual(
            len(event_ids),
            len(events)
        )

        self.assertTrue(
            all(event["event_id"] for event in events)
        )


if __name__ == "__main__":
    unittest.main()
