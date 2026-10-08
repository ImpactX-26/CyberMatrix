"""
LANDSHIELD Investigation Demo Runner.

Usage:

    python tools/run_investigation.py PROP-0491

This provides a clean command-line demo for the hackathon.
"""

from __future__ import annotations

import json
import sys

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.orchestrator import run_investigation


def print_header() -> None:
    print()
    print("=" * 70)
    print("                 LANDSHIELD")
    print("       AI Property Change Intelligence")
    print("=" * 70)
    print()


def print_result(result: dict) -> None:

    print(f"Property ID          : {result['property_id']}")
    print(
        f"Investigation needed : "
        f"{result['investigation_required']}"
    )
    print(f"Priority             : {result['priority']}")
    print(
        f"Human review         : "
        f"{result['human_review_required']}"
    )

    print()
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)
    print(result["summary"])

    print()
    print("-" * 70)
    print("FINDINGS")
    print("-" * 70)

    findings = result.get("findings", [])

    if not findings:
        print("No significant findings.")

    for index, finding in enumerate(
        findings,
        start=1,
    ):
        print(
            f"{index}. {finding.get('type')}"
        )

        print(
            f"   Finding : "
            f"{finding.get('finding')}"
        )

        print(
            f"   Reason  : "
            f"{finding.get('reason')}"
        )

        details = finding.get(
            "details",
            {},
        )

        if details:
            print(
                f"   Details : "
                f"{json.dumps(details)}"
            )

    print()
    print("-" * 70)
    print("EVIDENCE")
    print("-" * 70)

    evidence = result.get(
        "evidence",
        [],
    )

    if not evidence:
        print("No evidence retrieved.")

    for index, item in enumerate(
        evidence,
        start=1,
    ):
        print(
            f"{index}. "
            f"{item.get('source_record')} "
            f"({item.get('source_type')})"
        )

        print(
            f"   Field : "
            f"{item.get('field')}"
        )

        print(
            f"   Value : "
            f"{item.get('value')}"
        )

        print(
            f"   Date  : "
            f"{item.get('date')}"
        )

    print()
    print("-" * 70)
    print("MISSING EVIDENCE")
    print("-" * 70)

    missing = result.get(
        "missing_evidence",
        [],
    )

    if not missing:
        print("None.")

    for item in missing:
        print(f"- {item}")

    print()
    print("-" * 70)
    print("NEXT VERIFICATION")
    print("-" * 70)

    verification = result.get(
        "next_verification",
        [],
    )

    if not verification:
        print("None.")

    for item in verification:
        print(f"- {item}")

    print()
    print("-" * 70)
    print("INVESTIGATION TRACE")
    print("-" * 70)

    trace = result.get(
        "trace",
        [],
    )

    for item in trace:
        print(
            f"{item['step']}. "
            f"{item['agent']} → "
            f"{item['action']}"
        )

        print(
            f"   Status      : "
            f"{item['status']}"
        )

        print(
            f"   Next action : "
            f"{item['next_action']}"
        )

    print()
    print("=" * 70)
    print("Investigation complete.")
    print("=" * 70)
    print()


def main() -> int:

    if len(sys.argv) != 2:

        print(
            "Usage: "
            "python tools/run_investigation.py "
            "<property_id>"
        )

        print()
        print(
            "Example: "
            "python tools/run_investigation.py PROP-0491"
        )

        return 1

    property_id = sys.argv[1].strip()

    if not property_id:

        print(
            "Error: property_id cannot be empty."
        )

        return 1

    print_header()

    try:

        result = run_investigation(
            property_id
        )

        print_result(result)

        return 0

    except Exception as exc:

        print()
        print("=" * 70)
        print("INVESTIGATION ERROR")
        print("=" * 70)
        print(str(exc))
        print("=" * 70)
        print()

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )