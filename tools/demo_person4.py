import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NORMAL_DIR = ROOT / "data" / "scenarios" / "normal"
SUSPICIOUS_DIR = ROOT / "data" / "scenarios" / "suspicious"

def load_scenarios(folder):
    scenarios = []

    for path in sorted(folder.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenarios.append(data)

    return scenarios


def get_value(data, *keys, default=""):
    for key in keys:
        if key in data:
            return data[key]
    return default


def show_summary(normal, suspicious):
    print("=" * 65)
    print("             LANDSHIELD - PERSON 4 DEMO")
    print("       PROPERTY ACTIVITY & INVESTIGATION")
    print("=" * 65)

    print("\nSCENARIO SUMMARY")
    print("-" * 65)

    print(f"Normal activities     : {len(normal)}")
    print(f"Suspicious activities : {len(suspicious)}")
    print(f"Total scenarios       : {len(normal) + len(suspicious)}")

    print("\n" + "-" * 65)
    print("NORMAL ACTIVITIES")
    print("-" * 65)

    for s in normal:
        scenario_id = get_value(s, "scenario_id", "id")
        property_id = get_value(s, "property_id")
        classification = get_value(
            s,
            "classification",
            "expected_classification",
            default="NORMAL"
        )

        print(f"{scenario_id:<6} | {property_id:<12} | {classification}")

    print("\n" + "-" * 65)
    print("SUSPICIOUS ACTIVITIES")
    print("-" * 65)

    for s in suspicious:
        scenario_id = get_value(s, "scenario_id", "id")
        property_id = get_value(s, "property_id")

        finding = get_value(
            s,
            "finding",
            "finding_type",
            "expected_finding",
            default=""
        )

        expected = s.get("expected_findings", [])
        if not finding and expected:
            if isinstance(expected, list):
                finding = ", ".join(expected)
            else:
                finding = str(expected)

        risk = get_value(
            s,
            "risk_level",
            "priority",
            default="HIGH"
        )

        print(f"{scenario_id:<6} | {property_id:<12} | {risk:<6} | {finding}")


def show_detail(scenario):
    print("\n" + "=" * 65)

    scenario_id = get_value(scenario, "scenario_id", "id")
    property_id = get_value(scenario, "property_id")

    print(f"SCENARIO : {scenario_id}")
    print(f"PROPERTY : {property_id}")
    print("=" * 65)

    classification = get_value(
        scenario,
        "classification",
        "expected_classification",
        default="UNKNOWN"
    )

    print("\nCLASSIFICATION")
    print("-" * 65)
    print(classification)

    risk = get_value(
        scenario,
        "risk_level",
        "priority",
        default=""
    )

    if risk:
        print(f"\nRISK LEVEL\n{'-' * 65}\n{risk}")

    findings = scenario.get("expected_findings", [])

    if findings:
        print("\nFINDINGS")
        print("-" * 65)

        if isinstance(findings, list):
            for finding in findings:
                print(f"- {finding}")
        else:
            print(findings)
    else:
        print("\nFINDINGS")
        print("-" * 65)
        print("No suspicious finding detected.")

    investigation_input = scenario.get("investigation_input")

    if investigation_input:
        print("\nINVESTIGATION INPUT")
        print("-" * 65)

        if isinstance(investigation_input, dict):
            for key, value in investigation_input.items():
                print(f"{key}: {value}")
        else:
            print(investigation_input)

    expected_result = scenario.get("expected_result")

    if expected_result:
        print("\nEXPECTED INVESTIGATION RESULT")
        print("-" * 65)

        if isinstance(expected_result, dict):
            for key, value in expected_result.items():
                print(f"{key}: {value}")
        else:
            print(expected_result)

    print("\nSTATUS")
    print("-" * 65)

    if findings:
        print("INVESTIGATION REQUIRED")
        print("Human/legal verification required.")
    else:
        print("NO INVESTIGATION ALERT")


def main():
    normal = load_scenarios(NORMAL_DIR)
    suspicious = load_scenarios(SUSPICIOUS_DIR)

    show_summary(normal, suspicious)

    all_scenarios = normal + suspicious

    while True:
        print("\n" + "=" * 65)
        print("Enter a scenario ID to inspect.")
        print("Examples: N001, S001, S004")
        print("Enter Q to quit.")
        print("=" * 65)

        choice = input("Scenario: ").strip().upper()

        if choice == "Q":
            break

        selected = None

        for scenario in all_scenarios:
            scenario_id = get_value(scenario, "scenario_id", "id")

            if scenario_id.upper() == choice:
                selected = scenario
                break

        if selected:
            show_detail(selected)
        else:
            print(f"\nScenario '{choice}' was not found.")


if __name__ == "__main__":
    main()