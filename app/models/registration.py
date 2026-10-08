"""RegistrationRecord: a registered deed (sale, gift, etc.) for a property."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.property import Property


class RegistrationRecord(Base):
    __tablename__ = "registration_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.property_id"), index=True)

    document_number: Mapped[str] = mapped_column(String(50))
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    document_type: Mapped[str] = mapped_column(String(50))  # e.g. "Sale Deed"
    seller: Mapped[str | None] = mapped_column(String(150), default=None)
    buyer: Mapped[str | None] = mapped_column(String(150), default=None)
    extent_acres: Mapped[float | None] = mapped_column(Float, default=None)
    market_value: Mapped[float | None] = mapped_column(Float, default=None)
    property_details: Mapped[str | None] = mapped_column(Text, default=None)

    property: Mapped["Property"] = relationship(back_populates="registrations")
