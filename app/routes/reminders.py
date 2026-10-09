
"""API for saving and managing land visit reminders."""
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LandVisitReminder, Property

router = APIRouter(prefix="/api/reminders", tags=["reminders"])
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class ReminderCreate(BaseModel):
    user_email: str = Field(min_length=3, max_length=254)
    property_id: str = Field(min_length=1, max_length=30)
    scheduled_at: datetime
    timezone_name: str = Field(default="UTC", max_length=100)

    @field_validator("user_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_RE.match(value):
            raise ValueError("Enter a valid email address.")
        return value


@router.post("")
def create_reminder(
    payload: ReminderCreate,
    db: Session = Depends(get_db),
):
    prop = db.query(Property).filter(
        Property.property_id == payload.property_id
    ).first()

    if not prop:
        raise HTTPException(status_code=404, detail="Property not found.")

    when = payload.scheduled_at
    if when.tzinfo is None:
        raise HTTPException(
            status_code=422,
            detail="scheduled_at must include a timezone.",
        )

    when = when.astimezone(timezone.utc).replace(tzinfo=None)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if when <= now:
        raise HTTPException(
            status_code=422,
            detail="Reminder time must be in the future.",
        )

    item = LandVisitReminder(
        user_email=payload.user_email,
        property_id=prop.property_id,
        village=prop.village or "",
        survey_number=prop.survey_number or "",
        scheduled_at=when,
        timezone_name=payload.timezone_name,
        status="pending",
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "status": item.status,
        "user_email": item.user_email,
        "property_id": item.property_id,
        "scheduled_at": item.scheduled_at.replace(
            tzinfo=timezone.utc
        ).isoformat(),
        "message": "Reminder saved successfully.",
    }


@router.get("")
def list_reminders(
    user_email: str = Query(min_length=3, max_length=254),
    db: Session = Depends(get_db),
):
    email = user_email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="Invalid email address.")

    rows = (
        db.query(LandVisitReminder)
        .filter(LandVisitReminder.user_email == email)
        .order_by(LandVisitReminder.scheduled_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": x.id,
            "user_email": x.user_email,
            "property_id": x.property_id,
            "village": x.village,
            "survey_number": x.survey_number,
            "scheduled_at": x.scheduled_at.replace(
                tzinfo=timezone.utc
            ).isoformat(),
            "status": x.status,
        }
        for x in rows
    ]


@router.delete("/{reminder_id}")
def cancel_reminder(
    reminder_id: int,
    user_email: str = Query(min_length=3, max_length=254),
    db: Session = Depends(get_db),
):
    email = user_email.strip().lower()

    item = db.query(LandVisitReminder).filter(
        LandVisitReminder.id == reminder_id,
        LandVisitReminder.user_email == email,
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Reminder not found.")

    if item.status == "sent":
        raise HTTPException(
            status_code=409,
            detail="This reminder has already been sent.",
        )

    item.status = "cancelled"
    db.commit()

    return {"id": item.id, "status": item.status}
