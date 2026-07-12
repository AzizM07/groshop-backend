# orders/models.py
from django.db import models
import uuid
from users.models import User, SupplierProfile
from products.models import Product, ProductVariant


# ══════════════════════════════════════════════════════════════════
# ORDER
# ══════════════════════════════════════════════════════════════════
class Order(models.Model):

    STATUS = [
        ('pending',          'En attente'),
        ('call_confirmed',   'Confirmée par appel'),
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
    shipping_address = models.TextField()
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Commande {self.id} — {self.buyer.full_name}'


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

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'


# ══════════════════════════════════════════════════════════════════
# CART ITEM
# ══════════════════════════════════════════════════════════════════
class CartItem(models.Model):

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer      = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    related_name='cart_items')
    product    = models.ForeignKey(
                    Product,
                    on_delete=models.CASCADE,
                    related_name='in_carts')
    variant    = models.ForeignKey(
                    ProductVariant,
                    on_delete=models.CASCADE,
                    null=True, blank=True,
                    related_name='in_carts')
    quantity   = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'cart_items'
        ordering        = ['-created_at']   # ← avant: '-updated_at'
        unique_together = ('buyer', 'product', 'variant')

    def __str__(self):
        return f'{self.buyer.email} — {self.product.name} x{self.quantity}'

    @property
    def unit_price(self):
        """Prix unitaire selon les paliers de prix (price_tiers)."""
        tier = self.product.price_tiers.filter(
            min_qty__lte=self.quantity
        ).order_by('-min_qty').first()
        return tier.price_tnd if tier else self.product.base_price_tnd

    @property
    def total_price(self):
        return self.unit_price * self.quantity