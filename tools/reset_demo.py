"""Regenerate CSV exports and the event stream from canonical JSON fixtures."""

import csv
import json
from pathlib import Path

from generate_events import SYNTHETIC_DIR, write_events


DATASETS = (
    "properties",
    "rtc_records",
    "registration_records",
    "mutation_records",
    "mortgage_records",
    "encumbrance_records",
)


def export_csv(name, data_dir=SYNTHETIC_DIR):
    data_dir = Path(data_dir)
    with (data_dir / f"{name}.json").open(encoding="utf-8") as source:
        records = json.load(source)
    if not records:
        raise ValueError(f"Cannot export empty record set: {name}")

    fields = list(records[0])
    if any(list(record) != fields for record in records):
        raise ValueError(f"Inconsistent fields in {name}.json")

    with (data_dir / f"{name}.csv").open(
        "w", encoding="utf-8", newline=""
    ) as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    return len(records)


def reset_demo(data_dir=SYNTHETIC_DIR):
    counts = {name: export_csv(name, data_dir) for name in DATASETS}
    counts["events"] = len(write_events(data_dir))
    return counts


if __name__ == "__main__":
    for dataset, count in reset_demo().items():
        print(f"{dataset}: {count} records")
