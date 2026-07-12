from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductPriceTier, ProductVariant, Review, ReviewPhoto


# ── Category ──────────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'icon_name', 'image_url',
                  'is_hot', 'is_new', 'sort_order', 'children']

    def get_children(self, obj):
        # Retourne les sous-catégories
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


# ── ProductVariant (NOUVEAU) ──────────────────────────────────────
class ProductVariantSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ProductVariant
        fields = ['id', 'name', 'image_url', 'sort_order']


# ── Product List (carte) ──────────────────────────────────────────
class ProductListSerializer(serializers.ModelSerializer):

    primary_image = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_slug = serializers.CharField(source='supplier.slug', read_only=True)
    supplier_verified = serializers.CharField(source='supplier.verification_status', read_only=True)
    supplier_medals  = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    years_active  = serializers.SerializerMethodField()
    price_tiers   = ProductPriceTierSerializer(many=True, read_only=True)

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
        image = obj.images.filter(is_primary=True).first()
        if not image:
            image = obj.images.first()
        return image.url if image else None

    def get_years_active(self, obj):
        from datetime import date
        store = getattr(obj.supplier, 'store', None)
        if store and store.founded_year:
            return date.today().year - store.founded_year
        return None

    def get_supplier_medals(self, obj):
        rating = obj.supplier.rating_avg
        if rating is None:
            return 0
        return round(float(rating))


# ── Product Detail (page produit) ────────────────────────────────
class ProductDetailSerializer(serializers.ModelSerializer):
    # Version complète pour la page détail

    images      = ProductImageSerializer(many=True, read_only=True)
    price_tiers = ProductPriceTierSerializer(many=True, read_only=True)
    variants    = ProductVariantSerializer(many=True, read_only=True)
    specs       = serializers.SerializerMethodField()  # ← AJOUTE ÇA

    supplier_name         = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_slug         = serializers.CharField(source='supplier.slug', read_only=True)
    supplier_logo         = serializers.CharField(source='supplier.store.logo_url', read_only=True)
    supplier_banner       = serializers.CharField(source='supplier.store.banner_url', read_only=True)  # ← AJOUTE ÇA
    supplier_rating       = serializers.DecimalField(source='supplier.rating_avg', max_digits=3, decimal_places=2, read_only=True)
    supplier_rating_count = serializers.IntegerField(source='supplier.rating_count', read_only=True)
    supplier_city         = serializers.CharField(source='supplier.city', read_only=True)
    supplier_wilaya       = serializers.CharField(source='supplier.wilaya', read_only=True)  # ← AJOUTE ÇA
    supplier_verified     = serializers.CharField(source='supplier.verification_status', read_only=True)

    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

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
            'shipping_price_tnd', 'delivery_days',  # ← AJOUTE ÇA
            'images', 'price_tiers', 'variants', 'specs',
            'supplier_name', 'supplier_slug', 'supplier_logo', 'supplier_banner',  # ← AJOUTE supplier_banner
            'supplier_rating', 'supplier_rating_count',
            'supplier_city', 'supplier_wilaya', 'supplier_verified',  # ← AJOUTE supplier_wilaya
            'category_name', 'category_slug',
        ]

    def get_specs(self, obj):
        """
        Parse specs_raw (format "Clé: Valeur" une par ligne)
        en liste de dicts [{k, v}, ...] pour le frontend.
        Ignore les lignes vides ou mal formées (sans ':').
        """
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


# ── Review ────────────────────────────────────────────────────────
class ReviewPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ReviewPhoto
        fields = ['id', 'url', 'sort_order']


class ReviewSerializer(serializers.ModelSerializer):

    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    variant_name  = serializers.CharField(source='variant.name', read_only=True)
    photos        = ReviewPhotoSerializer(many=True, read_only=True)  # ← AJOUTE ÇA

    class Meta:
        model  = Review
        fields = ['id', 'reviewer_name', 'rating', 'comment', 'created_at', 'variant_name', 'photos']