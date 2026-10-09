import json
from datetime import date
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.models import Property, RegistrationRecord, MutationRecord, MortgageRecord


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "person4"


def load_json(filename):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(value):
    return date.fromisoformat(value) if value else None


def main():
    Base.metadata.create_all(bind=engine)

    properties = load_json("properties.json")
    registrations = load_json("registration_records.json")
    mutations = load_json("mutation_records.json")
    mortgages = load_json("mortgage_records.json")

    db = SessionLocal()

    try:
        # Clear existing Person4 records so the importer is safe to rerun.
        property_ids = {row["property_id"] for row in properties}

        for prop in db.query(Property).filter(Property.property_id.in_(property_ids)).all():
            db.delete(prop)

        db.commit()

        # Properties
        for row in properties:
            db.add(
                Property(
                    property_id=row["property_id"],
                    district=row.get("district", ""),
                    taluk=row.get("taluk", ""),
                    hobli=row.get("hobli", ""),
                    village=row.get("village", ""),
                    survey_number=row.get("survey_number", ""),
                    hissa=row.get("hissa"),
                    owner_name=row.get("rtc_owner", ""),
                    extent_acres=row.get("extent_acres", 0),
                    mortgage_status="none",
                    court_status="none",
                    restriction_status="none",
                    baseline_date=date.today(),
                )
            )

        db.flush()

        # Registrations
        for row in registrations:
            db.add(
                RegistrationRecord(
                    property_id=row["property_id"],
                    document_number=row["registration_number"],
                    transaction_date=parse_date(row["registration_date"]),
                    document_type="Registration",
                    seller=row.get("seller"),
                    buyer=row.get("buyer"),
                    extent_acres=row.get("registered_extent_acres"),
                    market_value=None,
                    property_details=f"Survey Number: {row.get('survey_number', '')}",
                )
            )

        # Mutations
        for row in mutations:
            db.add(
                MutationRecord(
                    property_id=row["property_id"],
                    mutation_number=row["mutation_number"],
                    mutation_date=parse_date(row["mutation_date"]),
                    previous_owner=row.get("previous_owner"),
                    new_owner=row.get("new_owner"),
                    extent_acres=None,
                    mutation_type=row.get("mutation_type"),
                )
            )

        # Mortgages
        for row in mortgages:
            status = row.get("status", "ACTIVE").lower()

            db.add(
                MortgageRecord(
                    property_id=row["property_id"],
                    mortgage_id=row["mortgage_number"],
                    mortgage_date=parse_date(row["mortgage_date"]),
                    party=None,
                    institution=row.get("lender"),
                    amount=row.get("amount_inr"),
                    release_date=parse_date(row.get("release_date")),
                    status=status,
                )
            )

        db.commit()

        print("Person4 dataset imported successfully.")
        print(f"Properties:     {len(properties)}")
        print(f"Registrations:  {len(registrations)}")
        print(f"Mutations:      {len(mutations)}")
        print(f"Mortgages:      {len(mortgages)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
