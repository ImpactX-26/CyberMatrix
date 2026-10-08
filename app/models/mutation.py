"""MutationRecord: a change in the revenue (RTC/Pahani) ownership entry."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.property import Property


class MutationRecord(Base):
    __tablename__ = "mutation_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.property_id"), index=True)

    mutation_number: Mapped[str] = mapped_column(String(50))
    mutation_date: Mapped[date] = mapped_column(Date, index=True)
    previous_owner: Mapped[str | None] = mapped_column(String(150), default=None)
    new_owner: Mapped[str | None] = mapped_column(String(150), default=None)
    extent_acres: Mapped[float | None] = mapped_column(Float, default=None)
    mutation_type: Mapped[str | None] = mapped_column(String(50), default=None)  # e.g. "Sale"

    property: Mapped["Property"] = relationship(back_populates="mutations")
