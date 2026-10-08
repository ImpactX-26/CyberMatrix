"""Property read endpoints: list, detail, snapshot, evidence."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.properties import (
    EvidenceOut,
    PropertyDetailResponse,
    PropertySnapshot,
    PropertySummary,
)
from app.services import property_service
from app.services.event_service import PropertyNotFoundError

router = APIRouter(prefix="/api/properties", tags=["properties"])


def _not_found(err: PropertyNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.get("", response_model=List[PropertySummary])
def list_properties(db: Session = Depends(get_db)):
    return property_service.list_properties(db)


@router.get("/{property_id}", response_model=PropertyDetailResponse)
def get_property(property_id: str, db: Session = Depends(get_db)):
    try:
        prop = property_service.get_property(db, property_id)
    except PropertyNotFoundError as err:
        raise _not_found(err)
    return PropertyDetailResponse(
        property=prop,
        registrations=sorted(prop.registrations, key=lambda r: (r.transaction_date, r.id)),
        mutations=sorted(prop.mutations, key=lambda m: (m.mutation_date, m.id)),
        mortgages=sorted(prop.mortgages, key=lambda m: (m.mortgage_date, m.id)),
    )


@router.get("/{property_id}/snapshot", response_model=PropertySnapshot)
def get_snapshot(property_id: str, db: Session = Depends(get_db)):
    try:
        return property_service.get_property(db, property_id)
    except PropertyNotFoundError as err:
        raise _not_found(err)


@router.get("/{property_id}/evidence", response_model=List[EvidenceOut])
def get_evidence(property_id: str, db: Session = Depends(get_db)):
    try:
        return property_service.get_property_evidence(db, property_id)
    except PropertyNotFoundError as err:
        raise _not_found(err)