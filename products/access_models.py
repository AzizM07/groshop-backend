# products/access_models.py — GROSHOP.tn
# Modèles pour le contrôle d'accès aux prix masqués.
# ─ SupplierUserUnlock  : le fournisseur donne à un user l'accès à TOUT son catalogue
# ─ ProductPriceUnlock  : le fournisseur donne à un user l'accès à UN produit précis
#
# Logique de visibilité (dans products/serializers.py) :
#   voir prix si :
#     product.price_visibility == 'public'
#     OU user.business_status == 'verified'
#     OU SupplierUserUnlock(supplier=product.supplier, user=user, actif) existe
#     OU ProductPriceUnlock(product=product, user=user, actif) existe

import uuid
from django.db import models
from django.utils import timezone
from users.models import User, SupplierProfile
from .models import Product


def _is_active(unlock):
    """Un unlock est actif s'il n'est pas révoqué et pas expiré."""
    if unlock.revoked_at:
        return False
    if unlock.expires_at and unlock.expires_at <= timezone.now():
        return False
    return True


class SupplierUserUnlock(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier   = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='user_unlocks')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplier_unlocks')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='null = permanent')
    revoked_at = models.DateTimeField(null=True, blank=True)
    note       = models.TextField(blank=True)

    class Meta:
        db_table = 'supplier_user_unlocks'
        constraints = [
            models.UniqueConstraint(fields=['supplier', 'user'], name='uniq_supplier_user_unlock'),
        ]
        indexes = [
            models.Index(fields=['user', 'supplier']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.supplier.company_name} → {self.user.full_name}'

    @property
    def is_active(self):
        return _is_active(self)


class ProductPriceUnlock(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_unlocks')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_unlocks')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='null = permanent')
    revoked_at = models.DateTimeField(null=True, blank=True)
    note       = models.TextField(blank=True)

    class Meta:
        db_table = 'product_price_unlocks'
        constraints = [
            models.UniqueConstraint(fields=['product', 'user'], name='uniq_product_price_unlock'),
        ]
        indexes = [
            models.Index(fields=['user', 'product']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.product.name} → {self.user.full_name}'

    @property
    def is_active(self):
        return _is_active(self)


def can_see_price(user, product):
    """
    Fonction utilitaire centrale : renvoie True si `user` peut voir le prix
    de `product`. Utilisée par les serializers ET les views.
    """
    # Prix public → toujours visible
    if product.price_visibility == 'public':
        return True

    # Non authentifié → jamais accès aux prix masqués
    if not user or not user.is_authenticated:
        return False

    # Le fournisseur voit toujours ses propres prix
    if user.role == 'supplier' and product.supplier_id == getattr(user, 'id', None):
        return True

    # Boutique vérifiée par GROSHOP → accès universel
    if getattr(user, 'business_status', 'none') == 'verified':
        return True

    # Unlock catalogue complet
    now = timezone.now()
    has_supplier_unlock = SupplierUserUnlock.objects.filter(
        supplier_id=product.supplier_id,
        user_id=user.id,
        revoked_at__isnull=True,
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
    ).exists()
    if has_supplier_unlock:
        return True

    # Unlock produit spécifique
    has_product_unlock = ProductPriceUnlock.objects.filter(
        product_id=product.id,
        user_id=user.id,
        revoked_at__isnull=True,
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
    ).exists()
    return has_product_unlock