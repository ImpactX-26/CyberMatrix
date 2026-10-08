"""
LANDSHIELD Evidence Agent.

Responsible for retrieving and organizing evidence for investigation findings.

This agent:
- retrieves evidence using investigation tools
- never invents evidence
- links source records to findings
- identifies missing evidence
- recommends next verification steps

It does NOT declare fraud, ownership, or document authenticity.
"""

from __future__ import annotations

from typing import Any

from backend.investigation_tools import (
    find_evidence,
    get_mutation_history,
    get_registration_history,
)


class EvidenceAgent:
    """
    Evidence retrieval and organization agent.

    The agent is intentionally deterministic for the hackathon.
    An LLM can be added later without changing the interface.
    """

    name = "Evidence Agent"

    def investigate_finding(
        self,
        property_id: str,
        finding: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Retrieve evidence relevant to one investigation finding.

        Parameters
        ----------
        property_id:
            Property being investigated.

        finding:
            Indicator returned by investigation_rules.py.

        Returns
        -------
        dict
            Structured evidence result.
        """

        finding_type = finding.get("type", "")
        required_evidence = finding.get("required_evidence", [])

        evidence: list[dict[str, Any]] = []
        missing_evidence: list[str] = []
        next_verification: list[str] = []

        # =========================================================
        # 1. REGISTRATION / MUTATION MISMATCH
        # =========================================================
        if finding_type == "REGISTRATION_MUTATION_MISMATCH":

            registration_result = get_registration_history(
                property_id
            )

            mutation_result = get_mutation_history(
                property_id
            )

            registrations = registration_result.get(
                "records",
                [],
            )

            mutations = mutation_result.get(
                "records",
                [],
            )

            # -----------------------------------------------------
            # Registration evidence
            # -----------------------------------------------------
            if registrations:
                registration = registrations[-1]

                evidence.append(
                    {
                        "source_record": registration.get(
                            "record_id"
                        ),
                        "source_type": "REGISTRATION",
                        "field": "buyer",
                        "value": registration.get(
                            "buyer"
                        ),
                        "date": registration.get(
                            "date"
                        ),
                        "related_record": (
                            mutations[-1].get("record_id")
                            if mutations
                            else None
                        ),
                        "reason": (
                            "The registration identifies "
                            "the receiving party recorded "
                            "in the transaction."
                        ),
                    }
                )

            else:
                missing_evidence.append(
                    "Registration record"
                )

            # -----------------------------------------------------
            # Mutation evidence
            # -----------------------------------------------------
            if mutations:
                mutation = mutations[-1]

                evidence.append(
                    {
                        "source_record": mutation.get(
                            "record_id"
                        ),
                        "source_type": "MUTATION",
                        "field": "new_owner",
                        "value": mutation.get(
                            "new_owner"
                        ),
                        "date": mutation.get(
                            "date"
                        ),
                        "related_record": (
                            registrations[-1].get(
                                "record_id"
                            )
                            if registrations
                            else None
                        ),
                        "reason": (
                            "The mutation identifies "
                            "the party recorded as the "
                            "new owner in the mutation record."
                        ),
                    }
                )

            else:
                missing_evidence.append(
                    "Mutation record"
                )

            # -----------------------------------------------------
            # Evidence required by the rule
            # -----------------------------------------------------
            for item in required_evidence:

                if item not in missing_evidence:

                    if item not in (
                        "Registration record",
                        "Mutation record",
                    ):
                        missing_evidence.append(item)

            # -----------------------------------------------------
            # Recommended verification
            # -----------------------------------------------------
            next_verification.extend(
                [
                    "Review underlying sale deed",
                    "Review mutation order",
                ]
            )

        # =========================================================
        # 2. SUSPICIOUS EVENT SEQUENCE
        # =========================================================
        elif finding_type == "SUSPICIOUS_EVENT_SEQUENCE":

            # The current investigation tool supports source_types.
            # It does not support an evidence_types parameter.
            #
            # We retrieve registration and mutation records here.
            # Mortgage records remain a required verification item
            # because the current demo evidence tool does not expose
            # them as source records.

            evidence_result = find_evidence(
                property_id=property_id,
                source_types=[
                    "REGISTRATION",
                    "MUTATION",
                ],
            )

            records = evidence_result.get(
                "evidence",
                [],
            )

            for item in records:

                # find_evidence() returns the actual record
                # inside the "record" field.
                record = item.get(
                    "record",
                    {},
                )

                source_record = (
                    item.get("source_record")
                    or record.get("record_id")
                    or record.get("source_record")
                )

                source_type = (
                    item.get("source_type")
                    or record.get("source_type")
                    or ""
                )

                evidence.append(
                    {
                        "source_record": source_record,
                        "source_type": source_type,
                        "field": "event",
                        "value": (
                            record.get("event_type")
                            or record.get("transaction_type")
                            or source_type
                        ),
                        "date": record.get("date"),
                        "related_record": record.get(
                            "source_record"
                        ),
                        "reason": (
                            "This record forms part of "
                            "the chronological event sequence "
                            "requiring verification."
                        ),
                    }
                )

            # -----------------------------------------------------
            # Required evidence that is not directly available
            # -----------------------------------------------------
            available_source_types = {
                item.get("source_type")
                or item.get("record", {}).get("source_type")
                for item in records
            }

            if not records:
                missing_evidence.extend(
                    [
                        "Mortgage record",
                        "Underlying sale deed",
                        "Mutation order",
                        "Mortgage release record",
                    ]
                )
            else:
                # The current demo tool does not expose these
                # documents as direct evidence records.
                if "MORTGAGE" not in available_source_types:
                    missing_evidence.append(
                        "Mortgage record"
                    )

                if "MORTGAGE_RELEASE" not in available_source_types:
                    missing_evidence.append(
                        "Mortgage release record"
                    )

                missing_evidence.extend(
                    [
                        "Underlying sale deed",
                        "Mutation order",
                    ]
                )

            # -----------------------------------------------------
            # Recommended verification
            # -----------------------------------------------------
            next_verification.extend(
                [
                    "Review mortgage record",
                    "Review underlying sale deed",
                    "Review mutation order",
                    "Review mortgage release record",
                ]
            )

        # =========================================================
        # 3. GENERIC FINDING
        # =========================================================
        else:

            evidence_result = find_evidence(
                property_id=property_id,
            )

            records = evidence_result.get(
                "evidence",
                [],
            )

            for item in records:

                record = item.get(
                    "record",
                    {},
                )

                source_record = (
                    item.get("source_record")
                    or record.get("record_id")
                    or record.get("source_record")
                )

                source_type = (
                    item.get("source_type")
                    or record.get("source_type")
                    or ""
                )

                evidence.append(
                    {
                        "source_record": source_record,
                        "source_type": source_type,
                        "field": "event",
                        "value": (
                            record.get("event_type")
                            or record.get("transaction_type")
                            or source_type
                        ),
                        "date": record.get("date"),
                        "related_record": record.get(
                            "source_record"
                        ),
                        "reason": (
                            "The record is relevant to "
                            "the investigation finding "
                            "and should be reviewed."
                        ),
                    }
                )

            if not records:
                missing_evidence.extend(
                    required_evidence
                )

            next_verification.extend(
                required_evidence
            )

        # =========================================================
        # 4. REMOVE DUPLICATES
        # =========================================================

        missing_evidence = list(
            dict.fromkeys(missing_evidence)
        )

        next_verification = list(
            dict.fromkeys(next_verification)
        )

        # =========================================================
        # 5. RETURN STRUCTURED RESULT
        # =========================================================

        return {
            "success": True,
            "property_id": property_id,
            "finding_type": finding_type,
            "evidence": evidence,
            "missing_evidence": missing_evidence,
            "next_verification": next_verification,
            "human_review_required": True,
        }


def get_evidence_agent() -> EvidenceAgent:
    """
    Return a new Evidence Agent instance.
    """

    return EvidenceAgent()