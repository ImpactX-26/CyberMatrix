"""Evidence: a source-backed fact (record, field, value) supporting an event."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.property import Property


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.property_id"), index=True)
    # Nullable so a fact can be stored before/without being tied to one specific event.
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), index=True, default=None)

    source_type: Mapped[str] = mapped_column(String(30))   # registration / mutation / mortgage / ...
    source_id: Mapped[str] = mapped_column(String(50))     # e.g. "MUT-88"
    field_name: Mapped[str] = mapped_column(String(50))    # e.g. "new_owner"
    field_value: Mapped[str | None] = mapped_column(Text, default=None)
    evidence_date: Mapped[date | None] = mapped_column(Date, default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    property: Mapped["Property"] = relationship(back_populates="evidence")
    event: Mapped["Event | None"] = relationship(back_populates="evidence")
