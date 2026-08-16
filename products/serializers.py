from rest_framework import serializers
from django.utils.text import slugify
import uuid as _uuid

from .models import (
    Category, Product, ProductImage, ProductPriceTier,
    ProductShippingTier,
    ProductChoiceGroup, ProductVariant,
    ProductVariantCombo, ProductComboPriceTier,
    Review, ReviewPhoto,
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

# ── Category (#1) ─────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'icon_name', 'image_url',
                  'is_hot', 'is_new', 'sort_order', 'children', 'banner_url', 'banner_link']

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
        fields = ['id', 'min_qty', 'max_qty', 'price_tnd', 'old_price_tnd']


# ── ProductShippingTier ───────────────────────────────────────────
class ProductShippingTierSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductShippingTier
        fields = ['id', 'min_qty', 'price_tnd']


# ── ProductVariant ────────────────────────────────────────────────
class ProductVariantSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ProductVariant
        fields = ['id', 'name', 'image_url', 'sort_order']


# ── ProductChoiceGroup ────────────────────────────────────────────
class ProductChoiceGroupSerializer(serializers.ModelSerializer):

    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model  = ProductChoiceGroup
        fields = ['id', 'name', 'sort_order', 'variants']


# ── ProductComboPriceTier ─────────────────────────────────────────
class ProductComboPriceTierSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductComboPriceTier
        fields = ['id', 'min_qty', 'max_qty', 'price_tnd', 'old_price_tnd']


# ── ProductVariantCombo ───────────────────────────────────────────
class ProductVariantComboSerializer(serializers.ModelSerializer):
    variant_ids = serializers.SerializerMethodField()
    price_tiers = ProductComboPriceTierSerializer(many=True, read_only=True)

    class Meta:
        model  = ProductVariantCombo
        fields = ['id', 'variant_ids', 'price_tiers']

    def get_variant_ids(self, obj):
        # ⚡ .all() → cache du prefetch_related('variant_combos__variants'), 0 requête
        return [str(v.id) for v in obj.variants.all()]


# ── Product List (carte) ──────────────────────────────────────────
class ProductListSerializer(serializers.ModelSerializer):

    primary_image     = serializers.SerializerMethodField()
    images            = ProductImageSerializer(many=True, read_only=True)   # ← AJOUT
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
            'moq', 'unit', 'in_stock',                                      # ← in_stock
            'sold_count', 'rating_avg', 'rating_count',
            'badge_choice', 'badge_flash', 'badge_flash_end',
            'is_free_shipping',
            'primary_image', 'images',                                      # ← AJOUT
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


# ── Category (#2 — variante 'icon') ───────────────────────────────
# NOTE : redéfinition volontaire de CategorySerializer. En Python la 2e
# définition l'emporte au niveau module → c'est CELLE-CI qui sert partout.
# Laissée telle quelle pour ne rien changer au comportement existant.
class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()   # ← champ calculé pour le frontend

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'image_url', 'children', 'is_hot', 'is_new', 'sort_order']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data

    def get_icon(self, obj):
        """
        Retourne l'URL de l'image si disponible, sinon le nom de l'icône.
        Le frontend (CatIcon) saura les distinguer.
        """
        if obj.image_url:
            return obj.image_url
        return obj.icon_name or None


# ── Product Detail (page produit) ─────────────────────────────────
class ProductDetailSerializer(serializers.ModelSerializer):

    images         = ProductImageSerializer(many=True, read_only=True)
    price_tiers    = ProductPriceTierSerializer(many=True, read_only=True)
    shipping_tiers = ProductShippingTierSerializer(many=True, read_only=True)
    variants       = ProductVariantSerializer(many=True, read_only=True)
    choice_groups  = ProductChoiceGroupSerializer(many=True, read_only=True)
    variant_combos = ProductVariantComboSerializer(many=True, read_only=True)
    specs          = serializers.SerializerMethodField()
    is_favorited   = serializers.SerializerMethodField()

    # ── Champs du fournisseur (plats) ──
    supplier_name         = serializers.CharField(source='supplier.company_name', read_only=True, default='')
    supplier_slug         = serializers.CharField(source='supplier.slug', read_only=True, default='')
    supplier_city         = serializers.CharField(source='supplier.city', read_only=True, default='')
    supplier_wilaya       = serializers.CharField(source='supplier.wilaya', read_only=True, default='')
    supplier_verified     = serializers.CharField(source='supplier.verification_status', read_only=True, default='pending')
    supplier_rating       = serializers.DecimalField(source='supplier.rating_avg', max_digits=3, decimal_places=2, read_only=True, default=0)
    supplier_rating_count = serializers.IntegerField(source='supplier.rating_count', read_only=True, default=0)

    # ── Logo et bannière (avec fallback si store n'existe pas) ──
    supplier_logo   = serializers.SerializerMethodField()
    supplier_banner = serializers.SerializerMethodField()

    category_id   = serializers.IntegerField(source='category.id',   read_only=True, allow_null=True, default=None)  # ⭐ AJOUTÉ
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True, default=None)
    category_slug = serializers.CharField(source='category.slug', read_only=True, allow_null=True, default=None)

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'slug', 'description', 'sku', 'unit',
            'moq', 'base_price_tnd', 'old_price_tnd', 'video_url',
            'in_stock', 'sold_count', 'view_count',
            'rating_avg', 'rating_count',
            'status', 'badge_choice', 'badge_flash', 'badge_flash_end',
            'created_at',
            'brand', 'reference', 'pack_size',
            'shipping_mode', 'shipping_price_tnd', 'shipping_block_size',
            'shipping_block_price', 'shipping_tiers', 'delivery_days',
            'images', 'price_tiers', 'variants', 'choice_groups', 'variant_combos', 'specs',
            'supplier_name', 'supplier_slug', 'supplier_logo', 'supplier_banner',
            'supplier_rating', 'supplier_rating_count',
            'supplier_city', 'supplier_wilaya', 'supplier_verified',
            'category_id', 'category_name', 'category_slug',   # ⭐ category_id AJOUTÉ ici
            'is_favorited',
        ]

    def get_specs(self, obj):
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
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=request.user).exists()

    # ── Méthodes pour le logo / bannière ──
    def _get_store(self, obj):
        if obj.supplier_id:
            return getattr(obj.supplier, 'store', None)
        return None

    def get_supplier_logo(self, obj):
        store = self._get_store(obj)
        return (store.logo_url or '') if store else ''

    def get_supplier_banner(self, obj):
        store = self._get_store(obj)
        return (store.banner_url or '') if store else ''
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
    old_price_tnd = serializers.DecimalField(max_digits=10, decimal_places=3,
                                             required=False, allow_null=True)

    class Meta:
        model  = ProductPriceTier
        fields = ['min_qty', 'price_tnd', 'old_price_tnd']   # max_qty calculé serveur


class _ShippingTierWrite(serializers.ModelSerializer):
    class Meta:
        model  = ProductShippingTier
        fields = ['min_qty', 'price_tnd']


class _ImageWrite(serializers.ModelSerializer):
    class Meta:
        model  = ProductImage
        fields = ['url', 'is_primary', 'sort_order']


class _VariantWrite(serializers.ModelSerializer):
    class Meta:
        model  = ProductVariant
        fields = ['name', 'image_url', 'sort_order']


class _ChoiceGroupWrite(serializers.ModelSerializer):
    variants = _VariantWrite(many=True, required=False)

    class Meta:
        model  = ProductChoiceGroup
        fields = ['name', 'sort_order', 'variants']


class _ComboPriceTierWrite(serializers.ModelSerializer):
    old_price_tnd = serializers.DecimalField(max_digits=10, decimal_places=3,
                                             required=False, allow_null=True)

    class Meta:
        model  = ProductComboPriceTier
        fields = ['min_qty', 'price_tnd', 'old_price_tnd']   # max_qty calculé serveur


class _ComboSelectionWrite(serializers.Serializer):
    group   = serializers.CharField(max_length=50)
    variant = serializers.CharField(max_length=50)


class _VariantComboWrite(serializers.Serializer):
    selections  = _ComboSelectionWrite(many=True)
    price_tiers = _ComboPriceTierWrite(many=True)


class ProductCreateSerializer(serializers.ModelSerializer):
    images         = _ImageWrite(many=True, required=False)
    price_tiers    = _TierWrite(many=True)
    shipping_tiers = _ShippingTierWrite(many=True, required=False)
    choice_groups  = _ChoiceGroupWrite(many=True, required=False)
    variant_combos = _VariantComboWrite(many=True, required=False)   # ← AJOUT

    class Meta:
        model  = Product
        fields = [
            'id', 'category', 'name', 'description', 'unit',
            'brand', 'reference', 'specs_raw', 'video_url', 'video_poster_url',
            'in_stock', 'delivery_days',
            'shipping_mode', 'shipping_price_tnd',
            'shipping_block_size', 'shipping_block_price',
            'status', 'images', 'price_tiers', 'shipping_tiers', 'choice_groups', 'variant_combos',
        ]
        read_only_fields = ['id']
        # base_price_tnd, old_price_tnd, moq, is_free_shipping : dérivés dans create()

    def validate_status(self, value):
        if value not in ('draft', 'pending_review'):
            raise serializers.ValidationError("Statut non autorisé.")
        return value

    def validate_choice_groups(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 groupes de choix par produit.")
        return value

    def validate_price_tiers(self, value):
        if not value:
            raise serializers.ValidationError("Ajoute au moins une tranche de prix.")
        tiers = sorted(value, key=lambda t: t['min_qty'])
        prev_q = prev_p = None
        for t in tiers:
            q, p = t['min_qty'], t['price_tnd']
            if q < 1:
                raise serializers.ValidationError("La quantité de départ doit être ≥ 1.")
            if prev_q is not None and q <= prev_q:
                raise serializers.ValidationError("Les quantités de départ doivent être strictement croissantes.")
            if prev_p is not None and p >= prev_p:
                raise serializers.ValidationError("Le prix doit diminuer quand la quantité augmente.")
            op = t.get('old_price_tnd')
            if op is not None and op <= p:
                raise serializers.ValidationError("L'ancien prix (solde) doit être supérieur au prix de la tranche.")
            prev_q, prev_p = q, p
        return tiers

    def validate(self, data):
        mode = data.get('shipping_mode', 'flat')
        if mode == 'tiered':
            st = data.get('shipping_tiers') or []
            if not st:
                raise serializers.ValidationError({'shipping_tiers': "Ajoute au moins une tranche de livraison."})
            prev = None
            for t in sorted(st, key=lambda x: x['min_qty']):
                if t['min_qty'] < 1:
                    raise serializers.ValidationError({'shipping_tiers': "Quantité de départ ≥ 1."})
                if prev is not None and t['min_qty'] <= prev:
                    raise serializers.ValidationError({'shipping_tiers': "Quantités strictement croissantes."})
                prev = t['min_qty']
        if mode == 'per_block' and (not data.get('shipping_block_size') or not data.get('shipping_block_price')):
            raise serializers.ValidationError({'shipping_block_price': "Renseigne le palier et le frais par palier."})
        return data

    def _unique_slug(self, name):
        base = slugify(name)[:340] or 'produit'
        slug = base
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base}-{_uuid.uuid4().hex[:6]}"
        return slug

    def create(self, validated_data):
        images     = validated_data.pop('images', [])
        tiers      = validated_data.pop('price_tiers', [])
        ship_tiers = validated_data.pop('shipping_tiers', [])
        groups     = validated_data.pop('choice_groups', [])
        combos     = validated_data.pop('variant_combos', [])   # ← AJOUT

        tiers = sorted(tiers, key=lambda t: t['min_qty'])
        # Bornes hautes auto : jusqu'à (tranche suivante − 1), dernière = ouverte (null)
        for i, t in enumerate(tiers):
            t['max_qty'] = (tiers[i + 1]['min_qty'] - 1) if i + 1 < len(tiers) else None

        first = tiers[0]
        mode  = validated_data.get('shipping_mode', 'flat')
        validated_data['base_price_tnd']   = first['price_tnd']
        validated_data['old_price_tnd']    = first.get('old_price_tnd')   # solde 1re tranche → barré carte
        validated_data['moq']              = first['min_qty']
        validated_data['is_free_shipping'] = (mode == 'free')

        validated_data['supplier'] = self.context['request'].user.supplier_profile
        validated_data['slug']     = self._unique_slug(validated_data['name'])
        product = Product.objects.create(**validated_data)

        if images and not any(i.get('is_primary') for i in images):
            images[0]['is_primary'] = True
        ProductImage.objects.bulk_create([ProductImage(product=product, **i) for i in images])
        ProductPriceTier.objects.bulk_create([ProductPriceTier(product=product, **t) for t in tiers])

        if mode == 'tiered':
            ProductShippingTier.objects.bulk_create([
                ProductShippingTier(product=product, **t)
                for t in sorted(ship_tiers, key=lambda x: x['min_qty'])
            ])

        # ── Groupes + variantes, avec lookup (nom_groupe, nom_variante) → instance ──
        variant_lookup = {}
        for gi, g in enumerate(groups):
            variants = g.pop('variants', [])
            group = ProductChoiceGroup.objects.create(
                product=product, name=g['name'], sort_order=g.get('sort_order', gi),
            )
            created_variants = ProductVariant.objects.bulk_create([
                ProductVariant(product=product, group=group, **v) for v in variants
            ])
            for v in created_variants:
                variant_lookup[(g['name'], v.name)] = v

        # ── Prix par combinaison de variantes (optionnel) ──────────────
        for c in combos:
            selections  = c.get('selections') or []
            combo_tiers = c.get('price_tiers') or []
            if not selections or not combo_tiers:
                continue

            variant_instances = [
                variant_lookup[(s['group'], s['variant'])]
                for s in selections
                if (s['group'], s['variant']) in variant_lookup
            ]
            if len(variant_instances) != len(selections):
                continue  # sélection incomplète/invalide → ignorée silencieusement

            combo_tiers = sorted(combo_tiers, key=lambda t: t['min_qty'])
            for i, t in enumerate(combo_tiers):
                t['max_qty'] = (combo_tiers[i + 1]['min_qty'] - 1) if i + 1 < len(combo_tiers) else None

            combo_key = '|'.join(sorted(str(v.id) for v in variant_instances))
            combo = ProductVariantCombo.objects.create(product=product, combo_key=combo_key)
            combo.variants.set(variant_instances)
            ProductComboPriceTier.objects.bulk_create([
                ProductComboPriceTier(combo=combo, **t) for t in combo_tiers
            ])

        return product


# ── Liste fournisseur (page "Mes produits") ───────────────────────
class SupplierProductSerializer(serializers.ModelSerializer):

    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True,
                                          allow_null=True, default=None)

    class Meta:
        model  = Product
        fields = ['id', 'name', 'slug', 'base_price_tnd', 'old_price_tnd',
                  'moq', 'unit', 'stock_qty', 'in_stock', 'sold_count',   # ← in_stock ajouté
                  'rating_avg', 'rating_count', 'status',
                  'is_free_shipping', 'category_name', 'primary_image', 'created_at']

    def get_primary_image(self, obj):
        return _primary_image_url(obj)