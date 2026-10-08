"""MortgageRecord: a mortgage on a property, and its release if any."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.property import Property


class MortgageRecord(Base):
    __tablename__ = "mortgage_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.property_id"), index=True)

    mortgage_id: Mapped[str] = mapped_column(String(50))
    mortgage_date: Mapped[date] = mapped_column(Date, index=True)
    party: Mapped[str | None] = mapped_column(String(150), default=None)        # borrower
    institution: Mapped[str | None] = mapped_column(String(150), default=None)  # lender
    amount: Mapped[float | None] = mapped_column(Float, default=None)
    release_date: Mapped[date | None] = mapped_column(Date, default=None)       # empty while active
    status: Mapped[str] = mapped_column(String(30), default="active")           # active / released

    property: Mapped["Property"] = relationship(back_populates="mortgages")
