"""
LANDSHIELD Orchestrator Agent

Main controller for the LandShield investigation workflow.

Architecture:

User
  |
  v
Orchestrator Agent
  |
  v
Change Investigation Agent
  |
  v
Evidence Agent
  |
  v
Investigation Tools

Safety:
- Never invent facts.
- Never invent documents.
- Never declare fraud confirmed.
- Never declare ownership legally confirmed.
- Never declare a document genuine or fake.
- Never provide legal advice.
"""

from __future__ import annotations

from typing import Any

from .evidence_agent import get_evidence_agent
from .investigation_agent import get_investigation_agent
from .investigation_tools import (
    compare_property_states,
    get_mutation_history,
    get_property_snapshot,
    get_recent_events,
    get_related_transactions,
    get_registration_history,
)
from .investigation_types import InvestigationResult


MAX_INVESTIGATION_STEPS = 8


class OrchestratorAgent:
    """
    Controls the complete LandShield investigation workflow.
    """

    AGENT_NAME = "Orchestrator Agent"

    def __init__(self) -> None:
        self.investigation_agent = get_investigation_agent()
        self.evidence_agent = get_evidence_agent()

    # ================================================================
    # TRACE
    # ================================================================

    def _add_trace(
        self,
        trace: list[dict[str, Any]],
        agent: str,
        action: str,
        input_data: Any,
        result: Any,
        next_action: str,
        status: str,
    ) -> None:

        if len(trace) >= MAX_INVESTIGATION_STEPS:
            return

        trace.append(
            {
                "step": len(trace) + 1,
                "agent": agent,
                "action": action,
                "input": input_data,
                "result": result,
                "next_action": next_action,
                "status": status,
            }
        )

    # ================================================================
    # RESULT HELPER
    # ================================================================

    def _result(
        self,
        property_id: str,
        summary: str,
        trace: list[dict[str, Any]],
        investigation_required: bool = False,
        priority: str = "LOW",
        findings: list[dict[str, Any]] | None = None,
        evidence: list[dict[str, Any]] | None = None,
        missing_evidence: list[str] | None = None,
        next_verification: list[str] | None = None,
        human_review_required: bool = False,
    ) -> dict[str, Any]:

        return InvestigationResult(
            property_id=property_id,
            investigation_required=investigation_required,
            priority=priority,
            summary=summary,
            findings=findings or [],
            evidence=evidence or [],
            missing_evidence=missing_evidence or [],
            next_verification=next_verification or [],
            human_review_required=human_review_required,
            trace=trace,
        ).to_dict()

    # ================================================================
    # MAIN INVESTIGATION
    # ================================================================

    def investigate(
        self,
        property_id: str,
    ) -> dict[str, Any]:

        trace: list[dict[str, Any]] = []

        # ------------------------------------------------------------
        # STEP 1 — START
        # ------------------------------------------------------------

        self._add_trace(
            trace,
            self.AGENT_NAME,
            "start_investigation",
            {
                "property_id": property_id,
            },
            "Investigation started.",
            "get_recent_events",
            "completed",
        )

        # ------------------------------------------------------------
        # STEP 2 — RECENT EVENTS
        #
        # We check recent events first.
        #
        # If the service successfully returns an empty list,
        # the property has nothing new to investigate.
        #
        # If the service fails, we then check the property snapshot.
        # This allows us to distinguish:
        #
        # 1. Unknown property
        # 2. Existing property with event-service failure
        # ------------------------------------------------------------

        events_response = get_recent_events(
            property_id
        )

        # ------------------------------------------------------------
        # EVENT SERVICE FAILURE
        # ------------------------------------------------------------

        if not events_response.get(
            "success",
            False,
        ):

            # Check the property snapshot before deciding
            # which evidence is missing.

            snapshot_check = get_property_snapshot(
                property_id
            )

            # --------------------------------------------------------
            # UNKNOWN PROPERTY
            # --------------------------------------------------------

            if not snapshot_check.get(
                "success",
                False,
            ):

                self._add_trace(
                    trace,
                    self.AGENT_NAME,
                    "get_property_snapshot",
                    {
                        "property_id": property_id,
                    },
                    {
                        "success": False,
                        "error": snapshot_check.get(
                            "error",
                            "Property snapshot unavailable.",
                        ),
                    },
                    "stop",
                    "failed",
                )

                return self._result(
                    property_id=property_id,
                    summary=(
                        "Property snapshot was unavailable. "
                        "Human review is required because the "
                        "property could not be verified."
                    ),
                    trace=trace,
                    investigation_required=False,
                    priority="LOW",
                    findings=[],
                    evidence=[],
                    missing_evidence=[
                        "Property snapshot"
                    ],
                    next_verification=[
                        "Verify property snapshot"
                    ],
                    human_review_required=True,
                )

            # --------------------------------------------------------
            # EXISTING PROPERTY BUT EVENT SERVICE FAILED
            # --------------------------------------------------------

            self._add_trace(
                trace,
                self.AGENT_NAME,
                "get_recent_events",
                {
                    "property_id": property_id,
                },
                {
                    "success": False,
                    "error": events_response.get(
                        "error",
                        "Recent event history unavailable.",
                    ),
                },
                "stop",
                "failed",
            )

            return self._result(
                property_id=property_id,
                summary=(
                    "Recent event history was unavailable. "
                    "Human review is required because the "
                    "event history could not be verified."
                ),
                trace=trace,
                investigation_required=False,
                priority="LOW",
                findings=[],
                evidence=[],
                missing_evidence=[
                    "Recent event history"
                ],
                next_verification=[
                    "Verify recent event history"
                ],
                human_review_required=True,
            )

        # ------------------------------------------------------------
        # EVENT SERVICE SUCCESS
        # ------------------------------------------------------------

        recent_events = events_response.get(
            "events",
            [],
        )

        # ------------------------------------------------------------
        # NO RECENT EVENTS
        #
        # Successful empty event history is a normal LOW outcome.
        # Do not require human review.
        # ------------------------------------------------------------

        if not recent_events:

            self._add_trace(
                trace,
                self.AGENT_NAME,
                "check_recent_events",
                {
                    "property_id": property_id,
                    "event_count": 0,
                },
                "No recent property events found.",
                "complete_investigation",
                "completed",
            )

            return self._result(
                property_id=property_id,
                summary=(
                    "No recent property events require "
                    "investigation."
                ),
                trace=trace,
                investigation_required=False,
                priority="LOW",
                findings=[],
                evidence=[],
                missing_evidence=[],
                next_verification=[],
                human_review_required=False,
            )

        # ------------------------------------------------------------
        # EVENTS EXIST
        # ------------------------------------------------------------

        self._add_trace(
            trace,
            self.AGENT_NAME,
            "get_recent_events",
            {
                "property_id": property_id,
            },
            {
                "event_count": len(
                    recent_events
                ),
            },
            "get_property_snapshot",
            "completed",
        )

        # ------------------------------------------------------------
        # STEP 3 — PROPERTY SNAPSHOT
        # ------------------------------------------------------------

        snapshot_response = get_property_snapshot(
            property_id
        )

        # ------------------------------------------------------------
        # SNAPSHOT FAILURE
        # ------------------------------------------------------------

        if not snapshot_response.get(
            "success",
            False,
        ):

            self._add_trace(
                trace,
                self.AGENT_NAME,
                "get_property_snapshot",
                {
                    "property_id": property_id,
                },
                {
                    "success": False,
                    "error": snapshot_response.get(
                        "error",
                        "Property snapshot unavailable.",
                    ),
                },
                "stop",
                "failed",
            )

            return self._result(
                property_id=property_id,
                summary=(
                    "Property snapshot was unavailable. "
                    "Human review is required because the "
                    "property state could not be verified."
                ),
                trace=trace,
                investigation_required=False,
                priority="LOW",
                findings=[],
                evidence=[],
                missing_evidence=[
                    "Property snapshot"
                ],
                next_verification=[
                    "Verify property snapshot"
                ],
                human_review_required=True,
            )

        property_snapshot = snapshot_response.get(
            "property",
            snapshot_response.get(
                "snapshot",
                {},
            ),
        )

        self._add_trace(
            trace,
            self.AGENT_NAME,
            "get_property_snapshot",
            {
                "property_id": property_id,
            },
            "Current property snapshot retrieved.",
            "get_supporting_records",
            "completed",
        )

        # ------------------------------------------------------------
        # STEP 4 — SUPPORTING RECORDS
        # ------------------------------------------------------------

        registration_response = (
            get_registration_history(
                property_id
            )
        )

        mutation_response = (
            get_mutation_history(
                property_id
            )
        )

        transaction_response = (
            get_related_transactions(
                property_id
            )
        )

        registrations = registration_response.get(
            "records",
            [],
        )

        mutations = mutation_response.get(
            "records",
            [],
        )

        transactions = transaction_response.get(
            "transactions",
            [],
        )

        # ------------------------------------------------------------
        # EMPTY SUPPORTING RECORDS
        #
        # Do not infer suspicious behavior when the underlying
        # supporting records are unavailable.
        # ------------------------------------------------------------

        if (
            not registrations
            and not mutations
            and not transactions
        ):

            self._add_trace(
                trace,
                self.AGENT_NAME,
                "check_supporting_records",
                {
                    "property_id": property_id,
                    "registration_count": len(
                        registrations
                    ),
                    "mutation_count": len(
                        mutations
                    ),
                    "transaction_count": len(
                        transactions
                    ),
                },
                (
                    "Supporting registration, mutation, "
                    "and transaction records are empty."
                ),
                "complete_investigation",
                "completed",
            )

            return self._result(
                property_id=property_id,
                summary=(
                    "Supporting registration, mutation, "
                    "and transaction records were unavailable, "
                    "so no suspicious finding was inferred."
                ),
                trace=trace,
                investigation_required=False,
                priority="LOW",
                findings=[],
                evidence=[],
                missing_evidence=[],
                next_verification=[],
                human_review_required=False,
            )

        self._add_trace(
            trace,
            self.AGENT_NAME,
            "get_supporting_records",
            {
                "property_id": property_id,
            },
            {
                "registration_count": len(
                    registrations
                ),
                "mutation_count": len(
                    mutations
                ),
                "transaction_count": len(
                    transactions
                ),
            },
            "change_investigation",
            "completed",
        )

        # ------------------------------------------------------------
        # STEP 5 — CHANGE INVESTIGATION AGENT
        # ------------------------------------------------------------

        investigation = (
            self.investigation_agent.analyze(
                property_id=property_id,
                property_snapshot=property_snapshot,
                recent_events=recent_events,
                registrations=registrations,
                mutations=mutations,
                transactions=transactions,
            )
        )

        findings = investigation.get(
            "findings",
            [],
        )

        self._add_trace(
            trace,
            "Change Investigation Agent",
            "analyze_property_changes",
            {
                "property_id": property_id,
                "event_count": len(
                    recent_events
                ),
                "registration_count": len(
                    registrations
                ),
                "mutation_count": len(
                    mutations
                ),
                "transaction_count": len(
                    transactions
                ),
            },
            {
                "investigation_required": investigation.get(
                    "investigation_required",
                    False,
                ),
                "priority": investigation.get(
                    "priority",
                    "LOW",
                ),
                "finding_count": len(
                    findings
                ),
            },
            (
                "evidence_investigation"
                if findings
                else "complete_investigation"
            ),
            "completed",
        )

        # ------------------------------------------------------------
        # NO FINDINGS
        # ------------------------------------------------------------

        if not findings:

            return self._result(
                property_id=property_id,
                summary=investigation.get(
                    "summary",
                    (
                        "No significant suspicious "
                        "property-change indicator was detected."
                    ),
                ),
                trace=trace,
                investigation_required=False,
                priority="LOW",
                findings=[],
                evidence=[],
                missing_evidence=[],
                next_verification=[],
                human_review_required=False,
            )

        # ------------------------------------------------------------
        # STEP 6 — EVIDENCE AGENT
        # ------------------------------------------------------------

        all_evidence: list[
            dict[str, Any]
        ] = []

        all_missing_evidence: list[
            str
        ] = []

        all_next_verification: list[
            str
        ] = []

        for index, finding in enumerate(
            findings
        ):

            # Reserve one trace step for completion.
            if (
                len(trace)
                >= MAX_INVESTIGATION_STEPS - 1
            ):
                break

            evidence_result = (
                self.evidence_agent.investigate_finding(
                    property_id=property_id,
                    finding=finding,
                )
            )

            # --------------------------------------------------------
            # Evidence
            # --------------------------------------------------------

            for evidence_item in (
                evidence_result.get(
                    "evidence",
                    [],
                )
            ):

                if (
                    evidence_item
                    not in all_evidence
                ):
                    all_evidence.append(
                        evidence_item
                    )

            # --------------------------------------------------------
            # Missing evidence
            # --------------------------------------------------------

            for missing_item in (
                evidence_result.get(
                    "missing_evidence",
                    [],
                )
            ):

                if (
                    missing_item
                    not in all_missing_evidence
                ):
                    all_missing_evidence.append(
                        missing_item
                    )

            # --------------------------------------------------------
            # Next verification
            # --------------------------------------------------------

            for next_item in (
                evidence_result.get(
                    "next_verification",
                    [],
                )
            ):

                if (
                    next_item
                    not in all_next_verification
                ):
                    all_next_verification.append(
                        next_item
                    )

            self._add_trace(
                trace,
                "Evidence Agent",
                "retrieve_evidence",
                {
                    "property_id": property_id,
                    "finding_type": finding.get(
                        "type",
                        "UNKNOWN",
                    ),
                },
                {
                    "success": evidence_result.get(
                        "success",
                        False,
                    ),
                    "evidence_count": len(
                        evidence_result.get(
                            "evidence",
                            [],
                        )
                    ),
                    "missing_evidence_count": len(
                        evidence_result.get(
                            "missing_evidence",
                            [],
                        )
                    ),
                },
                (
                    "check_next_finding"
                    if index < len(findings) - 1
                    else "compare_property_states"
                ),
                "completed",
            )

        # ------------------------------------------------------------
        # STEP 7 — COMPARE PROPERTY STATES
        # ------------------------------------------------------------

        comparison_response = (
            compare_property_states(
                property_id=property_id
            )
        )

        comparison_result = (
            comparison_response.get(
                "comparison",
                comparison_response.get(
                    "differences",
                    comparison_response.get(
                        "result",
                        {},
                    ),
                ),
            )
        )

        self._add_trace(
            trace,
            self.AGENT_NAME,
            "compare_property_states",
            {
                "property_id": property_id,
            },
            comparison_result,
            "complete_investigation",
            "completed",
        )

        # ------------------------------------------------------------
        # DEDUPLICATE EVIDENCE
        # ------------------------------------------------------------

        unique_evidence: list[
            dict[str, Any]
        ] = []

        seen_evidence_keys: set[
            tuple[Any, Any]
        ] = set()

        for item in all_evidence:

            if not isinstance(
                item,
                dict,
            ):
                continue

            key = (
                item.get("source_record"),
                item.get("source_type"),
            )

            if key in seen_evidence_keys:
                continue

            seen_evidence_keys.add(
                key
            )

            unique_evidence.append(
                item
            )

        # ------------------------------------------------------------
        # STEP 8 — COMPLETE
        # ------------------------------------------------------------

        self._add_trace(
            trace,
            self.AGENT_NAME,
            "complete_investigation",
            {
                "property_id": property_id,
            },
            {
                "priority": investigation.get(
                    "priority",
                    "LOW",
                ),
                "evidence_count": len(
                    unique_evidence
                ),
                "missing_evidence_count": len(
                    all_missing_evidence
                ),
            },
            "stop",
            "completed",
        )

        # ------------------------------------------------------------
        # FINAL RESULT
        # ------------------------------------------------------------

        return self._result(
            property_id=property_id,
            summary=investigation.get(
                "summary",
                (
                    "Potential suspicious transaction "
                    "pattern requiring verification."
                ),
            ),
            trace=trace,
            investigation_required=investigation.get(
                "investigation_required",
                False,
            ),
            priority=investigation.get(
                "priority",
                "LOW",
            ),
            findings=findings,
            evidence=unique_evidence,
            missing_evidence=all_missing_evidence,
            next_verification=all_next_verification,
            human_review_required=investigation.get(
                "human_review_required",
                bool(findings),
            ),
        )


# ====================================================================
# SHARED ORCHESTRATOR INSTANCE
# ====================================================================

_orchestrator: OrchestratorAgent | None = None


def get_orchestrator() -> OrchestratorAgent:
    """
    Return the shared orchestrator instance.
    """

    global _orchestrator

    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()

    return _orchestrator


# ====================================================================
# PUBLIC ENTRY POINT
# ====================================================================

def run_investigation(
    property_id: str,
) -> dict[str, Any]:
    """
    Public entry point used by tests, CLI, and frontend.
    """

    orchestrator = get_orchestrator()

    return orchestrator.investigate(
        property_id
    )