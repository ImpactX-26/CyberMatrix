"""
LandShield investigation rules.

These are deterministic indicators, NOT fraud classifiers.

They answer:

"What looks inconsistent?"

They do NOT answer:

"Is this fraud?"

All conclusions require verification.
"""

from __future__ import annotations

from typing import Any


# ============================================================
# INDICATOR NAMES
# ============================================================

REGISTRATION_MUTATION_MISMATCH = (
    "REGISTRATION_MUTATION_MISMATCH"
)

EXTENT_OVERLAP = "EXTENT_OVERLAP"

OWNERSHIP_CHAIN_GAP = "OWNERSHIP_CHAIN_GAP"

EXTENT_INCONSISTENCY = "EXTENT_INCONSISTENCY"

SURVEY_HISSA_INCONSISTENCY = (
    "SURVEY_HISSA_INCONSISTENCY"
)

SUSPICIOUS_EVENT_SEQUENCE = (
    "SUSPICIOUS_EVENT_SEQUENCE"
)


# ============================================================
# HUMAN-READABLE FINDINGS
# ============================================================


FINDING_TEXT = {
    REGISTRATION_MUTATION_MISMATCH:
        "Registration and mutation indicate different receiving parties.",

    EXTENT_OVERLAP:
        "Potential extent overlap.",

    OWNERSHIP_CHAIN_GAP:
        "Unexplained ownership transition.",

    EXTENT_INCONSISTENCY:
        "Extent inconsistency requiring verification.",

    SURVEY_HISSA_INCONSISTENCY:
        "Property identifier inconsistency.",

    SUSPICIOUS_EVENT_SEQUENCE:
        "Suspicious sequence of property events requires investigation.",
}


REASON_TEXT = {
    REGISTRATION_MUTATION_MISMATCH:
        "The registration buyer and mutation owner do not match.",

    EXTENT_OVERLAP:
        "Related transactions account for more land than the available property extent.",

    OWNERSHIP_CHAIN_GAP:
        "The ownership sequence contains a transition that is not explained by an available record.",

    EXTENT_INCONSISTENCY:
        "The recorded transaction extent differs from the property extent.",

    SURVEY_HISSA_INCONSISTENCY:
        "Survey or hissa identifiers differ across related records.",

    SUSPICIOUS_EVENT_SEQUENCE:
        "Multiple related property events occur in a sequence that requires additional verification.",
}


# ============================================================
# PRIORITY WEIGHTS
# ============================================================


PRIORITY_WEIGHTS = {
    REGISTRATION_MUTATION_MISMATCH: 3,
    EXTENT_OVERLAP: 3,
    OWNERSHIP_CHAIN_GAP: 3,
    EXTENT_INCONSISTENCY: 2,
    SURVEY_HISSA_INCONSISTENCY: 2,
    SUSPICIOUS_EVENT_SEQUENCE: 3,
}


# ============================================================
# INDICATOR 1
# ============================================================


def detect_registration_mutation_mismatch(
    registrations: list[dict[str, Any]],
    mutations: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Detect when registration buyer and mutation new owner differ.
    """

    if not registrations or not mutations:
        return None

    registration = registrations[-1]
    mutation = mutations[-1]

    buyer = registration.get("buyer")
    new_owner = mutation.get("new_owner")

    if not buyer or not new_owner:
        return None

    if str(buyer).strip().lower() == str(
        new_owner
    ).strip().lower():
        return None

    return {
        "type": REGISTRATION_MUTATION_MISMATCH,
        "finding": FINDING_TEXT[
            REGISTRATION_MUTATION_MISMATCH
        ],
        "reason": REASON_TEXT[
            REGISTRATION_MUTATION_MISMATCH
        ],
        "severity": "HIGH",
        "details": {
            "registration_buyer": buyer,
            "mutation_new_owner": new_owner,
        },
        "required_evidence": [
            "Underlying sale deed",
            "Mutation order",
        ],
    }


# ============================================================
# INDICATOR 2
# ============================================================


def detect_extent_overlap(
    property_extent: float | None,
    transactions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Detect potential overlap when related transaction extents
    exceed the property extent.

    This is a warning indicator only.
    """

    if property_extent is None:
        return None

    if len(transactions) < 2:
        return None

    total_extent = 0.0

    for transaction in transactions:
        extent = transaction.get("extent_acres")

        if extent is None:
            continue

        try:
            total_extent += float(extent)
        except (TypeError, ValueError):
            continue

    if total_extent <= float(property_extent):
        return None

    return {
        "type": EXTENT_OVERLAP,
        "finding": FINDING_TEXT[EXTENT_OVERLAP],
        "reason": (
            f"Related transactions account for "
            f"{total_extent:g} acres against a "
            f"{float(property_extent):g} acre property."
        ),
        "severity": "HIGH",
        "details": {
            "property_extent_acres": property_extent,
            "transaction_extent_acres": total_extent,
        },
        "required_evidence": [
            "Underlying transaction deeds",
            "Property extent record",
        ],
    }


# ============================================================
# INDICATOR 3
# ============================================================


def detect_ownership_chain_gap(
    transactions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Detect an ownership transition that cannot be connected
    through the available transaction records.
    """

    if len(transactions) < 2:
        return None

    ordered = sorted(
        transactions,
        key=lambda item: item.get("date", ""),
    )

    for previous, current in zip(
        ordered,
        ordered[1:],
    ):
        previous_buyer = previous.get("buyer")
        current_seller = current.get("seller")

        if not previous_buyer or not current_seller:
            continue

        if (
            str(previous_buyer).strip().lower()
            != str(current_seller).strip().lower()
        ):
            return {
                "type": OWNERSHIP_CHAIN_GAP,
                "finding": FINDING_TEXT[
                    OWNERSHIP_CHAIN_GAP
                ],
                "reason": (
                    "The later transaction seller does not "
                    "match the preceding transaction buyer."
                ),
                "severity": "HIGH",
                "details": {
                    "previous_buyer": previous_buyer,
                    "current_seller": current_seller,
                },
                "required_evidence": [
                    "Missing ownership transfer record",
                    "Underlying transaction documents",
                ],
            }

    return None


# ============================================================
# INDICATOR 4
# ============================================================


def detect_extent_inconsistency(
    property_extent: float | None,
    registrations: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Detect a registration extent different from the property extent.
    """

    if property_extent is None:
        return None

    if not registrations:
        return None

    registration = registrations[-1]

    registration_extent = registration.get(
        "extent_acres"
    )

    if registration_extent is None:
        return None

    try:
        property_extent = float(property_extent)
        registration_extent = float(
            registration_extent
        )
    except (TypeError, ValueError):
        return None

    if property_extent == registration_extent:
        return None

    return {
        "type": EXTENT_INCONSISTENCY,
        "finding": FINDING_TEXT[
            EXTENT_INCONSISTENCY
        ],
        "reason": (
            "The registration extent differs from "
            "the property record."
        ),
        "severity": "HIGH",
        "details": {
            "property_extent_acres": property_extent,
            "registration_extent_acres": registration_extent,
        },
        "required_evidence": [
            "Underlying registration deed",
            "Current property record",
        ],
    }


# ============================================================
# INDICATOR 5
# ============================================================


def detect_survey_hissa_inconsistency(
    property_snapshot: dict[str, Any],
    registrations: list[dict[str, Any]],
    mutations: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Detect inconsistent survey/hissa identifiers.
    """

    identifiers: list[tuple[str, str, str]] = []

    snapshot_survey = property_snapshot.get(
        "survey_number"
    )
    snapshot_hissa = property_snapshot.get(
        "hissa"
    )

    if snapshot_survey:
        identifiers.append(
            (
                "PROPERTY",
                str(snapshot_survey),
                str(snapshot_hissa or ""),
            )
        )

    for record in registrations:
        survey = record.get("survey_number")

        if survey:
            identifiers.append(
                (
                    "REGISTRATION",
                    str(survey),
                    str(record.get("hissa") or ""),
                )
            )

    for record in mutations:
        survey = record.get("survey_number")

        if survey:
            identifiers.append(
                (
                    "MUTATION",
                    str(survey),
                    str(record.get("hissa") or ""),
                )
            )

    if len(identifiers) < 2:
        return None

    unique_identifiers = {
        (survey, hissa)
        for _, survey, hissa in identifiers
    }

    if len(unique_identifiers) <= 1:
        return None

    return {
        "type": SURVEY_HISSA_INCONSISTENCY,
        "finding": FINDING_TEXT[
            SURVEY_HISSA_INCONSISTENCY
        ],
        "reason": (
            "Survey or hissa identifiers differ "
            "across related records."
        ),
        "severity": "MEDIUM",
        "details": {
            "identifiers": [
                {
                    "source": source,
                    "survey_number": survey,
                    "hissa": hissa,
                }
                for source, survey, hissa in identifiers
            ]
        },
        "required_evidence": [
            "Current property record",
            "Registration record",
            "Mutation record",
        ],
    }


# ============================================================
# INDICATOR 6
# ============================================================


def detect_suspicious_event_sequence(
    events: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Detect:

    Mortgage
       ↓
    Registration
       ↓
    Mutation
       ↓
    Mortgage release

    This is an investigation indicator, not a fraud conclusion.
    """

    event_types = [
        str(event.get("event_type", ""))
        for event in events
    ]

    required_sequence = [
        "MORTGAGE_REGISTERED",
        "SALE_REGISTERED",
        "MUTATION_UPDATED",
        "MORTGAGE_RELEASED",
    ]

    position = 0

    for event_type in event_types:
        if (
            position < len(required_sequence)
            and event_type
            == required_sequence[position]
        ):
            position += 1

    if position != len(required_sequence):
        return None

    return {
        "type": SUSPICIOUS_EVENT_SEQUENCE,
        "finding": FINDING_TEXT[
            SUSPICIOUS_EVENT_SEQUENCE
        ],
        "reason": REASON_TEXT[
            SUSPICIOUS_EVENT_SEQUENCE
        ],
        "severity": "HIGH",
        "details": {
            "sequence": required_sequence,
        },
        "required_evidence": [
            "Mortgage record",
            "Underlying sale deed",
            "Mutation order",
            "Mortgage release record",
        ],
    }


# ============================================================
# PRIORITY
# ============================================================


def calculate_priority(
    indicators: list[dict[str, Any]],
) -> str:
    """
    Calculate explainable investigation priority.

    LOW:
        No material indicator or very limited concern.

    MEDIUM:
        One moderate indicator.

    HIGH:
        Strong indicator or multiple indicators.
    """

    score = 0

    for indicator in indicators:
        indicator_type = indicator.get("type")

        score += PRIORITY_WEIGHTS.get(
            indicator_type,
            0,
        )

    if score >= 5:
        return "HIGH"

    if score >= 2:
        return "MEDIUM"

    return "LOW"


# ============================================================
# INVESTIGATION DECISION
# ============================================================


def determine_investigation_required(
    indicators: list[dict[str, Any]],
) -> bool:
    """
    Any material indicator requires investigation.
    """

    return bool(indicators)


# ============================================================
# MAIN RULE EVALUATOR
# ============================================================


def evaluate_indicators(
    property_snapshot: dict[str, Any],
    events: list[dict[str, Any]],
    registrations: list[dict[str, Any]],
    mutations: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Run all LandShield investigation indicators.
    """

    indicators: list[dict[str, Any]] = []

    property_extent = property_snapshot.get(
        "extent_acres"
    )

    result = detect_registration_mutation_mismatch(
        registrations,
        mutations,
    )

    if result:
        indicators.append(result)

    result = detect_extent_overlap(
        property_extent,
        transactions,
    )

    if result:
        indicators.append(result)

    result = detect_ownership_chain_gap(
        transactions,
    )

    if result:
        indicators.append(result)

    result = detect_extent_inconsistency(
        property_extent,
        registrations,
    )

    if result:
        indicators.append(result)

    result = detect_survey_hissa_inconsistency(
        property_snapshot,
        registrations,
        mutations,
    )

    if result:
        indicators.append(result)

    result = detect_suspicious_event_sequence(
        events,
    )

    if result:
        indicators.append(result)

    priority = calculate_priority(
        indicators
    )

    return {
        "investigation_required":
            determine_investigation_required(
                indicators
            ),
        "priority": priority,
        "indicators": indicators,
    }