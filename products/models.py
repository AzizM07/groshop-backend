from django.db import models
import uuid

# ── Category ──────────────────────────────────────────────────────
class Category(models.Model):

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent     = models.ForeignKey(
                    'self',
                    on_delete=models.SET_NULL,
                    null=True, blank=True,
                    related_name='children'
                 )
    name       = models.CharField(max_length=150)
    slug       = models.SlugField(max_length=200, unique=True)
    icon_name  = models.CharField(max_length=100, blank=True)
    image_url  = models.TextField(blank=True)
    is_hot     = models.BooleanField(default=False)
    is_new     = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    is_active  = models.BooleanField(default=True)
    banner_url  = models.TextField(blank=True, default='')
    banner_link = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        db_table = 'categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


# ── Product ───────────────────────────────────────────────────────
SHIPPING_MODES = [
    ('free',      'Gratuite'),
    ('flat',      'Fixe'),
    ('tiered',    'Par tranche de quantité'),
    ('per_block', 'Par palier'),
]

class Product(models.Model):

    STATUS = [
        ('draft',          'Brouillon'),
        ('pending_review', 'En attente de validation'),
        ('approved',       'Approuvé'),
        ('rejected',       'Rejeté'),
    ]

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier       = models.ForeignKey('users.SupplierProfile', on_delete=models.CASCADE, related_name='products')
    category       = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name           = models.CharField(max_length=300)
    slug           = models.SlugField(max_length=350, unique=True)
    description    = models.TextField(blank=True)
    sku            = models.CharField(max_length=100, blank=True)   # legacy — plus alimenté par le form
    unit           = models.CharField(max_length=50, blank=True)
    moq            = models.IntegerField()                          # auto = 1re tranche
    base_price_tnd = models.DecimalField(max_digits=10, decimal_places=3)  # auto = prix 1re tranche
    video_url      = models.TextField(blank=True)
    stock_qty      = models.IntegerField(default=0)                 # legacy
    in_stock       = models.BooleanField(default=True)             # ← nouveau : dispo on/off
    sold_count     = models.IntegerField(default=0)
    view_count     = models.IntegerField(default=0)
    rating_avg     = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count   = models.IntegerField(default=0)
    status         = models.CharField(max_length=20, choices=STATUS, default='draft')
    badge_choice   = models.BooleanField(default=False)
    badge_flash    = models.BooleanField(default=False)
    badge_flash_end= models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    old_price_tnd    = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)  # auto = solde 1re tranche
    is_free_shipping = models.BooleanField(default=False)           # dérivé de shipping_mode == 'free'
    video_url         = models.TextField(blank=True)
    video_poster_url  = models.TextField(blank=True, default='')   # ← miniature générée au transcodage
    brand      = models.CharField(max_length=100, blank=True, default='')
    reference  = models.CharField(max_length=100, blank=True, default='')  # code fabricant
    pack_size  = models.PositiveIntegerField(default=1)            # legacy — plus dans le form
    specs_raw  = models.TextField(blank=True, default='')

    # ── Livraison ──
    shipping_mode        = models.CharField(max_length=12, choices=SHIPPING_MODES, default='flat')
    shipping_price_tnd   = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # mode 'flat'
    shipping_block_size  = models.PositiveIntegerField(default=10)                          # mode 'per_block' : tous les N articles
    shipping_block_price = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # mode 'per_block' : + M DT par palier
    delivery_days        = models.PositiveIntegerField(default=3)

    class Meta:
        db_table = 'products'
        indexes  = [
            models.Index(fields=['supplier']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['sold_count']),
        ]

    def __str__(self):
        return self.name


# ── ProductImage ──────────────────────────────────────────────────
class ProductImage(models.Model):

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    url        = models.TextField()
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'product_images'
        ordering = ['sort_order']

    def __str__(self):
        return f'Image {self.sort_order} → {self.product.name}'


# ── ProductPriceTier ──────────────────────────────────────────────
class ProductPriceTier(models.Model):

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product       = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_tiers')
    min_qty       = models.IntegerField()
    max_qty       = models.IntegerField(null=True, blank=True)      # calculé serveur (borne suivante-1, dernière = null)
    price_tnd     = models.DecimalField(max_digits=10, decimal_places=3)
    old_price_tnd = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)  # ← solde par tranche

    class Meta:
        db_table = 'product_price_tiers'
        ordering = ['min_qty']

    def __str__(self):
        return f'{self.product.name} | {self.min_qty}-{self.max_qty} → {self.price_tnd} TND'


# ── ProductShippingTier (NOUVEAU) ─────────────────────────────────
class ProductShippingTier(models.Model):
    """Frais de livraison par tranche de quantité (mode 'tiered')."""
    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product   = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shipping_tiers')
    min_qty   = models.IntegerField()
    price_tnd = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        db_table = 'product_shipping_tiers'
        ordering = ['min_qty']

    def __str__(self):
        return f'{self.product.name} | {self.min_qty}+ → {self.price_tnd} TND livraison'


# ── ProductChoiceGroup ────────────────────────────────────────────
class ProductChoiceGroup(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='choice_groups')
    name       = models.CharField(max_length=50)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'product_choice_groups'
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.product.name} — {self.name}'


# ── ProductVariant ────────────────────────────────────────────────
class ProductVariant(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    group       = models.ForeignKey(
        ProductChoiceGroup, on_delete=models.CASCADE,
        related_name='variants', null=True, blank=True,
    )
    name        = models.CharField(max_length=50)
    image_url   = models.TextField(blank=True)
    sort_order  = models.IntegerField(default=0)

    class Meta:
        db_table = 'product_variants'
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.product.name} — {self.name}'


# ── Review ────────────────────────────────────────────────────────
class Review(models.Model):

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reviewer   = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    product    = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    supplier   = models.ForeignKey('users.SupplierProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    order      = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, related_name='reviews')
    rating     = models.SmallIntegerField()
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    variant    = models.ForeignKey(
        ProductVariant, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviews_for_variant'
    )

    class Meta:
        db_table = 'reviews'
        constraints = [
            models.UniqueConstraint(fields=['reviewer', 'product'],  name='unique_review_product'),
            models.UniqueConstraint(fields=['reviewer', 'supplier'], name='unique_review_supplier'),
        ]

    def __str__(self):
        return f'{self.rating}★'


# ── ReviewPhoto ────────────────────────────────────────────────────
class ReviewPhoto(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review     = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='photos')
    url        = models.TextField()
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'review_photos'
        ordering = ['sort_order']

    def __str__(self):
        return f'Photo {self.sort_order} → avis {self.review_id}'


# ── Favorite ───────────────────────────────────────────────────────
class Favorite(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='favorites')
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_favorite_user_product'),
        ]
        indexes = [
            models.Index(fields=['user', 'product']),
        ]

    def __str__(self):
        return f'{self.user_id} ♥ {self.product_id}'