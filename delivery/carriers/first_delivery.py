# delivery/carriers/first_delivery.py — GROSHOP.tn
#
# GABARIT pour un VRAI transporteur. Recette pour en ajouter un :
#   1. Copie ce fichier (aramex.py, colilog.py, rapid_poste.py, intigo.py…)
#   2. Renomme la classe + code + label
#   3. Remplis STATUS_MAP avec les libellés RÉELS de leur API
#   4. Implémente get_rates / create_shipment / get_tracking
#   5. Ajoute la classe dans carriers/registry.py
# Rien d'autre à toucher dans le reste de l'app.
#
# import requests   # décommente quand tu brancheras les appels HTTP
from .base import (BaseCarrier, ShipmentResult, TrackingResult, ShipmentStatus)


class FirstDeliveryCarrier(BaseCarrier):
    code = "first_delivery"
    label = "First Delivery"

    BASE_URL = "https://api.first-delivery.tn"   # ← à confirmer avec leur doc

    STATUS_MAP = {
        "created":          ShipmentStatus.CONFIRMED,
        "picked_up":        ShipmentStatus.PICKED_UP,
        "in_transit":       ShipmentStatus.IN_TRANSIT,
        "out_for_delivery": ShipmentStatus.OUT_FOR_DELIVERY,
        "delivered":        ShipmentStatus.DELIVERED,
        "returned":         ShipmentStatus.RETURNED,
        "cancelled":        ShipmentStatus.CANCELLED,
    }

    def _headers(self):
        self.require("api_key")
        return {"Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"}

    def get_rates(self, origin, destination, parcels):
        # TODO: r = requests.post(f"{self.BASE_URL}/rates", json=..., headers=self._headers())
        #       return [RateQuote(self.code, x["service"], x["price"]) for x in r.json()]
        raise NotImplementedError("First Delivery: get_rates à implémenter")

    def create_shipment(self, *, order_ref, origin, destination, parcels,
                        service="", cod_amount_tnd=0.0):
        # TODO: r = requests.post(f"{self.BASE_URL}/shipments", json={...}, headers=self._headers())
        #       data = r.json()
        #       return ShipmentResult(tracking_number=data["tracking"], label_url=data["label"], raw=data)
        raise NotImplementedError("First Delivery: create_shipment à implémenter")

    def get_tracking(self, tracking_number):
        # TODO: r = requests.get(f"{self.BASE_URL}/tracking/{tracking_number}", headers=self._headers())
        #       data = r.json()
        #       status = self.normalize_status(data["status"])
        #       events = [TrackingEvent(self.normalize_status(e["status"]), ...) for e in data["events"]]
        #       return TrackingResult(tracking_number, status, events, raw=data)
        raise NotImplementedError("First Delivery: get_tracking à implémenter")

    # cancel_shipment / parse_webhook : surcharge si l'API les fournit.