# delivery/carriers/base.py — GROSHOP.tn
# Contrat commun à TOUS les transporteurs. Ton code métier ne parle qu'à ça.
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ShipmentStatus(str, Enum):
    """Statuts INTERNES normalisés (chaque transporteur mappe les siens dessus)."""
    PENDING          = "pending"
    CONFIRMED        = "confirmed"
    PICKED_UP        = "picked_up"
    IN_TRANSIT       = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED        = "delivered"
    FAILED           = "failed"
    RETURNED         = "returned"
    CANCELLED        = "cancelled"

    @classmethod
    def choices(cls):
        return [(s.value, s.name.replace("_", " ").title()) for s in cls]


# ── DTOs échangés avec les transporteurs (indépendants de Django) ──
@dataclass
class Address:
    name: str = ""
    phone: str = ""
    line1: str = ""
    city: str = ""
    governorate: str = ""     # wilaya
    postal_code: str = ""
    country: str = "TN"
    email: str = ""

@dataclass
class Parcel:
    weight_kg: float = 1.0
    length_cm: float = 0
    width_cm: float = 0
    height_cm: float = 0
    description: str = ""
    value_tnd: float = 0

@dataclass
class RateQuote:
    carrier_code: str
    service: str
    amount_tnd: float
    currency: str = "TND"
    eta_days: Optional[int] = None
    raw: dict = field(default_factory=dict)

@dataclass
class ShipmentResult:
    tracking_number: str
    status: ShipmentStatus = ShipmentStatus.CONFIRMED
    label_url: str = ""
    amount_tnd: Optional[float] = None
    raw: dict = field(default_factory=dict)

@dataclass
class TrackingEvent:
    status: ShipmentStatus
    carrier_status: str = ""
    message: str = ""
    location: str = ""
    happened_at: Optional[str] = None   # ISO 8601
    raw: dict = field(default_factory=dict)

@dataclass
class TrackingResult:
    tracking_number: str
    status: ShipmentStatus
    events: list = field(default_factory=list)   # list[TrackingEvent]
    raw: dict = field(default_factory=dict)


class CarrierError(Exception): ...
class CarrierConfigError(CarrierError): ...
class CarrierAPIError(CarrierError): ...


class BaseCarrier(ABC):
    code: str = ""          # identifiant court, ex. "first_delivery"
    label: str = ""         # nom affiché, ex. "First Delivery"
    STATUS_MAP: dict = {}   # {statut transporteur -> ShipmentStatus}

    def __init__(self, config: Optional[dict] = None):
        # config = identifiants API du fournisseur (clé, secret, id compte…)
        self.config = config or {}

    def require(self, *keys):
        missing = [k for k in keys if not self.config.get(k)]
        if missing:
            raise CarrierConfigError(
                f"{self.label}: identifiants manquants: {', '.join(missing)}"
            )

    def normalize_status(self, carrier_status: str) -> ShipmentStatus:
        return self.STATUS_MAP.get(
            (carrier_status or "").lower().strip(), ShipmentStatus.IN_TRANSIT
        )

    # ── à implémenter par chaque transporteur ──
    @abstractmethod
    def get_rates(self, origin: Address, destination: Address, parcels: list) -> list: ...

    @abstractmethod
    def create_shipment(self, *, order_ref: str, origin: Address, destination: Address,
                        parcels: list, service: str = "",
                        cod_amount_tnd: float = 0.0) -> ShipmentResult: ...

    @abstractmethod
    def get_tracking(self, tracking_number: str) -> TrackingResult: ...

    # ── optionnels : surcharge si le transporteur le gère ──
    def cancel_shipment(self, tracking_number: str) -> bool:
        raise NotImplementedError(f"{self.label}: annulation non supportée")

    def parse_webhook(self, payload: dict, headers: Optional[dict] = None) -> Optional[TrackingResult]:
        raise NotImplementedError(f"{self.label}: webhooks non supportés")