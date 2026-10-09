"""All database logic for property events lives here (routes stay thin)."""
from typing import List

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import Event, Evidence, Property
from app.schemas.events import EventCreate


class PropertyNotFoundError(Exception):
    """Raised when a property_id does not exist."""

    def __init__(self, property_id: str):
        self.property_id = property_id
        super().__init__(f"Property {property_id} not found")


def _require_property(db: Session, property_id: str) -> Property:
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if prop is None:
        raise PropertyNotFoundError(property_id)
    return prop


def get_property_events(db: Session, property_id: str) -> List[Event]:
    """All events for a property, oldest first."""
    _require_property(db, property_id)
    return (
        db.query(Event)
        .filter(Event.property_id == property_id)
        .order_by(Event.event_date.asc(), Event.id.asc())
        .all()
    )


def create_property_event(db: Session, property_id: str, data: EventCreate) -> Event:
    """Store a new property event."""
    _require_property(db, property_id)
    event = Event(
        property_id=property_id,
        event_type=data.event_type.value,
        event_date=data.event_date,
        source_type=data.source_type,
        source_id=data.source_id,
        description=data.description,
        
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_property_timeline(db: Session, property_id: str) -> List[dict]:
    """Events in a frontend-friendly chronological shape. Pure formatting, no interpretation."""
    events = get_property_events(db, property_id)
    return [
        {
            "event_id": e.id,
            "event_type": e.event_type,
            "event_date": e.event_date,
            "title": e.event_type.replace("_", " ").title(),  # SALE_REGISTERED -> "Sale Registered"
            "description": e.description,
            "source_type": e.source_type,
            "source_id": e.source_id,
        }
        for e in events
    ]



