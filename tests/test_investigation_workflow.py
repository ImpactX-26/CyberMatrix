"""
LANDSHIELD Person 2 Investigation Workflow Tests.

Tests the 3-agent investigation architecture:

1. Orchestrator Agent
2. Change Investigation Agent
3. Evidence Agent

These tests use the synthetic demo property and do not require
an LLM or external API.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.evidence_agent import EvidenceAgent
from backend.investigation_agent import InvestigationAgent
from backend.investigation_tools import (
    get_property_snapshot,
    get_recent_events,
    get_registration_history,
    get_mutation_history,
    get_related_transactions,
)
from backend.orchestrator import (
    MAX_INVESTIGATION_STEPS,
    OrchestratorAgent,
    run_investigation,
)


# ================================================================
# 1. PERFECT DEMO PROPERTY
# ================================================================


def test_demo_property_requires_high_priority_investigation():
    """
    PROP-0491 is the perfect suspicious demo case.
    """

    result = run_investigation("PROP-0491")

    assert result["property_id"] == "PROP-0491"

    assert result["investigation_required"] is True

    assert result["priority"] == "HIGH"

    finding_types = [
        finding["type"]
        for finding in result["findings"]
    ]

    assert (
        "REGISTRATION_MUTATION_MISMATCH"
        in finding_types
    )

    assert (
        "SUSPICIOUS_EVENT_SEQUENCE"
        in finding_types
    )


# ================================================================
# 2. DEMO EVIDENCE
# ================================================================


def test_demo_property_returns_registration_and_mutation_evidence():
    """
    The Evidence Agent should retrieve the actual registration
    and mutation source records.
    """

    result = run_investigation("PROP-0491")

    source_records = {
        item["source_record"]
        for item in result["evidence"]
    }

    assert "REG-0491-002" in source_records

    assert "MUT-0491-003" in source_records


# ================================================================
# 3. MISSING EVIDENCE
# ================================================================


def test_demo_property_identifies_missing_evidence():
    """
    Required source documents should be explicitly identified.
    """

    result = run_investigation("PROP-0491")

    missing = result["missing_evidence"]

    assert "Underlying sale deed" in missing

    assert "Mutation order" in missing

    assert "Mortgage record" in missing

    assert "Mortgage release record" in missing


# ================================================================
# 4. NEXT VERIFICATION
# ================================================================


def test_demo_property_has_next_verification_actions():
    """
    The final result should tell the reviewer what to verify next.
    """

    result = run_investigation("PROP-0491")

    verification = result["next_verification"]

    assert (
        "Review underlying sale deed"
        in verification
    )

    assert (
        "Review mutation order"
        in verification
    )

    assert (
        "Review mortgage record"
        in verification
    )

    assert (
        "Review mortgage release record"
        in verification
    )


# ================================================================
# 5. HUMAN REVIEW
# ================================================================


def test_suspicious_case_requires_human_review():
    """
    LandShield should route suspicious cases to human review.
    """

    result = run_investigation("PROP-0491")

    assert result["human_review_required"] is True


# ================================================================
# 6. TRACE
# ================================================================


def test_investigation_trace_is_present():
    """
    Every investigation should produce a trace.
    """

    result = run_investigation("PROP-0491")

    trace = result["trace"]

    assert len(trace) > 0

    assert len(trace) <= MAX_INVESTIGATION_STEPS


def test_trace_contains_all_three_agents():
    """
    The trace should demonstrate the requested 3-agent architecture.
    """

    result = run_investigation("PROP-0491")

    agents = {
        item["agent"]
        for item in result["trace"]
    }

    assert "Orchestrator Agent" in agents

    assert "Change Investigation Agent" in agents

    assert "Evidence Agent" in agents


# ================================================================
# 7. TRACE STEP ORDER
# ================================================================


def test_trace_steps_are_sequential():
    """
    Trace step numbers should be sequential.
    """

    result = run_investigation("PROP-0491")

    steps = [
        item["step"]
        for item in result["trace"]
    ]

    assert steps == list(
        range(
            1,
            len(steps) + 1,
        )
    )


# ================================================================
# 8. SAFE LANGUAGE
# ================================================================


def test_result_does_not_claim_fraud():
    """
    LandShield must not declare fraud as confirmed.
    """

    result = run_investigation("PROP-0491")

    result_text = str(
        result
    ).lower()

    assert "fraud confirmed" not in result_text

    assert "fraud is confirmed" not in result_text


def test_result_does_not_claim_document_authenticity():
    """
    LandShield must not declare a document genuine or fake.
    """

    result = run_investigation("PROP-0491")

    result_text = str(
        result
    ).lower()

    assert "document is genuine" not in result_text

    assert "document is fake" not in result_text


# ================================================================
# 9. EVIDENCE AGENT DIRECT TEST
# ================================================================


def test_evidence_agent_registration_mismatch():
    """
    Evidence Agent should independently handle the mismatch finding.
    """

    agent = EvidenceAgent()

    result = agent.investigate_finding(
        "PROP-0491",
        {
            "type": "REGISTRATION_MUTATION_MISMATCH",
            "required_evidence": [
                "Underlying sale deed",
                "Mutation order",
            ],
        },
    )

    assert result["success"] is True

    assert (
        result["finding_type"]
        == "REGISTRATION_MUTATION_MISMATCH"
    )

    records = {
        item["source_record"]
        for item in result["evidence"]
    }

    assert "REG-0491-002" in records

    assert "MUT-0491-003" in records


# ================================================================
# 10. INVESTIGATION AGENT DIRECT TEST
# ================================================================


def test_investigation_agent_identifies_demo_indicators():
    """
    Investigation Agent should identify the expected indicators
    independently of the Orchestrator.
    """

    agent = InvestigationAgent()

    property_snapshot = (
        get_property_snapshot(
            "PROP-0491"
        )["property"]
    )

    recent_events = (
        get_recent_events(
            "PROP-0491"
        )["events"]
    )

    registrations = (
        get_registration_history(
            "PROP-0491"
        )["records"]
    )

    mutations = (
        get_mutation_history(
            "PROP-0491"
        )["records"]
    )

    transactions = (
        get_related_transactions(
            "PROP-0491"
        )["transactions"]
    )

    result = agent.analyze(
        property_id="PROP-0491",
        property_snapshot=property_snapshot,
        recent_events=recent_events,
        registrations=registrations,
        mutations=mutations,
        transactions=transactions,
    )

    assert result["success"] is True

    assert result["investigation_required"] is True

    assert result["priority"] == "HIGH"

    finding_types = {
        finding["type"]
        for finding in result["findings"]
    }

    assert (
        "REGISTRATION_MUTATION_MISMATCH"
        in finding_types
    )

    assert (
        "SUSPICIOUS_EVENT_SEQUENCE"
        in finding_types
    )


# ================================================================
# 11. UNKNOWN PROPERTY
# ================================================================


def test_unknown_property_does_not_crash():
    """
    An unknown property should return a structured result
    rather than crashing the application.
    """

    result = run_investigation(
        "PROP-DOES-NOT-EXIST"
    )

    assert result["property_id"] == (
        "PROP-DOES-NOT-EXIST"
    )

    assert result["human_review_required"] is True

    assert (
        "Property snapshot"
        in result["missing_evidence"]
    )


# ================================================================
# 12. PROPERTY SNAPSHOT FAILURE
# ================================================================


def test_snapshot_failure_is_handled():
    """
    Simulate a backend/database failure while retrieving
    the property snapshot.
    """

    with patch(
        "backend.orchestrator.get_property_snapshot"
    ) as mocked_snapshot:

        mocked_snapshot.return_value = {
            "success": False,
            "error": "Database unavailable",
        }

        result = run_investigation(
            "PROP-0491"
        )

    assert result["property_id"] == (
        "PROP-0491"
    )

    assert result["human_review_required"] is True

    assert (
        "Property snapshot"
        in result["missing_evidence"]
    )


# ================================================================
# 13. RECENT EVENTS FAILURE
# ================================================================


def test_recent_events_failure_is_handled():
    """
    Simulate a backend/database failure while retrieving
    recent property events.
    """

    with patch(
        "backend.orchestrator.get_recent_events"
    ) as mocked_events:

        mocked_events.return_value = {
            "success": False,
            "error": "Event service unavailable",
        }

        result = run_investigation(
            "PROP-0491"
        )

    assert result["property_id"] == (
        "PROP-0491"
    )

    assert result["human_review_required"] is True

    assert (
        "Recent event history"
        in result["missing_evidence"]
    )


# ================================================================
# 14. NO RECENT EVENTS
# ================================================================


def test_no_recent_events_does_not_trigger_investigation():
    """
    If a property has no recent events, the orchestrator should
    stop cleanly instead of inventing a suspicious pattern.
    """

    with patch(
        "backend.orchestrator.get_recent_events"
    ) as mocked_events:

        mocked_events.return_value = {
            "success": True,
            "property_id": "PROP-NORMAL",
            "events": [],
        }

        result = run_investigation(
            "PROP-NORMAL"
        )

    assert result["investigation_required"] is False

    assert result["priority"] == "LOW"

    assert result["findings"] == []

    assert result["evidence"] == []

    assert result["human_review_required"] is False


# ================================================================
# 15. EMPTY SUPPORTING RECORDS
# ================================================================


def test_empty_supporting_records_are_handled():
    """
    Missing registration/mutation/transaction records should not
    cause an exception.
    """

    with patch(
        "backend.orchestrator.get_registration_history"
    ) as mocked_registration, patch(
        "backend.orchestrator.get_mutation_history"
    ) as mocked_mutation, patch(
        "backend.orchestrator.get_related_transactions"
    ) as mocked_transactions:

        mocked_registration.return_value = {
            "success": True,
            "records": [],
        }

        mocked_mutation.return_value = {
            "success": True,
            "records": [],
        }

        mocked_transactions.return_value = {
            "success": True,
            "transactions": [],
        }

        result = run_investigation(
            "PROP-0491"
        )

    assert result["property_id"] == (
        "PROP-0491"
    )

    assert result["investigation_required"] is False

    assert result["findings"] == []


# ================================================================
# 16. NO INVENTED EVIDENCE
# ================================================================


def test_evidence_agent_does_not_invent_source_records():
    """
    Evidence Agent should only return records available from
    the investigation tools.
    """

    agent = EvidenceAgent()

    result = agent.investigate_finding(
        "PROP-0491",
        {
            "type": "REGISTRATION_MUTATION_MISMATCH",
            "required_evidence": [
                "Underlying sale deed",
                "Mutation order",
            ],
        },
    )

    source_records = {
        item["source_record"]
        for item in result["evidence"]
    }

    assert source_records <= {
        "REG-0491-002",
        "MUT-0491-003",
    }


# ================================================================
# 17. DUPLICATE EVIDENCE IS REMOVED
# ================================================================


def test_duplicate_evidence_is_removed():
    """
    The final Orchestrator result should not contain duplicate
    copies of the same source record.
    """

    result = run_investigation(
        "PROP-0491"
    )

    keys = [
        (
            item.get("source_record"),
            item.get("source_type"),
        )
        for item in result["evidence"]
    ]

    assert len(keys) == len(
        set(keys)
    )


# ================================================================
# 18. PRIORITY IS EXPLAINABLE
# ================================================================


def test_priority_is_one_of_allowed_values():
    """
    Priority must remain one of the defined explainable levels.
    """

    result = run_investigation(
        "PROP-0491"
    )

    assert result["priority"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }


# ================================================================
# 19. RESULT IS JSON SERIALIZABLE
# ================================================================


def test_final_result_is_json_serializable():
    """
    The final result must be suitable for an API/frontend.
    """

    import json

    result = run_investigation(
        "PROP-0491"
    )

    encoded = json.dumps(
        result
    )

    assert encoded

    decoded = json.loads(
        encoded
    )

    assert decoded["property_id"] == (
        "PROP-0491"
    )


# ================================================================
# 20. ORCHESTRATOR CONVENIENCE FUNCTION
# ================================================================


def test_orchestrator_instance_works():
    """
    Verify that OrchestratorAgent can be instantiated directly.
    """

    orchestrator = OrchestratorAgent()

    result = orchestrator.investigate(
        "PROP-0491"
    )

    assert result["property_id"] == (
        "PROP-0491"
    )

    assert result["investigation_required"] is True