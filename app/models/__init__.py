"""Import every model here so Base.metadata knows about all six tables."""
from .property import Property
from .registration import RegistrationRecord
from .mutation import MutationRecord
from .mortgage import MortgageRecord
from .event import Event
from .evidence import Evidence

__all__ = [
    "Property",
    "RegistrationRecord",
    "MutationRecord",
    "MortgageRecord",
    "Event",
    "Evidence",
]
