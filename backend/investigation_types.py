"""
LandShield investigation data types.

Shared structures used by:
- Orchestrator Agent
- Change Investigation Agent
- Evidence Agent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InvestigationTrace:
    """
    One step in the investigation trace.
    """

    step: int
    agent: str
    action: str
    input: Any
    result: Any
    next_action: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "agent": self.agent,
            "action": self.action,
            "input": self.input,
            "result": self.result,
            "next_action": self.next_action,
            "status": self.status,
        }


@dataclass
class Finding:
    """
    A suspicious pattern identified during investigation.
    """

    type: str
    finding: str
    reason: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    next_verification: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "finding": self.finding,
            "reason": self.reason,
            "evidence": self.evidence,
            "missing_evidence": self.missing_evidence,
            "next_verification": self.next_verification,
        }


@dataclass
class InvestigationResult:
    """
    Final structured result returned by LandShield.
    """

    property_id: str
    investigation_required: bool
    priority: str
    summary: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    next_verification: list[str] = field(default_factory=list)
    human_review_required: bool = False
    trace: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "property_id": self.property_id,
            "investigation_required": self.investigation_required,
            "priority": self.priority,
            "summary": self.summary,
            "findings": self.findings,
            "evidence": self.evidence,
            "missing_evidence": self.missing_evidence,
            "next_verification": self.next_verification,
            "human_review_required": self.human_review_required,
            "trace": self.trace,
        }