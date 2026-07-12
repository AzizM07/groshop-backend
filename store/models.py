from django.db import models
import uuid


# ── Wishlist ──────────────────────────────────────────────────────
class Wishlist(models.Model):

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wishlists')
    product    = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True, related_name='wishlisted_by')
    supplier   = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlists'
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'],  name='unique_wishlist_product'),
            models.UniqueConstraint(fields=['user', 'supplier'], name='unique_wishlist_supplier'),
        ]

    def __str__(self):
        return f'{self.user.full_name} → favori'


# ── Quote ─────────────────────────────────────────────────────────
class Quote(models.Model):

    STATUS = [
        ('pending',  'En attente'),
        ('quoted',   'Devis envoyé'),
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='quotes')
    supplier    = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE, related_name='quotes')
    product     = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')
    quantity    = models.IntegerField()
    message     = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS, default='pending')
    quote_tnd   = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quotes'

    def __str__(self):
        return f'Devis {self.buyer.full_name} → {self.supplier.company_name}'


# ── SearchHistory ─────────────────────────────────────────────────
class SearchHistory(models.Model):

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user         = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='search_history')
    query        = models.CharField(max_length=300)
    result_count = models.IntegerField(default=0)
    searched_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_history'
        indexes  = [
            models.Index(fields=['user', 'searched_at']),
        ]

    def __str__(self):
        return f'{self.user.full_name} → "{self.query}"'


# ── ProductInteraction ────────────────────────────────────────────
class ProductInteraction(models.Model):

    EVENTS = [
        ('view',         'Vue'),
        ('click',        'Clic'),
        ('add_to_cart',  'Ajout panier'),
        ('purchase',     'Achat'),
    ]

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='interactions')
    product    = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='interactions')
    event_type = models.CharField(max_length=20, choices=EVENTS)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_interactions'
        indexes  = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['product', 'event_type']),
        ]

    def __str__(self):
        return f'{self.user.full_name} → {self.event_type} → {self.product.name}'


# ── Banner ────────────────────────────────────────────────────────
class Banner(models.Model):

    SLOTS = [
        ('hero_1',    'Hero principal 1'),
        ('hero_2',    'Hero principal 2'),
        ('sidebar',   'Sidebar'),
        ('mega_menu', 'Mega menu'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier    = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE, related_name='banners')
    image_url   = models.TextField()
    link_url    = models.TextField(blank=True)
    slot        = models.CharField(max_length=30, choices=SLOTS)
    starts_at   = models.DateTimeField(null=True, blank=True)
    ends_at     = models.DateTimeField(null=True, blank=True)
    price_tnd   = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    impressions = models.IntegerField(default=0)
    clicks      = models.IntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'banners'

    def __str__(self):
        return f'Banner {self.slot} → {self.supplier.company_name}'


# ── SupplierDocument ──────────────────────────────────────────────
class SupplierDocument(models.Model):

    DOC_TYPES = [
        ('rne',     'Registre National des Entreprises'),
        ('patente', 'Patente'),
        ('id_card', 'Carte d\'identité'),
        ('other',   'Autre'),
    ]

    STATUS = [
        ('pending',  'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier    = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE, related_name='documents')
    doc_type    = models.CharField(max_length=50, choices=DOC_TYPES)
    file_url    = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'supplier_documents'

    def __str__(self):
        return f'{self.doc_type} → {self.supplier.company_name}'


# ── SubscriptionPlan ──────────────────────────────────────────────
class SubscriptionPlan(models.Model):

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name           = models.CharField(max_length=100)
    # ex: Basic, Pro, Premium
    price_tnd      = models.DecimalField(max_digits=10, decimal_places=3)
    commission_pct = models.DecimalField(max_digits=5, decimal_places=2)
    # ex: 10.00 = 10%
    max_products   = models.IntegerField(null=True, blank=True)
    # null = illimité
    features       = models.JSONField(default=dict, blank=True)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscription_plans'

    def __str__(self):
        return f'{self.name} → {self.price_tnd} TND/mois'


# ── SupplierSubscription ──────────────────────────────────────────
class SupplierSubscription(models.Model):

    STATUS = [
        ('active',    'Actif'),
        ('expired',   'Expiré'),
        ('cancelled', 'Annulé'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier    = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE, related_name='subscriptions')
    plan        = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status      = models.CharField(max_length=20, choices=STATUS, default='active')
    started_at  = models.DateTimeField()
    expires_at  = models.DateTimeField(null=True, blank=True)
    changed_by  = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='subscription_changes')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'supplier_subscriptions'

    def __str__(self):
        return f'{self.supplier.company_name} → {self.plan.name}'


# ── Commission ────────────────────────────────────────────────────
class Commission(models.Model):

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_order        = models.OneToOneField('orders.SubOrder', on_delete=models.CASCADE, related_name='commission')
    supplier         = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE, related_name='commissions')
    commission_pct   = models.DecimalField(max_digits=5, decimal_places=2)
    subtotal_tnd     = models.DecimalField(max_digits=12, decimal_places=3)
    commission_tnd   = models.DecimalField(max_digits=12, decimal_places=3)
    supplier_net_tnd = models.DecimalField(max_digits=12, decimal_places=3)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'commissions'

    def __str__(self):
        return f'Commission {self.commission_pct}% → {self.commission_tnd} TND'