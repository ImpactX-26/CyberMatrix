
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "synthetic"


def parse_date(value):
    if not value:
        return datetime.max

    value = str(value)

    for fmt in (
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    return datetime.max


def load_json(filename):
    path = DATA_DIR / filename

    if not path.exists():
        return []

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_event_stream():
    events = load_json("events.json")
    normalized = []

    for event in events:
        item = {
            "event_id": event.get("event_id"),
            "property_id": event.get("property_id"),
            "event_type": event.get("event_type"),
            "event_date": event.get("event_date"),
            "source": event.get("source"),
        }

        for key, value in event.items():
            if key not in item:
                item[key] = value

        normalized.append(item)

    # Global chronological event stream.
    normalized.sort(
        key=lambda x: (
            parse_date(x.get("event_date")),
            str(x.get("property_id", "")),
            str(x.get("event_id", "")),
        )
    )

    return normalized


def save_events(events):
    output_path = DATA_DIR / "normalized_events.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    return output_path


def main():
    events = build_event_stream()
    output = save_events(events)

    print("LANDSHIELD Event Generator")
    print("--------------------------")
    print(f"Input events : {len(events)}")
    print(f"Output file  : {output}")
    print()

    if events:
        print("First 5 events:")

        for event in events[:5]:
            print(
                event["event_id"],
                "|",
                event["property_id"],
                "|",
                event["event_type"],
                "|",
                event["event_date"],
            )

    print()
    print("Event generation completed.")


if __name__ == "__main__":
    main()
