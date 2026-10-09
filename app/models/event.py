"""Event: one detected change in a property's recorded state."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import JSON, Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.evidence import Evidence
    from app.models.property import Property


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.property_id"), index=True)

    event_type: Mapped[str] = mapped_column(String(50))            # e.g. "MORTGAGE_REGISTERED"
    event_date: Mapped[date] = mapped_column(Date, index=True)
    source_type: Mapped[str | None] = mapped_column(String(30), default=None)  # registration / mutation / ...
    source_id: Mapped[str | None] = mapped_column(String(50), default=None)    # e.g. "REG-102"
    description: Mapped[str | None] = mapped_column(Text, default=None)

    

    # Structured before/after snapshots stored as JSON dicts, e.g.
    # {"owner_name": "Person A", "extent_acres": 5.0, "mortgage_status": "None"}
    previous_state: Mapped[Dict[str, Any] | None] = mapped_column(JSON, default=None)
    new_state: Mapped[Dict[str, Any] | None] = mapped_column(JSON, default=None)

    property: Mapped["Property"] = relationship(back_populates="events")
    evidence: Mapped[List["Evidence"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
