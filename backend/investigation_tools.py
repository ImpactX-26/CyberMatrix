"""
LandShield investigation tools.

These tools provide structured property/event information to the
Orchestrator, Investigation Agent, and Evidence Agent.

IMPORTANT:
- Demo data is synthetic only.
- Tools never invent evidence.
- Later, these functions can be replaced with calls to Person 1's API.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


# ============================================================
# SYNTHETIC DEMO DATABASE
# ============================================================

DEMO_PROPERTIES: dict[str, dict[str, Any]] = {
    "PROP-0491": {
        "property_id": "PROP-0491",
        "district": "Demo District",
        "taluk": "Demo Taluk",
        "hobli": "Demo Hobli",
        "village": "Demo Village",
        "survey_number": "49/1",
        "hissa": "1",
        "owner": "Owner A",
        "extent_acres": 5.0,
        "status": "ACTIVE",
    },
}


DEMO_EVENTS: dict[str, list[dict[str, Any]]] = {
    "PROP-0491": [
        {
            "event_id": "EV-0491-001",
            "property_id": "PROP-0491",
            "event_type": "MORTGAGE_REGISTERED",
            "date": "2026-01-30",
            "details": {
                "mortgagee": "Bank A",
                "amount": 500000,
                "status": "ACTIVE",
            },
        },
        {
            "event_id": "EV-0491-002",
            "property_id": "PROP-0491",
            "event_type": "SALE_REGISTERED",
            "date": "2026-02-14",
            "details": {
                "seller": "Person B",
                "buyer": "Person C",
                "extent_acres": 5.0,
                "document_id": "REG-0491-002",
            },
        },
        {
            "event_id": "EV-0491-003",
            "property_id": "PROP-0491",
            "event_type": "MUTATION_UPDATED",
            "date": "2026-02-16",
            "details": {
                "previous_owner": "Person B",
                "new_owner": "Person D",
                "document_id": "MUT-0491-003",
            },
        },
        {
            "event_id": "EV-0491-004",
            "property_id": "PROP-0491",
            "event_type": "MORTGAGE_RELEASED",
            "date": "2026-02-17",
            "details": {
                "mortgagee": "Bank A",
                "status": "RELEASED",
                "document_id": "REL-0491-004",
            },
        },
    ],
}


DEMO_REGISTRATIONS: dict[str, list[dict[str, Any]]] = {
    "PROP-0491": [
        {
            "record_id": "REG-0491-002",
            "property_id": "PROP-0491",
            "source_type": "REGISTRATION",
            "date": "2026-02-14",
            "survey_number": "49/1",
            "hissa": "1",
            "seller": "Person B",
            "buyer": "Person C",
            "extent_acres": 5.0,
            "status": "REGISTERED",
        }
    ]
}


DEMO_MUTATIONS: dict[str, list[dict[str, Any]]] = {
    "PROP-0491": [
        {
            "record_id": "MUT-0491-003",
            "property_id": "PROP-0491",
            "source_type": "MUTATION",
            "date": "2026-02-16",
            "survey_number": "49/1",
            "hissa": "1",
            "previous_owner": "Person B",
            "new_owner": "Person D",
            "status": "UPDATED",
        }
    ]
}


DEMO_TRANSACTIONS: dict[str, list[dict[str, Any]]] = {
    "PROP-0491": [
        {
            "transaction_id": "TXN-0491-001",
            "property_id": "PROP-0491",
            "transaction_type": "SALE",
            "date": "2026-02-14",
            "seller": "Person B",
            "buyer": "Person C",
            "extent_acres": 5.0,
            "source_record": "REG-0491-002",
        }
    ]
}


# ============================================================
# INTERNAL HELPERS
# ============================================================


def _copy(value: Any) -> Any:
    """
    Prevent callers from modifying the demo database directly.
    """
    return deepcopy(value)


def _property_exists(property_id: str) -> bool:
    return property_id in DEMO_PROPERTIES


# ============================================================
# TOOL 1
# ============================================================


def get_property_snapshot(property_id: str) -> dict[str, Any]:
    """
    Retrieve the current property state.
    """

    if not _property_exists(property_id):
        return {
            "success": False,
            "property_id": property_id,
            "error": "PROPERTY_NOT_FOUND",
            "message": "No property record is available.",
        }

    return {
        "success": True,
        "property": _copy(DEMO_PROPERTIES[property_id]),
    }


# ============================================================
# TOOL 2
# ============================================================


def get_recent_events(
    property_id: str,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Retrieve chronological property events.
    """

    if not _property_exists(property_id):
        return {
            "success": False,
            "property_id": property_id,
            "events": [],
            "error": "PROPERTY_NOT_FOUND",
        }

    events = _copy(DEMO_EVENTS.get(property_id, []))

    events.sort(key=lambda event: event.get("date", ""))

    return {
        "success": True,
        "property_id": property_id,
        "events": events[-limit:],
    }


# ============================================================
# TOOL 3
# ============================================================


def get_registration_history(
    property_id: str,
) -> dict[str, Any]:
    """
    Retrieve registration records.
    """

    if not _property_exists(property_id):
        return {
            "success": False,
            "property_id": property_id,
            "records": [],
            "error": "PROPERTY_NOT_FOUND",
        }

    return {
        "success": True,
        "property_id": property_id,
        "records": _copy(
            DEMO_REGISTRATIONS.get(property_id, [])
        ),
    }


# ============================================================
# TOOL 4
# ============================================================


def get_mutation_history(
    property_id: str,
) -> dict[str, Any]:
    """
    Retrieve mutation records.
    """

    if not _property_exists(property_id):
        return {
            "success": False,
            "property_id": property_id,
            "records": [],
            "error": "PROPERTY_NOT_FOUND",
        }

    return {
        "success": True,
        "property_id": property_id,
        "records": _copy(
            DEMO_MUTATIONS.get(property_id, [])
        ),
    }


# ============================================================
# TOOL 5
# ============================================================


def get_related_transactions(
    property_id: str,
) -> dict[str, Any]:
    """
    Retrieve transactions related to the property.
    """

    if not _property_exists(property_id):
        return {
            "success": False,
            "property_id": property_id,
            "transactions": [],
            "error": "PROPERTY_NOT_FOUND",
        }

    return {
        "success": True,
        "property_id": property_id,
        "transactions": _copy(
            DEMO_TRANSACTIONS.get(property_id, [])
        ),
    }


# ============================================================
# TOOL 6
# ============================================================


def find_evidence(
    property_id: str,
    record_ids: list[str] | None = None,
    source_types: list[str] | None = None,
) -> dict[str, Any]:
    """
    Find evidence records for an investigation.

    Evidence is returned only when it actually exists in the
    available synthetic database.
    """

    if not _property_exists(property_id):
        return {
            "success": False,
            "property_id": property_id,
            "evidence": [],
            "error": "PROPERTY_NOT_FOUND",
        }

    record_ids = set(record_ids or [])
    source_types_normalized = {
        value.upper()
        for value in (source_types or [])
    }

    evidence: list[dict[str, Any]] = []

    records = []

    records.extend(
        DEMO_REGISTRATIONS.get(property_id, [])
    )

    records.extend(
        DEMO_MUTATIONS.get(property_id, [])
    )

    records.extend(
        DEMO_TRANSACTIONS.get(property_id, [])
    )

    for record in records:
        record_id = record.get("record_id")

        source_type = str(
            record.get("source_type", "")
        ).upper()

        if record_ids and record_id not in record_ids:
            continue

        if (
            source_types_normalized
            and source_type not in source_types_normalized
        ):
            continue

        evidence.append(
            {
                "source_record": record_id,
                "source_type": source_type,
                "record": _copy(record),
            }
        )

    return {
        "success": True,
        "property_id": property_id,
        "evidence": evidence,
    }


# ============================================================
# TOOL 7
# ============================================================


def compare_property_states(
    property_id: str,
) -> dict[str, Any]:
    """
    Compare current property state against recent registration
    and mutation information.

    This is deterministic and does not make legal conclusions.
    """

    snapshot_result = get_property_snapshot(property_id)

    if not snapshot_result.get("success"):
        return snapshot_result

    registration_result = get_registration_history(
        property_id
    )

    mutation_result = get_mutation_history(
        property_id
    )

    snapshot = snapshot_result["property"]

    registrations = registration_result.get(
        "records",
        [],
    )

    mutations = mutation_result.get(
        "records",
        [],
    )

    differences: list[dict[str, Any]] = []

    if registrations:
        latest_registration = registrations[-1]

        registered_extent = latest_registration.get(
            "extent_acres"
        )

        current_extent = snapshot.get(
            "extent_acres"
        )

        if (
            registered_extent is not None
            and current_extent is not None
            and registered_extent != current_extent
        ):
            differences.append(
                {
                    "type": "EXTENT_INCONSISTENCY",
                    "current_value": current_extent,
                    "registration_value": registered_extent,
                }
            )

        registered_survey = latest_registration.get(
            "survey_number"
        )

        if (
            registered_survey
            and snapshot.get("survey_number")
            and registered_survey
            != snapshot.get("survey_number")
        ):
            differences.append(
                {
                    "type": "SURVEY_INCONSISTENCY",
                    "current_value": snapshot.get(
                        "survey_number"
                    ),
                    "registration_value": registered_survey,
                }
            )

    if mutations:
        latest_mutation = mutations[-1]

        new_owner = latest_mutation.get(
            "new_owner"
        )

        current_owner = snapshot.get(
            "owner"
        )

        if (
            new_owner
            and current_owner
            and new_owner != current_owner
        ):
            differences.append(
                {
                    "type": "OWNER_STATE_DIFFERENCE",
                    "current_value": current_owner,
                    "mutation_value": new_owner,
                }
            )

    return {
        "success": True,
        "property_id": property_id,
        "differences": differences,
    }


# ============================================================
# TOOL REGISTRY
# ============================================================


TOOL_REGISTRY = {
    "get_property_snapshot": get_property_snapshot,
    "get_recent_events": get_recent_events,
    "get_registration_history": get_registration_history,
    "get_mutation_history": get_mutation_history,
    "get_related_transactions": get_related_transactions,
    "find_evidence": find_evidence,
    "compare_property_states": compare_property_states,
}


def get_tool(name: str):
    """
    Return a registered tool by name.
    """
    return TOOL_REGISTRY.get(name)