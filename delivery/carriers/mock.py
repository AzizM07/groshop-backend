# delivery/carriers/mock.py — GROSHOP.tn
# Transporteur FACTICE. Permet de développer/tester tout le flux TOUT DE SUITE,
# sans aucune vraie API ni requête réseau. C'est le transporteur par défaut
# tant qu'un fournisseur n'a pas configuré un vrai transporteur.
import random
import string
from datetime import datetime, timezone, timedelta
from .base import (BaseCarrier, RateQuote, ShipmentResult, TrackingResult,
                   TrackingEvent, ShipmentStatus)


class MockCarrier(BaseCarrier):
    code = "mock"
    label = "Transporteur (démo)"

    def get_rates(self, origin, destination, parcels):
        weight = sum(p.weight_kg for p in parcels) or 1
        base = 7.0 + 0.5 * max(weight - 1, 0)
        return [
            RateQuote(self.code, "standard", round(base, 3), eta_days=3),
            RateQuote(self.code, "express",  round(base * 1.8, 3), eta_days=1),
        ]

    def create_shipment(self, *, order_ref, origin, destination, parcels,
                        service="standard", cod_amount_tnd=0.0):
        tn = "MOCK" + "".join(random.choices(string.digits, k=9))
        return ShipmentResult(
            tracking_number=tn,
            status=ShipmentStatus.CONFIRMED,
            label_url=f"https://example.test/labels/{tn}.pdf",
            amount_tnd=self.get_rates(origin, destination, parcels)[0].amount_tnd,
            raw={"order_ref": order_ref, "service": service, "cod": cod_amount_tnd},
        )

    def get_tracking(self, tracking_number):
        now = datetime.now(timezone.utc)
        steps = [
            (ShipmentStatus.CONFIRMED,        "Commande enregistrée",   4),
            (ShipmentStatus.PICKED_UP,        "Colis récupéré",         3),
            (ShipmentStatus.IN_TRANSIT,       "En transit",             2),
            (ShipmentStatus.OUT_FOR_DELIVERY, "En cours de livraison",  1),
            (ShipmentStatus.DELIVERED,        "Livré",                  0),
        ]
        events = [
            TrackingEvent(status=s, message=m,
                          happened_at=(now - timedelta(days=d)).isoformat())
            for s, m, d in steps
        ]
        return TrackingResult(tracking_number=tracking_number,
                              status=steps[-1][0], events=events)

    def cancel_shipment(self, tracking_number):
        return True

    def parse_webhook(self, payload, headers=None):
        payload = payload or {}
        status = self.normalize_status(payload.get("status", ""))
        return TrackingResult(
            tracking_number=payload.get("tracking_number", ""),
            status=status,
            events=[TrackingEvent(status=status, message=payload.get("message", ""))],
            raw=payload,
        )