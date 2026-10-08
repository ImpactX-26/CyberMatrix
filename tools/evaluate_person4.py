"""Evaluate record-consistency checks for the LANDSHIELD synthetic dataset."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DIR = ROOT / "data" / "synthetic"
GROUND_TRUTH_PATH = ROOT / "data" / "ground_truth" / "ground_truth.json"
TOLERANCE_ACRES = 0.01


def load_records(data_dir=SYNTHETIC_DIR):
    data_dir = Path(data_dir)
    names = (
        "properties",
        "rtc_records",
        "registration_records",
        "mutation_records",
        "mortgage_records",
        "encumbrance_records",
    )

    loaded = {}
    for name in names:
        with (data_dir / f"{name}.json").open(encoding="utf-8") as source:
            loaded[name] = json.load(source)

    return loaded


def findings_for_property(property_id, records):
    properties = {
        record["property_id"]: record
        for record in records["properties"]
    }

    property_record = properties.get(property_id)
    if property_record is None:
        raise ValueError(f"Unknown property_id: {property_id}")

    rtc_records = [
        record
        for record in records["rtc_records"]
        if record["property_id"] == property_id
    ]

    if len(rtc_records) != 1:
        raise ValueError(
            f"Expected one RTC record for {property_id}; "
            f"found {len(rtc_records)}"
        )

    rtc = rtc_records[0]

    registrations = sorted(
        [
            record
            for record in records["registration_records"]
            if record["property_id"] == property_id
        ],
        key=lambda record: (
            record.get("registration_date", ""),
            record.get("registration_number", ""),
        ),
    )

    mutations = [
        record
        for record in records["mutation_records"]
        if record["property_id"] == property_id
    ]

    active_encumbrances = [
        record
        for record in records["encumbrance_records"]
        if record["property_id"] == property_id
        and str(record.get("status", "")).lower() == "active"
    ]

    findings = []

    # 1. Registration recipient differs from current RTC owner.
    if registrations:
        if registrations[-1]["buyer"] != rtc["owner"]:
            findings.append("ownership_mismatch")

    # 2. Later registration does not continue from the previous buyer.
    if any(
        previous["buyer"] != current["seller"]
        for previous, current in zip(registrations, registrations[1:])
    ):
        findings.append("ownership_chain_gap")

    # 3. Extent inconsistency.
    recorded_extents = [rtc["extent_acres"]]

    recorded_extents.extend(
        record["registered_extent_acres"]
        for record in registrations
    )

    for record in mutations:
        if "recorded_extent_acres" in record:
            recorded_extents.append(record["recorded_extent_acres"])
        elif "extent_acres" in record:
            recorded_extents.append(record["extent_acres"])

    if any(
        abs(extent - property_record["extent_acres"])
        > TOLERANCE_ACRES
        for extent in recorded_extents
    ):
        findings.append("extent_mismatch")

    # 4. Only ACTIVE encumbrances contribute to overlap.
    encumbered_extent = sum(
        record["extent_acres"]
        for record in active_encumbrances
    )

    if (
        encumbered_extent - property_record["extent_acres"]
        > TOLERANCE_ACRES
    ):
        findings.append("overlapping_encumbrances")

    return findings


def evaluate(root=ROOT):
    root = Path(root)
    records = load_records(root / "data" / "synthetic")

    with (root / "data" / "ground_truth" / "ground_truth.json").open(
        encoding="utf-8"
    ) as source:
        truth = json.load(source)

    results = []
    true_positive = 0
    false_positive = 0
    false_negative = 0
    exact_matches = 0

    for case in truth:
        expected = set(case["expected_findings"])
        detected = set(
            findings_for_property(case["property_id"], records)
        )

        true_positive += len(expected & detected)
        false_positive += len(detected - expected)
        false_negative += len(expected - detected)
        exact_matches += expected == detected

        results.append(
            {
                "scenario_id": case["scenario_id"],
                "property_id": case["property_id"],
                "expected_findings": sorted(expected),
                "detected_findings": sorted(detected),
                "match": expected == detected,
            }
        )

    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative

    return {
        "scenario_count": len(results),
        "exact_match_count": exact_matches,
        "accuracy": (
            exact_matches / len(results)
            if results
            else 1.0
        ),
        "precision": (
            true_positive / precision_denominator
            if precision_denominator
            else 1.0
        ),
        "recall": (
            true_positive / recall_denominator
            if recall_denominator
            else 1.0
        ),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "cases": results,
    }


if __name__ == "__main__":
    report = evaluate()
    print(json.dumps(report, indent=2))
