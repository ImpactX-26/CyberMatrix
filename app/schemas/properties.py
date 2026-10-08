"""Pydantic schemas for the property read APIs (internal DB ids are not exposed)."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class _FromORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PropertySummary(_FromORM):
    """One row in GET /api/properties."""

    property_id: str
    district: str
    taluk: str
    hobli: str
    village: str
    survey_number: str
    hissa: Optional[str] = None
    owner_name: str
    extent_acres: float
    mortgage_status: str
    court_status: str
    restriction_status: str
    baseline_date: date


class RegistrationOut(_FromORM):
    document_number: str
    transaction_date: date
    document_type: str
    seller: Optional[str] = None
    buyer: Optional[str] = None
    extent_acres: Optional[float] = None
    market_value: Optional[float] = None
    property_details: Optional[str] = None


class MutationOut(_FromORM):
    mutation_number: str
    mutation_date: date
    previous_owner: Optional[str] = None
    new_owner: Optional[str] = None
    extent_acres: Optional[float] = None
    mutation_type: Optional[str] = None


class MortgageOut(_FromORM):
    mortgage_id: str
    mortgage_date: date
    party: Optional[str] = None
    institution: Optional[str] = None
    amount: Optional[float] = None
    release_date: Optional[date] = None
    status: str


class PropertyDetailResponse(BaseModel):
    """GET /api/properties/{property_id}. Events live in the Event API, not here."""

    property: PropertySummary
    registrations: List[RegistrationOut]
    mutations: List[MutationOut]
    mortgages: List[MortgageOut]


class PropertySnapshot(_FromORM):
    """GET /api/properties/{property_id}/snapshot - the known recorded state, nothing derived."""

    property_id: str
    owner_name: str
    survey_number: str
    hissa: Optional[str] = None
    extent_acres: float
    mortgage_status: str
    court_status: str
    restriction_status: str
    baseline_date: date


class EvidenceOut(_FromORM):
    """One item of GET /api/properties/{property_id}/evidence."""

    id: int
    event_id: Optional[int] = None
    source_type: str
    source_id: str
    field_name: str
    field_value: Optional[str] = None
    evidence_date: Optional[date] = None
    description: Optional[str] = None