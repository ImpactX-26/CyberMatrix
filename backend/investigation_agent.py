"""
LANDSHIELD Change Investigation Agent.

Responsibilities:
- Analyze property changes.
- Identify suspicious patterns.
- Explain why a pattern matters.
- Identify evidence that should be checked.
- Identify unresolved questions.

This agent does NOT:
- declare fraud
- declare ownership
- determine document authenticity
- provide legal conclusions

The implementation is deterministic so the hackathon demo
works even when an LLM/API key is unavailable.
"""

from __future__ import annotations

from typing import Any

from backend.investigation_rules import evaluate_indicators


class InvestigationAgent:
    """
    Change Investigation Agent.

    The rule engine identifies structured indicators.
    This agent converts those indicators into investigation findings.
    """

    name = "Change Investigation Agent"

    def analyze(
        self,
        property_id: str,
        property_snapshot: dict[str, Any],
        recent_events: list[dict[str, Any]],
        registrations: list[dict[str, Any]],
        mutations: list[dict[str, Any]],
        transactions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Analyze a property's current state and recent history.

        Returns a structured investigation assessment.
        """

        # ---------------------------------------------------------
        # 1. Evaluate investigation indicators
        # ---------------------------------------------------------

        evaluation = evaluate_indicators(
            property_snapshot,
            recent_events,
            registrations,
            mutations,
            transactions,
        )

        indicators = evaluation.get(
            "indicators",
            [],
        )

        investigation_required = evaluation.get(
            "investigation_required",
            False,
        )

        priority = evaluation.get(
            "priority",
            "LOW",
        )

        # ---------------------------------------------------------
        # 2. Convert indicators into structured findings
        # ---------------------------------------------------------

        findings: list[dict[str, Any]] = []

        missing_evidence: list[str] = []

        for indicator in indicators:

            finding = {
                "type": indicator.get(
                    "type"
                ),
                "finding": indicator.get(
                    "finding",
                    "Potential suspicious transaction pattern.",
                ),
                "reason": indicator.get(
                    "reason",
                    "The observed records require additional verification.",
                ),
                "severity": indicator.get(
                    "severity",
                    "MEDIUM",
                ),
                "details": indicator.get(
                    "details",
                    {},
                ),
                "required_evidence": indicator.get(
                    "required_evidence",
                    [],
                ),
            }

            findings.append(finding)

            missing_evidence.extend(
                indicator.get(
                    "required_evidence",
                    [],
                )
            )

        # ---------------------------------------------------------
        # 3. Remove duplicate evidence requirements
        # ---------------------------------------------------------

        missing_evidence = list(
            dict.fromkeys(
                missing_evidence
            )
        )

        # ---------------------------------------------------------
        # 4. Build next verification actions
        # ---------------------------------------------------------

        next_verification: list[str] = []

        for item in missing_evidence:

            if item == "Underlying sale deed":

                next_verification.append(
                    "Review underlying sale deed"
                )

            elif item == "Mutation order":

                next_verification.append(
                    "Review mutation order"
                )

            elif item == "Mortgage record":

                next_verification.append(
                    "Review mortgage record"
                )

            elif item == "Mortgage release record":

                next_verification.append(
                    "Review mortgage release record"
                )

            else:

                next_verification.append(
                    f"Review {item}"
                )

        next_verification = list(
            dict.fromkeys(
                next_verification
            )
        )

        # ---------------------------------------------------------
        # 5. Generate safe investigation summary
        # ---------------------------------------------------------

        if investigation_required:

            summary = (
                "Potential suspicious transaction pattern "
                "requiring verification."
            )

        else:

            summary = (
                "No significant suspicious property-change "
                "indicator was detected in the reviewed records."
            )

        # ---------------------------------------------------------
        # 6. Human review decision
        # ---------------------------------------------------------

        human_review_required = (
            investigation_required
        )

        # ---------------------------------------------------------
        # 7. Return structured result
        # ---------------------------------------------------------

        return {
            "success": True,

            "property_id": property_id,

            "investigation_required": (
                investigation_required
            ),

            "priority": priority,

            "summary": summary,

            "findings": findings,

            "missing_evidence": missing_evidence,

            "next_verification": next_verification,

            "human_review_required": (
                human_review_required
            ),

            "analysis": {
                "property_snapshot_reviewed": True,
                "recent_events_reviewed": len(
                    recent_events
                ),
                "registrations_reviewed": len(
                    registrations
                ),
                "mutations_reviewed": len(
                    mutations
                ),
                "transactions_reviewed": len(
                    transactions
                ),
                "indicator_count": len(
                    indicators
                ),
            },
        }


def get_investigation_agent() -> InvestigationAgent:
    """
    Return a new Change Investigation Agent.
    """

    return InvestigationAgent()