from rest_framework import serializers
from django.utils.text import slugify
import uuid as _uuid

from .models import (
    Category, Product, ProductImage, ProductPriceTier,
    ProductVariant, Review, ReviewPhoto,
)


# ── Helper partagé : image primaire sans requête SQL ───────────────
def _primary_image_url(product):
    """
    ⚡ .all() → utilise le cache du prefetch_related('images') (0 requête).
       .filter(is_primary=True) relancerait une requête par produit → N+1.
    """
    images = product.images.all()
    for img in images:
        if img.is_primary:
            return img.url
    return images[0].url if images else None


# ══════════════════════════════════════════════════════════════════
#  LECTURE
# ══════════════════════════════════════════════════════════════════

# ── Category ──────────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'icon_name', 'image_url',
                  'is_hot', 'is_new', 'sort_order', 'children']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data


# ── ProductImage ──────────────────────────────────────────────────
class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ProductImage
        fields = ['id', 'url', 'is_primary', 'sort_order']


# ── ProductPriceTier ──────────────────────────────────────────────
class ProductPriceTierSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ProductPriceTier
        fields = ['id', 'min_qty', 'max_qty', 'price_tnd']


# ── ProductVariant ────────────────────────────────────────────────
class ProductVariantSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ProductVariant
        fields = ['id', 'name', 'image_url', 'sort_order']


# ── Product List (carte) ──────────────────────────────────────────
class ProductListSerializer(serializers.ModelSerializer):

    primary_image     = serializers.SerializerMethodField()
    supplier_name     = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_slug     = serializers.CharField(source='supplier.slug', read_only=True)
    supplier_verified = serializers.CharField(source='supplier.verification_status', read_only=True)
    supplier_medals   = serializers.SerializerMethodField()
    category_name     = serializers.CharField(source='category.name', read_only=True,
                                              allow_null=True, default=None)
    years_active      = serializers.SerializerMethodField()
    price_tiers       = ProductPriceTierSerializer(many=True, read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'slug',
            'base_price_tnd', 'old_price_tnd',
            'moq', 'unit',
            'sold_count', 'rating_avg', 'rating_count',
            'badge_choice', 'badge_flash', 'badge_flash_end',
            'is_free_shipping',
            'primary_image',
            'supplier_name', 'supplier_slug', 'supplier_verified', 'supplier_medals',
            'category_name',
            'years_active',
            'price_tiers',
        ]

    def get_primary_image(self, obj):
        return _primary_image_url(obj)

    def get_years_active(self, obj):
        from datetime import date
        # ⚠️ nécessite select_related('supplier__store') dans la vue, sinon 1 requête/produit
        store = getattr(obj.supplier, 'store', None)
        if store and store.founded_year:
            return date.today().year - store.founded_year
        return None

    def get_supplier_medals(self, obj):
        rating = obj.supplier.rating_avg
        if rating is None:
            return 0
        return round(float(rating))


# ── Product Detail (page produit) ─────────────────────────────────
class ProductDetailSerializer(serializers.ModelSerializer):

    images      = ProductImageSerializer(many=True, read_only=True)
    price_tiers = ProductPriceTierSerializer(many=True, read_only=True)
    variants    = ProductVariantSerializer(many=True, read_only=True)
    specs       = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()   # ← NOUVEAU (cœur wishlist)

    supplier_name         = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_slug         = serializers.CharField(source='supplier.slug', read_only=True)
    supplier_logo         = serializers.CharField(source='supplier.store.logo_url', read_only=True)
    supplier_banner       = serializers.CharField(source='supplier.store.banner_url', read_only=True)
    supplier_rating       = serializers.DecimalField(source='supplier.rating_avg', max_digits=3, decimal_places=2, read_only=True)
    supplier_rating_count = serializers.IntegerField(source='supplier.rating_count', read_only=True)
    supplier_city         = serializers.CharField(source='supplier.city', read_only=True)
    supplier_wilaya       = serializers.CharField(source='supplier.wilaya', read_only=True)
    supplier_verified     = serializers.CharField(source='supplier.verification_status', read_only=True)

    category_name = serializers.CharField(source='category.name', read_only=True,
                                          allow_null=True, default=None)
    category_slug = serializers.CharField(source='category.slug', read_only=True,
                                          allow_null=True, default=None)

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'slug', 'description', 'sku', 'unit',
            'moq', 'base_price_tnd', 'old_price_tnd', 'video_url',
            'stock_qty', 'sold_count', 'view_count',
            'rating_avg', 'rating_count',
            'status', 'badge_choice', 'badge_flash', 'badge_flash_end',
            'created_at',
            'brand', 'reference', 'pack_size',
            'shipping_price_tnd', 'delivery_days',
            'images', 'price_tiers', 'variants', 'specs',
            'supplier_name', 'supplier_slug', 'supplier_logo', 'supplier_banner',
            'supplier_rating', 'supplier_rating_count',
            'supplier_city', 'supplier_wilaya', 'supplier_verified',
            'category_name', 'category_slug',
            'is_favorited',                                  # ← NOUVEAU
        ]

    def get_specs(self, obj):
        """Parse specs_raw ("Clé: Valeur" par ligne) → [{k, v}, ...]."""
        if not obj.specs_raw:
            return []
        result = []
        for line in obj.specs_raw.splitlines():
            line = line.strip()
            if not line or ':' not in line:
                continue
            key, _, value = line.partition(':')
            key, value = key.strip(), value.strip()
            if key and value:
                result.append({'k': key, 'v': value})
        return result

    def get_is_favorited(self, obj):
        """True si l'utilisateur connecté a ce produit en favori."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=request.user).exists()


# ── Review ────────────────────────────────────────────────────────
class ReviewPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ReviewPhoto
        fields = ['id', 'url', 'sort_order']


class ReviewSerializer(serializers.ModelSerializer):

    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    variant_name  = serializers.CharField(source='variant.name', read_only=True,
                                          allow_null=True, default=None)
    photos        = ReviewPhotoSerializer(many=True, read_only=True)

    class Meta:
        model  = Review
        fields = ['id', 'reviewer_name', 'rating', 'comment', 'created_at', 'variant_name', 'photos']

class ReviewCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    rating     = serializers.IntegerField(min_value=1, max_value=5)
    comment    = serializers.CharField(required=False, allow_blank=True, default='')
    order_id   = serializers.UUIDField(required=False, allow_null=True)
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    photos     = serializers.ListField(
        child=serializers.URLField(), required=False, default=list
    )
# ══════════════════════════════════════════════════════════════════
#  ÉCRITURE (création produit fournisseur)
# ══════════════════════════════════════════════════════════════════

class _TierWrite(serializers.ModelSerializer):
    class Meta:
        model  = ProductPriceTier
        fields = ['min_qty', 'max_qty', 'price_tnd']


class _VariantWrite(serializers.ModelSerializer):
    class Meta:
        model  = ProductVariant
        fields = ['name', 'image_url', 'sort_order']


class _ImageWrite(serializers.ModelSerializer):
    class Meta:
        model  = ProductImage
        fields = ['url', 'is_primary', 'sort_order']


class ProductCreateSerializer(serializers.ModelSerializer):
    images      = _ImageWrite(many=True, required=False)
    price_tiers = _TierWrite(many=True, required=False)
    variants    = _VariantWrite(many=True, required=False)

    class Meta:
        model  = Product
        fields = [
            'id', 'category', 'name', 'description', 'sku', 'unit',
            'moq', 'base_price_tnd', 'old_price_tnd', 'video_url',
            'stock_qty', 'brand', 'reference', 'pack_size', 'specs_raw',
            'shipping_price_tnd', 'delivery_days', 'is_free_shipping',
            'status', 'images', 'price_tiers', 'variants',
        ]
        read_only_fields = ['id']

    def validate_status(self, value):
        # Un fournisseur ne peut créer qu'en brouillon ou soumettre pour validation
        if value not in ('draft', 'pending_review'):
            raise serializers.ValidationError("Statut non autorisé.")
        return value

    def _unique_slug(self, name):
        base = slugify(name)[:340] or 'produit'
        slug = base
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base}-{_uuid.uuid4().hex[:6]}"
        return slug

    def create(self, validated_data):
        images   = validated_data.pop('images', [])
        tiers    = validated_data.pop('price_tiers', [])
        variants = validated_data.pop('variants', [])

        validated_data['supplier'] = self.context['request'].user.supplier_profile
        validated_data['slug']     = self._unique_slug(validated_data['name'])
        product = Product.objects.create(**validated_data)

        # garantit une image primaire
        if images and not any(i.get('is_primary') for i in images):
            images[0]['is_primary'] = True

        ProductImage.objects.bulk_create([ProductImage(product=product, **i) for i in images])
        ProductPriceTier.objects.bulk_create([ProductPriceTier(product=product, **t) for t in tiers])
        ProductVariant.objects.bulk_create([ProductVariant(product=product, **v) for v in variants])
        return product


# ── Liste fournisseur (page "Mes produits") ───────────────────────
class SupplierProductSerializer(serializers.ModelSerializer):

    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True,
                                          allow_null=True, default=None)

    class Meta:
        model  = Product
        fields = ['id', 'name', 'slug', 'base_price_tnd', 'old_price_tnd',
                  'moq', 'unit', 'stock_qty', 'sold_count',
                  'rating_avg', 'rating_count', 'status',
                  'is_free_shipping', 'category_name', 'primary_image', 'created_at']

    def get_primary_image(self, obj):
        return _primary_image_url(obj)