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

    class Meta:
        db_table = 'categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


# ── Product ───────────────────────────────────────────────────────
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
    sku            = models.CharField(max_length=100, blank=True)
    unit           = models.CharField(max_length=50, blank=True)
    moq            = models.IntegerField()
    base_price_tnd = models.DecimalField(max_digits=10, decimal_places=3)
    video_url      = models.TextField(blank=True)
    stock_qty      = models.IntegerField(default=0)
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
    old_price_tnd    = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    is_free_shipping = models.BooleanField(default=False)

    # ── NOUVEAUX CHAMPS ──────────────────────────────────────────
    brand      = models.CharField(max_length=100, blank=True, default='')
    reference  = models.CharField(max_length=100, blank=True, default='')  # code fabricant
    pack_size  = models.PositiveIntegerField(default=1)  # ex: vendu par lot de X unités
    specs_raw  = models.TextField(blank=True, default='')  # format libre "Clé: Valeur" par ligne
    shipping_price_tnd = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # prix livraison fixe, défini par le fournisseur
    delivery_days       = models.PositiveIntegerField(default=3)  # délai estimé en jours, modifiable en admin

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

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product   = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_tiers')
    min_qty   = models.IntegerField()
    max_qty   = models.IntegerField(null=True, blank=True)
    price_tnd = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        db_table = 'product_price_tiers'
        ordering = ['min_qty']

    def __str__(self):
        return f'{self.product.name} | {self.min_qty}-{self.max_qty} → {self.price_tnd} TND'


# ── ProductVariant (NOUVEAU) ──────────────────────────────────────
class ProductVariant(models.Model):
    """
    Variante simple d'un produit : juste un label + image optionnelle.
    Même prix/stock que le produit parent (pas de gestion individuelle
    par variante pour l'instant — phase 2 si besoin).
    """
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name        = models.CharField(max_length=50)   # ex: "Silver", "Noir", "M", "XL"
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

    # ── NOUVEAU CHAMP ────────────────────────────────────────────
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


# ── ReviewPhoto (NOUVEAU) ──────────────────────────────────────────
class ReviewPhoto(models.Model):
    """
    Photos jointes à un avis (plusieurs possibles par avis).
    """
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review     = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='photos')
    url        = models.TextField()
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'review_photos'
        ordering = ['sort_order']

    def __str__(self):
        return f'Photo {self.sort_order} → avis {self.review_id}'