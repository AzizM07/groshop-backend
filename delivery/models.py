# delivery/models.py — GROSHOP.tn
from django.db import models
from .carriers.base import ShipmentStatus
from .carriers.registry import available_carriers

# ⚠️ AJUSTE ces deux chemins vers TES modèles réels avant makemigrations :
SUPPLIER_MODEL = "users.SupplierProfile"   # d'après ton back
ORDER_MODEL    = "orders.SubOrder"         # la commande par fournisseur


class SupplierCarrierConfig(models.Model):
    """Un transporteur activé par un fournisseur, avec ses identifiants API."""
    supplier     = models.ForeignKey(SUPPLIER_MODEL, on_delete=models.CASCADE,
                                     related_name="carrier_configs")
    carrier_code = models.CharField(max_length=40, choices=available_carriers())
    is_active    = models.BooleanField(default=True)
    is_default   = models.BooleanField(default=False)
    # ⚠️ Identifiants API en clair ici — à chiffrer en prod (django-cryptography
    #    ou champ dérivé d'une variable d'env). Ne jamais renvoyer en lecture API.
    credentials  = models.JSONField(default=dict, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("supplier", "carrier_code")

    def __str__(self):
        return f"{self.supplier_id} · {self.carrier_code}"


class Shipment(models.Model):
    order           = models.ForeignKey(ORDER_MODEL, on_delete=models.CASCADE,
                                        related_name="shipments", null=True, blank=True)
    supplier        = models.ForeignKey(SUPPLIER_MODEL, on_delete=models.CASCADE,
                                        related_name="shipments")
    carrier_code    = models.CharField(max_length=40)
    tracking_number = models.CharField(max_length=120, blank=True, db_index=True)
    status          = models.CharField(max_length=20, choices=ShipmentStatus.choices(),
                                       default=ShipmentStatus.PENDING.value)
    service         = models.CharField(max_length=40, blank=True)
    cod_amount_tnd  = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    label_url       = models.URLField(blank=True)
    raw             = models.JSONField(default=dict, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.carrier_code}:{self.tracking_number or '—'} ({self.status})"


class ShipmentEvent(models.Model):
    shipment       = models.ForeignKey(Shipment, on_delete=models.CASCADE,
                                       related_name="events")
    status         = models.CharField(max_length=20, choices=ShipmentStatus.choices())
    carrier_status = models.CharField(max_length=80, blank=True)
    message        = models.CharField(max_length=255, blank=True)
    location       = models.CharField(max_length=120, blank=True)
    happened_at    = models.DateTimeField(null=True, blank=True)
    raw            = models.JSONField(default=dict, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("happened_at", "created_at")