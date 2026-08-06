# delivery/services.py — GROSHOP.tn
# Couche métier AGNOSTIQUE du transporteur. Le reste de l'app appelle ça.
from django.apps import apps
from django.utils.dateparse import parse_datetime
from .models import SupplierCarrierConfig, Shipment, ShipmentEvent, ORDER_MODEL
from .carriers.registry import get_carrier
from .carriers.base import Address, Parcel


def carrier_for_supplier(supplier, carrier_code=None):
    """Instance de transporteur configurée pour ce fournisseur.
    Aucune config → MockCarrier, pour que le flux marche DÈS MAINTENANT."""
    qs = SupplierCarrierConfig.objects.filter(supplier=supplier, is_active=True)
    cfg = (qs.filter(carrier_code=carrier_code).first() if carrier_code
           else (qs.filter(is_default=True).first() or qs.first()))
    if cfg is None:
        return get_carrier("mock", {})
    return get_carrier(cfg.carrier_code, cfg.credentials)


def _addr(d: dict) -> Address:
    d = d or {}
    return Address(
        name=d.get("name", ""), phone=d.get("phone", ""), line1=d.get("line1", ""),
        city=d.get("city", ""), governorate=d.get("governorate", ""),
        postal_code=d.get("postal_code", ""), email=d.get("email", ""),
    )


def _resolve_order(order_id):
    if not order_id:
        return None
    Model = apps.get_model(ORDER_MODEL)
    return Model.objects.filter(pk=order_id).first()


def create_shipment(*, supplier, order_id=None, origin, destination,
                    parcels=None, carrier_code=None, service="standard",
                    cod_amount_tnd=0.0) -> Shipment:
    carrier = carrier_for_supplier(supplier, carrier_code)
    order = _resolve_order(order_id)
    parcel_objs = [Parcel(**p) for p in (parcels or [{"weight_kg": 1.0}])]

    result = carrier.create_shipment(
        order_ref=str(order_id or ""),
        origin=_addr(origin), destination=_addr(destination),
        parcels=parcel_objs, service=service, cod_amount_tnd=float(cod_amount_tnd),
    )

    return Shipment.objects.create(
        order=order, supplier=supplier, carrier_code=carrier.code,
        tracking_number=result.tracking_number, status=result.status.value,
        service=service, cod_amount_tnd=cod_amount_tnd,
        label_url=result.label_url, raw=result.raw,
    )


def refresh_tracking(shipment: Shipment) -> Shipment:
    carrier = carrier_for_supplier(shipment.supplier, shipment.carrier_code)
    result = carrier.get_tracking(shipment.tracking_number)

    shipment.status = result.status.value
    shipment.save(update_fields=["status", "updated_at"])

    shipment.events.all().delete()
    ShipmentEvent.objects.bulk_create([
        ShipmentEvent(
            shipment=shipment, status=e.status.value, carrier_status=e.carrier_status,
            message=e.message, location=e.location,
            happened_at=parse_datetime(e.happened_at) if e.happened_at else None,
            raw=e.raw,
        ) for e in result.events
    ])
    return shipment


def apply_webhook(carrier_code, payload, headers=None):
    """Appelé par la vue webhook : met à jour le Shipment concerné.
    ⚠️ Vérifie la signature du transporteur AVANT d'appeler ceci."""
    carrier = get_carrier(carrier_code, {})
    result = carrier.parse_webhook(payload, headers)
    if not result:
        return None
    shipment = Shipment.objects.filter(
        carrier_code=carrier_code, tracking_number=result.tracking_number
    ).first()
    if not shipment:
        return None
    shipment.status = result.status.value
    shipment.save(update_fields=["status", "updated_at"])
    for e in result.events:
        ShipmentEvent.objects.create(
            shipment=shipment, status=e.status.value,
            carrier_status=e.carrier_status, message=e.message, raw=e.raw,
        )
    return shipment