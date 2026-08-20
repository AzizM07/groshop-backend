from django.db import models, transaction
import uuid
from datetime import datetime
from users.models import User, SupplierProfile, Address
from products.models import Product, ProductVariant


# ══════════════════════════════════════════════════════════════════
# ORDER
# ══════════════════════════════════════════════════════════════════
class Order(models.Model):
    STATUS = [
        ('pending',          'En attente'),
        ('confirmed',        'Confirmée'),
        ('in_production',    'En production'),
        ('shipped',          'Expédiée'),
        ('delivered',        'Livrée'),
        ('cancelled',        'Annulée'),
    ]

    PAYMENT_STATUS = [
        ('unpaid',   'Non payée'),
        ('paid',     'Payée'),
        ('refunded', 'Remboursée'),
    ]

    PAYMENT_METHODS = [
        ('cod',      'Paiement à la livraison'),
        ('d17',      'D17'),
        ('flouci',   'Flouci'),
        ('sobflous', 'Sobflous'),
        ('virement', 'Virement bancaire'),
    ]

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer            = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    status           = models.CharField(max_length=30, choices=STATUS, default='pending')
    payment_status   = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_method   = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True)
    total_tnd        = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    discount_tnd     = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    reference = models.CharField(max_length=20, unique=True, blank=True, null=True)

    shipping_address     = models.TextField()
    shipping_address_ref = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders',
    )
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference:
            with transaction.atomic():
                year = datetime.now().year
                last = (
                    Order.objects
                    .select_for_update()
                    .filter(reference__startswith=f'ORD-{year}-')
                    .order_by('reference')
                    .last()
                )
                if last:
                    num = int(last.reference.split('-')[-1]) + 1
                else:
                    num = 1
                self.reference = f'ORD-{year}-{num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Commande {self.reference} — {self.buyer.full_name}'


# ══════════════════════════════════════════════════════════════════
# SUB-ORDER
# ══════════════════════════════════════════════════════════════════
class SubOrder(models.Model):
    STATUS = [
        ('pending',       'En attente'),
        ('confirmed',     'Confirmée'),
        ('in_production', 'En production'),
        ('shipped',       'Expédiée'),
        ('delivered',     'Livrée'),
        ('cancelled',     'Annulée'),
    ]

    DELIVERY_TYPES = [
        ('groshop',     'Livraison GROSHOP'),
        ('supplier',    'Livraison fournisseur'),
        ('third_party', 'Transporteur tiers'),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order         = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sub_orders')
    supplier      = models.ForeignKey(SupplierProfile, on_delete=models.PROTECT, related_name='sub_orders')
    status        = models.CharField(max_length=30, choices=STATUS, default='pending')
    subtotal_tnd  = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES, default='groshop')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sub_orders'

    def __str__(self):
        return f'Sous-commande {self.id} — {self.supplier.company_name}'


# ══════════════════════════════════════════════════════════════════
# ORDER ITEM
# ══════════════════════════════════════════════════════════════════
class OrderItem(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_order      = models.ForeignKey(SubOrder, on_delete=models.CASCADE, related_name='items')
    product        = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity       = models.IntegerField()
    unit_price_tnd = models.DecimalField(max_digits=10, decimal_places=3)
    total_tnd      = models.DecimalField(max_digits=12, decimal_places=3)

    # ── Personnalisation (snapshot au moment de la commande) ──
    is_customized         = models.BooleanField(default=False)
    customization_values  = models.JSONField(
        default=list, blank=True,
        help_text="Snapshot des valeurs saisies : [{field_id, label, field_type, value}]",
    )
    customization_request = models.ForeignKey(
        'CustomizationRequest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='order_items',
    )

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'


# ══════════════════════════════════════════════════════════════════
# CART ITEM
# ══════════════════════════════════════════════════════════════════
class CartItem(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    guest_id   = models.UUIDField(null=True, blank=True, db_index=True)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_carts')
    variant    = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='in_carts')
    quantity   = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── Personnalisation ──
    is_customized         = models.BooleanField(default=False)
    customization_values  = models.JSONField(
        default=list, blank=True,
        help_text="Valeurs saisies par l'acheteur : [{field_id, label, field_type, value}]",
    )
    customization_request = models.ForeignKey(
        'CustomizationRequest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cart_items',
        help_text="Rempli uniquement pour les items issus d'un devis accepté (mode quote).",
    )

    class Meta:
        db_table = 'cart_items'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(buyer__isnull=False, guest_id__isnull=True) |
                    models.Q(buyer__isnull=True,  guest_id__isnull=False)
                ),
                name='cart_owner_xor',
            ),
            # ⭐ Unicité : ne s'applique PAS aux items personnalisés
            # (chaque perso est distincte, même produit/variante).
            models.UniqueConstraint(
                fields=['buyer', 'product', 'variant'],
                name='uniq_cart_user',
                condition=models.Q(buyer__isnull=False) & models.Q(is_customized=False),
            ),
            models.UniqueConstraint(
                fields=['guest_id', 'product', 'variant'],
                name='uniq_cart_guest',
                condition=models.Q(guest_id__isnull=False) & models.Q(is_customized=False),
            ),
        ]

    def __str__(self):
        owner = self.buyer.email if self.buyer else f'guest:{self.guest_id}'
        return f'{owner} — {self.product.name} x{self.quantity}'

    @property
    def unit_price(self):
        """
        Résolution du prix unitaire :
        - Mode 'quote' + item customisé → prix verrouillé du CustomizationRequest
        - Mode 'fixed' + item customisé → tier(qty) + surcoût perso
        - Sinon → tier(qty) standard
        """
        p = self.product
        tier = p.price_tiers.filter(min_qty__lte=self.quantity).order_by('-min_qty').first()
        base = tier.price_tnd if tier else p.base_price_tnd

        if self.is_customized:
            if p.customization_mode == 'quote' and self.customization_request:
                return self.customization_request.quoted_price_tnd or base
            if p.customization_mode == 'fixed':
                return base + p.customization_extra_price_tnd

        return base

    @property
    def total_price(self):
        return self.unit_price * self.quantity


# ══════════════════════════════════════════════════════════════════
# CUSTOMIZATION REQUEST (devis pour perso mode 'quote')
# ══════════════════════════════════════════════════════════════════
class CustomizationRequest(models.Model):
    """
    Demande de devis pour un produit personnalisable en mode 'quote'.
    L'acheteur remplit les champs, le fournisseur voit la demande dans
    la messagerie et répond avec un prix. À l'acceptation, un CartItem
    est créé avec le prix verrouillé.
    """
    STATUS = [
        ('pending',  'En attente de devis'),
        ('quoted',   'Devis envoyé'),
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé'),
        ('expired',  'Expiré'),
    ]

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customization_requests')
    product           = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customization_requests')
    variant           = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='+',
    )
    quantity          = models.PositiveIntegerField(default=1)
    values            = models.JSONField(
        default=list, blank=True,
        help_text="Valeurs saisies : [{field_id, label, field_type, value}]",
    )
    status            = models.CharField(max_length=20, choices=STATUS, default='pending')
    quoted_price_tnd  = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    quoted_at         = models.DateTimeField(null=True, blank=True)
    expires_at        = models.DateTimeField(null=True, blank=True)
    supplier_note     = models.TextField(blank=True, default='',
                        help_text="Message optionnel du fournisseur avec le devis")
    conversation      = models.ForeignKey(
        'messaging.Conversation',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='customization_requests',
    )
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customization_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['product', 'status']),
            models.Index(fields=['conversation']),
        ]

    def __str__(self):
        return f'Devis {self.id} — {self.get_status_display()}'

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at is not None and self.expires_at < timezone.now()