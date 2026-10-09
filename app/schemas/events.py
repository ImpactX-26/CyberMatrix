"""Pydantic schemas for the property event API."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """The only event types the API accepts. Anything else is rejected with a 422."""

    SALE_REGISTERED = "SALE_REGISTERED"
    MUTATION_UPDATED = "MUTATION_UPDATED"
    MORTGAGE_REGISTERED = "MORTGAGE_REGISTERED"
    MORTGAGE_RELEASED = "MORTGAGE_RELEASED"
    OWNER_CHANGED = "OWNER_CHANGED"
    EXTENT_CHANGED = "EXTENT_CHANGED"
    SURVEY_CHANGED = "SURVEY_CHANGED"
    RESTRICTION_CHANGED = "RESTRICTION_CHANGED"
    COURT_STATUS_CHANGED = "COURT_STATUS_CHANGED"


class EventCreate(BaseModel):
    """Request body for POST /api/properties/{property_id}/events."""

    event_type: EventType
    event_date: date  # must be a valid ISO date, e.g. "2026-08-12"
    source_type: Optional[str] = Field(default=None, max_length=30)
    source_id: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = None


class EventCreatedResponse(BaseModel):
    """Response for a successful POST."""

    event_id: int
    property_id: str
    event_type: EventType
    event_date: date
    status: str = "created"


class EventDetail(BaseModel):
    """One event as returned by GET .../events."""

    event_id: int
    property_id: str
    event_type: str
    event_date: date
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    description: Optional[str] = None
    
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None


class EventListResponse(BaseModel):
    property_id: str
    count: int
    events: List[EventDetail]


class TimelineEvent(BaseModel):
    event_id: int
    event_type: str
    event_date: date
    title: str
    description: Optional[str] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None


class TimelineResponse(BaseModel):
    property_id: str
    timeline: List[TimelineEvent]



