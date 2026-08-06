# delivery/carriers/registry.py — GROSHOP.tn
# Le seul endroit où l'on déclare les transporteurs disponibles.
from .base import BaseCarrier, CarrierConfigError
from .mock import MockCarrier
from .first_delivery import FirstDeliveryCarrier

_CARRIERS = {
    MockCarrier.code:          MockCarrier,
    FirstDeliveryCarrier.code: FirstDeliveryCarrier,
    # AramexCarrier.code:      AramexCarrier,   # ← ajoute tes transporteurs ici
}


def available_carriers():
    """Liste (code, label) — pour un menu déroulant côté fournisseur."""
    return [(c.code, c.label) for c in _CARRIERS.values()]


def get_carrier(code: str, config: dict | None = None) -> BaseCarrier:
    cls = _CARRIERS.get(code)
    if cls is None:
        raise CarrierConfigError(f"Transporteur inconnu: {code}")
    return cls(config or {})


def register(cls):
    """Décorateur optionnel : @register au-dessus d'une classe transporteur."""
    _CARRIERS[cls.code] = cls
    return cls