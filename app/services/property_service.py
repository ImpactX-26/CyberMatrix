from sqlalchemy.orm import Session

from app.models import Property


def list_properties(db: Session):
    return (
        db.query(Property)
        .order_by(Property.property_id)
        .all()
    )


def get_property(db: Session, property_id: str):
    return (
        db.query(Property)
        .filter(Property.property_id == property_id)
        .first()
    )


def get_property_evidence(db: Session, property_id: str):
    property_obj = get_property(db, property_id)

    if property_obj is None:
        return None

    return property_obj.evidence