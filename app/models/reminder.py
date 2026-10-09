
"""Persistent land visit reminders."""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LandVisitReminder(Base):
    __tablename__ = "land_visit_reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_email: Mapped[str] = mapped_column(String(254), index=True)
    property_id: Mapped[str] = mapped_column(String(30), index=True)
    village: Mapped[str] = mapped_column(String(100), default="")
    survey_number: Mapped[str] = mapped_column(String(50), default="")
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    timezone_name: Mapped[str] = mapped_column(String(100), default="UTC")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
