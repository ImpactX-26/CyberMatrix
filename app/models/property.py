"""Property: the parent entity. Every other table points back to it."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import Date, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.evidence import Evidence
    from app.models.mortgage import MortgageRecord
    from app.models.mutation import MutationRecord
    from app.models.registration import RegistrationRecord


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Business key used everywhere else, e.g. "PROP-0491" (unique + indexed)
    property_id: Mapped[str] = mapped_column(String(30), unique=True, index=True)

    district: Mapped[str] = mapped_column(String(100))
    taluk: Mapped[str] = mapped_column(String(100))
    hobli: Mapped[str] = mapped_column(String(100))
    village: Mapped[str] = mapped_column(String(100))
    survey_number: Mapped[str] = mapped_column(String(30), index=True)
    hissa: Mapped[str | None] = mapped_column(String(30), default=None)

    owner_name: Mapped[str] = mapped_column(String(150))
    extent_acres: Mapped[float] = mapped_column(Float)

    # Current-state fields (the change engine will compare these over time)
    mortgage_status: Mapped[str] = mapped_column(String(30), default="none")
    court_status: Mapped[str] = mapped_column(String(30), default="none")
    restriction_status: Mapped[str] = mapped_column(String(30), default="none")

    baseline_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # One property -> many children. Deleting a property removes its own children.
    registrations: Mapped[List["RegistrationRecord"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    mutations: Mapped[List["MutationRecord"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    mortgages: Mapped[List["MortgageRecord"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    events: Mapped[List["Event"]] = relationship(
        back_populates="property", cascade="all, delete-orphan", order_by="Event.event_date"
    )
    evidence: Mapped[List["Evidence"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Property {self.property_id} survey={self.survey_number}/{self.hissa}>"
