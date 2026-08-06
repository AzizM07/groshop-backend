# delivery/models.py — GROSHOP.tn
from django.db import models
from .carriers.base import ShipmentStatus
from .carriers.registry import available_carriers

# ⚠️ AJUSTE ces deux chemins vers TES modèles réels avant makemigrations :
SUPPLIER_MODEL = "users.SupplierProfile"   # d'après ton back
ORDER_MODEL    = "orders.SubOrder"         # la commande par fournisseur


class CarrierProvider(models.Model):
    """Transporteur au niveau PLATEFORME, configuré par l'admin GROSHOP.

    GROSHOP détient UN compte maître par transporteur : les identifiants API
    vivent ICI (pas chez le fournisseur). Le fournisseur ne fait qu'activer /
    choisir un transporteur `is_active`. Le service transporteur utilise ces
    credentials pour tous les appels API, quel que soit le fournisseur.
    """
    code           = models.CharField(max_length=40, unique=True,
                                       choices=available_carriers())
    name           = models.CharField(max_length=80)
    description    = models.CharField(max_length=255, blank=True)
    logo_url       = models.URLField(blank=True)
    base_url       = models.URLField(blank=True)
    # ⚠️ Compte maître GROSHOP — À CHIFFRER en prod (django-cryptography / Fernet,
    #    clé en variable d'env). write_only côté serializer : ne repart jamais en lecture.
    credentials    = models.JSONField(default=dict, blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)
    cod_supported  = models.BooleanField(default=True)
    is_active      = models.BooleanField(default=False)   # disponible sur la plateforme
    sort_order     = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "name")

    def __str__(self):
        return f"{self.name} ({self.code})"


class SupplierCarrierConfig(models.Model):
    """Un transporteur activé/choisi par un fournisseur.

    ⚠️ Depuis la décision « compte maître GROSHOP », le champ `credentials`
    n'est plus utilisé (les identifiants vivent dans CarrierProvider). On le
    garde nullable pour ne pas casser l'existant ; tu peux le retirer via une
    migration quand tu veux. Ce modèle ne sert plus qu'à mémoriser le choix /
    le transporteur par défaut d'un fournisseur.
    """
    supplier     = models.ForeignKey(SUPPLIER_MODEL, on_delete=models.CASCADE,
                                     related_name="carrier_configs")
    carrier_code = models.CharField(max_length=40, choices=available_carriers())
    is_active    = models.BooleanField(default=True)
    is_default   = models.BooleanField(default=False)
    # Déprécié (voir docstring) — conservé pour compat, ne rien y écrire de sensible.
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