"""LandShield STEP 3 - synthetic demo dataset.

Run from the backend/ folder:   python -m app.seed

Creates exactly 10 SYNTHETIC properties (PROP-001 .. PROP-010) with registration,
mutation and mortgage records plus chronological demo events (is_demo=True).

Safe to re-run: it removes ONLY the previous demo dataset (properties PROP-001..PROP-010
and their children / demo events) and recreates it. Other data is never touched.

All names, document numbers and institutions below are fictional. The suspicious
scenarios are encoded in the records themselves (mismatched parties, extents, survey
values, broken chains); nothing is labelled "fraud" and no detection logic lives here.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import delete, func, select

from app import models  # noqa: F401  (registers all tables on Base.metadata)
from app.database import Base, SessionLocal, engine
from app.models import (
    Event,
    Evidence,
    MortgageRecord,
    MutationRecord,
    Property,
    RegistrationRecord,
)
from app.schemas.events import EventType

BASELINE = date(2022, 1, 10)  # all demo baselines are taken on this date
DEMO_IDS = [f"PROP-{i:03d}" for i in range(1, 11)]

BANK_A = "Demo Rural Credit Bank"
BANK_B = "Sample Agri Finance Ltd"


def d(y: int, m: int, day: int) -> date:
    return date(y, m, day)


# --------------------------------------------------------------------------------------
# Scenario definitions (pure data)
#   reg tuple: (doc_no, date, doc_type, seller, buyer, extent, value, property_details)
#   mut tuple: (mut_no, date, previous_owner, new_owner, extent, mutation_type)
#   mort dict: mortgage_id, date, party, institution, amount, release_date (or None)
#   extra_events: events not derivable from a record (e.g. SURVEY_CHANGED)
# --------------------------------------------------------------------------------------
SCENARIOS = [
    {
        "property_id": "PROP-001",
        "title": "Normal sale + matching mutation",
        "loc": ("Bengaluru Rural", "Hosakote", "Anugondanahalli", "Demovalli"),
        "survey": "112/3", "hissa": "1", "owner": "Rahul Sharma", "extent": 4.0,
        "registrations": [
            ("SYN-REG-1001", d(2023, 3, 14), "Sale Deed", "Rahul Sharma", "Anita Rao", 4.0,
             6_400_000, "Survey No. 112/3, Hissa 1, Demovalli village"),
        ],
        "mutations": [
            ("SYN-MUT-1001", d(2023, 4, 20), "Rahul Sharma", "Anita Rao", 4.0, "Sale"),
        ],
        "mortgages": [],
        "extra_events": [],
    },
    {
        "property_id": "PROP-002",
        "title": "Normal mortgage -> release -> sale",
        "loc": ("Mysuru", "Nanjangud", "Kadakola", "Sampurapura"),
        "survey": "78/2", "hissa": "1B", "owner": "Suresh Nair", "extent": 3.5,
        "registrations": [
            ("SYN-REG-2001", d(2024, 2, 20), "Sale Deed", "Suresh Nair", "Meena Iyer", 3.5,
             5_250_000, "Survey No. 78/2, Hissa 1B, Sampurapura village"),
        ],
        "mutations": [
            ("SYN-MUT-2001", d(2024, 3, 25), "Suresh Nair", "Meena Iyer", 3.5, "Sale"),
        ],
        "mortgages": [
            {"mortgage_id": "SYN-MTG-2001", "date": d(2022, 8, 10), "party": "Suresh Nair",
             "institution": BANK_A, "amount": 1_800_000, "release_date": d(2023, 11, 5)},
        ],
        "extra_events": [],
    },
    {
        "property_id": "PROP-003",
        "title": "Registration/mutation owner mismatch",
        "loc": ("Tumakuru", "Gubbi", "Nitturu", "Kalyanapura"),
        "survey": "34/1", "hissa": "3", "owner": "Rahul Sharma", "extent": 6.0,
        "registrations": [
            ("SYN-REG-3001", d(2023, 6, 12), "Sale Deed", "Rahul Sharma", "Vikram Kumar", 6.0,
             7_800_000, "Survey No. 34/1, Hissa 3, Kalyanapura village"),
        ],
        "mutations": [
            # Registered buyer is Vikram Kumar, but the revenue entry names Neha Patel.
            ("SYN-MUT-3001", d(2023, 7, 18), "Rahul Sharma", "Neha Patel", 6.0, "Sale"),
        ],
        "mortgages": [],
        "extra_events": [],
    },
    {
        "property_id": "PROP-004",
        "title": "Overlapping transaction extent",
        "loc": ("Ramanagara", "Channapatna", "Virupakshipura", "Hemmanahalli"),
        "survey": "21/4", "hissa": "2", "owner": "Arjun Reddy", "extent": 5.0,
        "registrations": [
            ("SYN-REG-4001", d(2023, 2, 15), "Sale Deed", "Arjun Reddy", "Kavya Menon", 3.0,
             3_900_000,
             "Survey No. 21/4, Hissa 2, Hemmanahalli village; 3.0 acres, north-eastern portion"),
            # Seller had 5.0 acres, sold 3.0, then sells 3.5 more (6.5 total) over the same area.
            ("SYN-REG-4002", d(2023, 5, 10), "Sale Deed", "Arjun Reddy", "Deepak Joshi", 3.5,
             4_550_000,
             "Survey No. 21/4, Hissa 2, Hemmanahalli village; 3.5 acres, central and north-eastern portion"),
        ],
        "mutations": [
            ("SYN-MUT-4001", d(2023, 3, 20), "Arjun Reddy", "Kavya Menon", 3.0, "Sale"),
            ("SYN-MUT-4002", d(2023, 6, 25), "Arjun Reddy", "Deepak Joshi", 3.5, "Sale"),
        ],
        "mortgages": [],
        "extra_events": [],
    },
    {
        "property_id": "PROP-005",
        "title": "Ownership chain gap",
        "loc": ("Mandya", "Maddur", "Koppa", "Lakshmipura"),
        "survey": "9/2", "hissa": "1A", "owner": "Pooja Hegde", "extent": 2.5,
        "registrations": [
            ("SYN-REG-5001", d(2023, 3, 8), "Sale Deed", "Pooja Hegde", "Ramesh Gowda", 2.5,
             2_750_000, "Survey No. 9/2, Hissa 1A, Lakshmipura village"),
            # Seller Sanjay Kulkarni never appears as an owner: Ramesh Gowda -> ??? -> Sanjay.
            ("SYN-REG-5002", d(2024, 9, 12), "Sale Deed", "Sanjay Kulkarni", "Lakshmi Bhat", 2.5,
             3_100_000, "Survey No. 9/2, Hissa 1A, Lakshmipura village"),
        ],
        "mutations": [
            ("SYN-MUT-5001", d(2023, 4, 12), "Pooja Hegde", "Ramesh Gowda", 2.5, "Sale"),
            ("SYN-MUT-5002", d(2024, 10, 20), "Sanjay Kulkarni", "Lakshmi Bhat", 2.5, "Sale"),
        ],
        "mortgages": [],
        "extra_events": [],
    },
    {
        "property_id": "PROP-006",
        "title": "Survey/hissa inconsistency",
        "loc": ("Hassan", "Arsikere", "Gandasi", "Ramanagara Kaval"),
        "survey": "49/1", "hissa": "2A", "owner": "Vikram Kumar", "extent": 2.0,
        "registrations": [
            ("SYN-REG-6001", d(2023, 5, 22), "Sale Deed", "Vikram Kumar", "Anita Rao", 2.0,
             2_600_000, "Survey No. 49/1, Hissa 2A, Ramanagara Kaval village"),
            # Later deed cites hissa 2B although the baseline record is hissa 2A.
            ("SYN-REG-6002", d(2025, 2, 10), "Sale Deed", "Anita Rao", "Deepak Joshi", 2.0,
             3_000_000, "Survey No. 49/1, Hissa 2B, Ramanagara Kaval village"),
        ],
        "mutations": [
            ("SYN-MUT-6001", d(2023, 6, 30), "Vikram Kumar", "Anita Rao", 2.0, "Sale"),
            ("SYN-MUT-6002", d(2025, 3, 18), "Anita Rao", "Deepak Joshi", 2.0, "Sale"),
        ],
        "mortgages": [],
        "extra_events": [
            {"event_type": EventType.SURVEY_CHANGED, "date": d(2025, 2, 10),
             "source_type": "registration", "source_id": "SYN-REG-6002",
             "description": "Survey reference in registered deed differs from baseline: "
                            "hissa 2A (baseline) vs hissa 2B (deed SYN-REG-6002).",
             "previous": {"survey_number": "49/1", "hissa": "2A"},
             "new": {"survey_number": "49/1", "hissa": "2B"}},
        ],
    },
    {
        "property_id": "PROP-007",
        "title": "Extent mismatch",
        "loc": ("Chikkaballapur", "Gauribidanur", "Manchenahalli", "Nagarjunapura"),
        "survey": "67/5", "hissa": "1", "owner": "Neha Patel", "extent": 5.0,
        "registrations": [
            ("SYN-REG-7001", d(2023, 9, 5), "Sale Deed", "Neha Patel", "Rahul Sharma", 5.0,
             6_000_000, "Survey No. 67/5, Hissa 1, Nagarjunapura village"),
        ],
        "mutations": [
            # Registered extent 5.0 acres, mutation entry records 5.8 acres.
            ("SYN-MUT-7001", d(2023, 10, 12), "Neha Patel", "Rahul Sharma", 5.8, "Sale"),
        ],
        "mortgages": [],
        "extra_events": [
            {"event_type": EventType.EXTENT_CHANGED, "date": d(2023, 10, 12),
             "source_type": "mutation", "source_id": "SYN-MUT-7001",
             "description": "Extent in revenue record (5.8 acres) differs from extent in "
                            "registered deed (5.0 acres).",
             "previous": {"extent_acres": 5.0}, "new": {"extent_acres": 5.8}},
        ],
    },
    {
        "property_id": "PROP-008",
        "title": "Normal multiple transactions",
        "loc": ("Kolar", "Malur", "Tekal", "Devarahalli Demo"),
        "survey": "156/2", "hissa": "1", "owner": "Meena Iyer", "extent": 8.0,
        "registrations": [
            ("SYN-REG-8001", d(2022, 6, 15), "Sale Deed", "Meena Iyer", "Arjun Reddy", 8.0,
             9_600_000, "Survey No. 156/2, Hissa 1, Devarahalli Demo village"),
            ("SYN-REG-8002", d(2025, 1, 22), "Sale Deed", "Arjun Reddy", "Kavya Menon", 8.0,
             12_000_000, "Survey No. 156/2, Hissa 1, Devarahalli Demo village"),
        ],
        "mutations": [
            ("SYN-MUT-8001", d(2022, 7, 20), "Meena Iyer", "Arjun Reddy", 8.0, "Sale"),
            ("SYN-MUT-8002", d(2025, 2, 28), "Arjun Reddy", "Kavya Menon", 8.0, "Sale"),
        ],
        "mortgages": [
            {"mortgage_id": "SYN-MTG-8001", "date": d(2023, 1, 18), "party": "Arjun Reddy",
             "institution": BANK_B, "amount": 3_000_000, "release_date": d(2024, 5, 30)},
        ],
        "extra_events": [],
    },
    {
        "property_id": "PROP-009",
        "title": "Mortgage -> sale -> inconsistent mutation",
        "loc": ("Belagavi", "Khanapur", "Nandagad", "Sundarapura"),
        "survey": "63/5", "hissa": "2", "owner": "Deepak Joshi", "extent": 4.5,
        "registrations": [
            # Sale happens while the mortgage is still active (no release recorded).
            ("SYN-REG-9001", d(2023, 10, 17), "Sale Deed", "Deepak Joshi", "Pooja Hegde", 4.5,
             5_400_000, "Survey No. 63/5, Hissa 2, Sundarapura village"),
        ],
        "mutations": [
            # Mutation names a previous owner who is neither the seller nor the mortgage party.
            ("SYN-MUT-9001", d(2024, 1, 15), "Dinesh Joshi", "Pooja Hegde", 4.5, "Sale"),
        ],
        "mortgages": [
            {"mortgage_id": "SYN-MTG-9001", "date": d(2023, 2, 8), "party": "Deepak Joshi",
             "institution": BANK_A, "amount": 2_500_000, "release_date": None},
        ],
        "extra_events": [],
    },
    {
        "property_id": "PROP-010",
        "title": "Multiple inconsistencies",
        "loc": ("Dharwad", "Kalghatgi", "Tadas", "Vidyanagara Demo"),
        "survey": "88/2", "hissa": "4A", "owner": "Rahul Sharma", "extent": 7.0,
        "registrations": [
            # (1) sold to Vikram Kumar while the mortgage below is still active
            ("SYN-REG-A001", d(2023, 7, 10), "Sale Deed", "Rahul Sharma", "Vikram Kumar", 7.0,
             9_100_000, "Survey No. 88/2, Hissa 4A, Vidyanagara Demo village"),
            # (3) seller Anita Rao never held title; (4) deed cites hissa 4B vs baseline 4A
            ("SYN-REG-A002", d(2024, 3, 5), "Sale Deed", "Anita Rao", "Deepak Joshi", 4.0,
             5_200_000, "Survey No. 88/2, Hissa 4B, Vidyanagara Demo village; 4.0 acres, northern portion"),
            # (5) overlaps A002 and together they exceed the 7.0 acres held
            ("SYN-REG-A003", d(2024, 4, 18), "Sale Deed", "Vikram Kumar", "Kavya Menon", 4.5,
             5_850_000, "Survey No. 88/2, Hissa 4A, Vidyanagara Demo village; 4.5 acres, northern and central portion"),
        ],
        "mutations": [
            # (2) buyer in deed is Vikram Kumar, mutation owner is Neha Patel
            ("SYN-MUT-A001", d(2023, 8, 14), "Rahul Sharma", "Neha Patel", 7.0, "Sale"),
            # (6) deed extent 4.5 acres vs mutation extent 5.6 acres
            ("SYN-MUT-A002", d(2024, 5, 22), "Vikram Kumar", "Kavya Menon", 5.6, "Sale"),
        ],
        "mortgages": [
            {"mortgage_id": "SYN-MTG-A001", "date": d(2023, 1, 12), "party": "Rahul Sharma",
             "institution": BANK_B, "amount": 4_000_000, "release_date": None},
        ],
        "extra_events": [
            {"event_type": EventType.SURVEY_CHANGED, "date": d(2024, 3, 5),
             "source_type": "registration", "source_id": "SYN-REG-A002",
             "description": "Survey reference in registered deed differs from baseline: "
                            "hissa 4A (baseline) vs hissa 4B (deed SYN-REG-A002).",
             "previous": {"survey_number": "88/2", "hissa": "4A"},
             "new": {"survey_number": "88/2", "hissa": "4B"}},
            {"event_type": EventType.EXTENT_CHANGED, "date": d(2024, 5, 22),
             "source_type": "mutation", "source_id": "SYN-MUT-A002",
             "description": "Extent in revenue record (5.6 acres) differs from extent in "
                            "registered deed (4.5 acres).",
             "previous": {"extent_acres": 4.5}, "new": {"extent_acres": 5.6}},
        ],
    },
]


# --------------------------------------------------------------------------------------
# Cleanup + build
# --------------------------------------------------------------------------------------
def clear_demo_dataset(db) -> None:
    """Remove ONLY PROP-001..PROP-010 and what hangs off them. Nothing else is touched."""
    # Demo events (is_demo=True) for the demo properties; evidence first to respect the FK.
    demo_event_ids = select(Event.id).where(
        Event.property_id.in_(DEMO_IDS), Event.is_demo.is_(True)
    )
    db.execute(delete(Evidence).where(Evidence.event_id.in_(demo_event_ids)))
    db.execute(delete(Event).where(Event.id.in_(demo_event_ids)))

    # Remaining children of the demo properties, then the properties themselves.
    for model in (Evidence, Event, RegistrationRecord, MutationRecord, MortgageRecord):
        db.execute(delete(model).where(model.property_id.in_(DEMO_IDS)))
    db.execute(delete(Property).where(Property.property_id.in_(DEMO_IDS)))
    db.flush()


def _events_for(sc: dict) -> list[dict]:
    """Derive one event per record, plus the scenario's extra events; sort chronologically."""
    pid = sc["property_id"]
    evts: list[dict] = []

    for doc_no, dt, doc_type, seller, buyer, extent, _val, _det in sc["registrations"]:
        evts.append({
            "event_type": EventType.SALE_REGISTERED, "date": dt,
            "source_type": "registration", "source_id": doc_no,
            "description": f"{doc_type} {doc_no} registered: {seller} to {buyer} ({extent} acres).",
            "previous": {"registered_owner": seller},
            "new": {"registered_owner": buyer, "extent_acres": extent},
        })

    for mut_no, dt, prev_owner, new_owner, extent, mut_type in sc["mutations"]:
        evts.append({
            "event_type": EventType.MUTATION_UPDATED, "date": dt,
            "source_type": "mutation", "source_id": mut_no,
            "description": f"Mutation {mut_no} ({mut_type}) recorded: {prev_owner} to {new_owner} ({extent} acres).",
            "previous": {"owner_name": prev_owner},
            "new": {"owner_name": new_owner, "extent_acres": extent},
        })

    for m in sc["mortgages"]:
        evts.append({
            "event_type": EventType.MORTGAGE_REGISTERED, "date": m["date"],
            "source_type": "mortgage", "source_id": m["mortgage_id"],
            "description": f"Mortgage {m['mortgage_id']} registered: {m['party']} with "
                           f"{m['institution']} (INR {m['amount']:,.0f}).",
            "previous": {"mortgage_status": "none"},
            "new": {"mortgage_status": "active", "institution": m["institution"]},
        })
        if m["release_date"]:
            evts.append({
                "event_type": EventType.MORTGAGE_RELEASED, "date": m["release_date"],
                "source_type": "mortgage", "source_id": m["mortgage_id"],
                "description": f"Mortgage {m['mortgage_id']} released by {m['institution']}.",
                "previous": {"mortgage_status": "active"},
                "new": {"mortgage_status": "released"},
            })

    for x in sc["extra_events"]:
        evts.append({
            "event_type": x["event_type"], "date": x["date"],
            "source_type": x["source_type"], "source_id": x["source_id"],
            "description": x["description"], "previous": x["previous"], "new": x["new"],
        })

    evts.sort(key=lambda e: e["date"])  # stable: same-day events keep insertion order
    for e in evts:
        e["property_id"] = pid
    return evts


def build_property(db, sc: dict) -> None:
    district, taluk, hobli, village = sc["loc"]
    db.add(Property(
        property_id=sc["property_id"], district=district, taluk=taluk, hobli=hobli,
        village=village, survey_number=sc["survey"], hissa=sc["hissa"],
        owner_name=sc["owner"], extent_acres=sc["extent"],
        mortgage_status="none", court_status="none", restriction_status="none",
        baseline_date=BASELINE,
    ))
    db.flush()  # property row must exist before children reference it

    for doc_no, dt, doc_type, seller, buyer, extent, value, details in sc["registrations"]:
        db.add(RegistrationRecord(
            property_id=sc["property_id"], document_number=doc_no, transaction_date=dt,
            document_type=doc_type, seller=seller, buyer=buyer, extent_acres=extent,
            market_value=value, property_details=details,
        ))
    for mut_no, dt, prev_owner, new_owner, extent, mut_type in sc["mutations"]:
        db.add(MutationRecord(
            property_id=sc["property_id"], mutation_number=mut_no, mutation_date=dt,
            previous_owner=prev_owner, new_owner=new_owner, extent_acres=extent,
            mutation_type=mut_type,
        ))
    for m in sc["mortgages"]:
        db.add(MortgageRecord(
            property_id=sc["property_id"], mortgage_id=m["mortgage_id"],
            mortgage_date=m["date"], party=m["party"], institution=m["institution"],
            amount=m["amount"], release_date=m["release_date"],
            status="released" if m["release_date"] else "active",
        ))
    for e in _events_for(sc):
        db.add(Event(
            property_id=e["property_id"], event_type=e["event_type"].value,
            event_date=e["date"], source_type=e["source_type"], source_id=e["source_id"],
            description=e["description"], previous_state=e["previous"],
            new_state=e["new"], is_demo=True,
        ))


def _count(db, model) -> int:
    return db.scalar(
        select(func.count()).select_from(model).where(model.property_id.in_(DEMO_IDS))
    )


def seed() -> None:
    Base.metadata.create_all(bind=engine)  # no-op if the tables already exist
    db = SessionLocal()
    try:
        clear_demo_dataset(db)
        for sc in SCENARIOS:
            build_property(db, sc)
        db.commit()

        print("LandShield synthetic dataset seeded successfully.\n")
        print(f"Properties: {_count(db, Property)}")
        print(f"Registrations: {_count(db, RegistrationRecord)}")
        print(f"Mutations: {_count(db, MutationRecord)}")
        print(f"Mortgages: {_count(db, MortgageRecord)}")
        print(f"Events: {_count(db, Event)}\n")
        print("Scenarios:")
        for sc in SCENARIOS:
            print(f"{sc['property_id']} - {sc['title']}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()