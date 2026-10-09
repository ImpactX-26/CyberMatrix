"""Property event endpoints: list, timeline, create."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.events import (
    EventCreate,
    EventCreatedResponse,
    EventDetail,
    EventListResponse,
    TimelineResponse,
)
from app.services import event_service
from app.services.event_service import PropertyNotFoundError

router = APIRouter(prefix="/api/properties", tags=["events"])


def _not_found(err: PropertyNotFoundError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(err),
    )


def _to_detail(e) -> EventDetail:
    return EventDetail(
        event_id=e.id,
        property_id=e.property_id,
        event_type=e.event_type,
        event_date=e.event_date,
        source_type=e.source_type,
        source_id=e.source_id,
        description=e.description,
        previous_state=e.previous_state,
        new_state=e.new_state,
    )


@router.get("/{property_id}/events", response_model=EventListResponse)
def list_events(property_id: str, db: Session = Depends(get_db)):
    try:
        events = event_service.get_property_events(db, property_id)
    except PropertyNotFoundError as err:
        raise _not_found(err)

    return EventListResponse(
        property_id=property_id,
        count=len(events),
        events=[_to_detail(e) for e in events],
    )


@router.get("/{property_id}/timeline", response_model=TimelineResponse)
def get_timeline(property_id: str, db: Session = Depends(get_db)):
    try:
        timeline = event_service.get_property_timeline(db, property_id)
    except PropertyNotFoundError as err:
        raise _not_found(err)

    return TimelineResponse(
        property_id=property_id,
        timeline=timeline,
    )


@router.post(
    "/{property_id}/events",
    response_model=EventCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    property_id: str,
    body: EventCreate,
    db: Session = Depends(get_db),
):
    try:
        event = event_service.create_property_event(db, property_id, body)
    except PropertyNotFoundError as err:
        raise _not_found(err)

    return EventCreatedResponse(
        event_id=event.id,
        property_id=event.property_id,
        event_type=event.event_type,
        event_date=event.event_date,
        status="created",
    )
