
"""Checks due reminders and sends email through SMTP."""
import logging
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

from sqlalchemy import select

from app.database import SessionLocal
from app.models import LandVisitReminder

log = logging.getLogger("cybermatrix.reminders")


def send_email(reminder: LandVisitReminder) -> None:
    host = os.getenv("SMTP_HOST", "").strip()
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SMTP_FROM_EMAIL", username).strip()
    port = int(os.getenv("SMTP_PORT", "587"))

    if not host or not username or not password or not sender:
        raise RuntimeError(
            "Configure SMTP_HOST, SMTP_PORT, SMTP_USERNAME, "
            "SMTP_PASSWORD and SMTP_FROM_EMAIL in .env."
        )

    message = EmailMessage()
    message["Subject"] = "CyberMatrix: land visit reminder"
    message["From"] = sender
    message["To"] = reminder.user_email
    message.set_content(
        "This is your scheduled CyberMatrix land visit reminder.\n\n"
        f"Property ID: {reminder.property_id}\n"
        f"Village: {reminder.village or 'Not available'}\n"
        f"Survey number: {reminder.survey_number or 'Not available'}\n\n"
        "Please check the current land records before making decisions.\n"
        "This reminder is not legal verification of ownership.\n\n"
        "CyberMatrix"
    )

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(message)


def send_due_reminders_once() -> int:
    """Send due reminders; failed messages remain pending for retry."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db = SessionLocal()
    sent = 0

    try:
        due_ids = list(
            db.scalars(
                select(LandVisitReminder.id)
                .where(
                    LandVisitReminder.status == "pending",
                    LandVisitReminder.scheduled_at <= now,
                )
                .order_by(LandVisitReminder.scheduled_at)
                .limit(20)
            )
        )
    finally:
        db.close()

    for reminder_id in due_ids:
        db = SessionLocal()
        try:
            item = db.get(LandVisitReminder, reminder_id)
            if (
                item is None
                or item.status != "pending"
                or item.scheduled_at > now
            ):
                continue

            try:
                send_email(item)
                item.status = "sent"
                item.sent_at = datetime.now(timezone.utc).replace(
                    tzinfo=None
                )
                item.last_error = None
                db.commit()
                sent += 1
            except Exception as exc:
                item.last_error = str(exc)[:2000]
                db.commit()
                log.exception("Could not send reminder %s", reminder_id)
        finally:
            db.close()

    return sent
