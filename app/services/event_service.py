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
    """Store a new synthetic/demo event (is_demo is always True here)."""
    _require_property(db, property_id)
    event = Event(
        property_id=property_id,
        event_type=data.event_type.value,
        event_date=data.event_date,
        source_type=data.source_type,
        source_id=data.source_id,
        description=data.description,
        is_demo=True,
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


def delete_demo_events(db: Session, property_id: str) -> int:
    """Delete ONLY this property's demo events. Returns how many were deleted.

    Evidence rows are never deleted: if one was linked to a deleted event, it is kept
    and simply unlinked (event_id set to NULL). Property and record tables are untouched.
    """
    _require_property(db, property_id)
    demo_ids = [
        row[0]
        for row in db.query(Event.id)
        .filter(Event.property_id == property_id, Event.is_demo.is_(True))
        .all()
    ]
    if not demo_ids:
        return 0

    db.execute(update(Evidence).where(Evidence.event_id.in_(demo_ids)).values(event_id=None))
    # Bulk delete (not ORM delete) so the Event -> Evidence cascade cannot remove evidence.
    db.query(Event).filter(Event.id.in_(demo_ids)).delete(synchronize_session=False)
    db.commit()
    return len(demo_ids)
