from rest_framework import serializers
from .models import User, BuyerProfile, SupplierProfile, SupplierStore, Address


# ── Register Buyer ────────────────────────────────────────────────
class RegisterBuyerSerializer(serializers.ModelSerializer):

    password  = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['email', 'full_name', 'phone', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value.lower()

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Minimum 8 caractères.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email     = validated_data['email'],
            password  = validated_data['password'],
            full_name = validated_data['full_name'],
            phone     = validated_data.get('phone', ''),
            role      = 'buyer',
        )
        BuyerProfile.objects.create(user=user)
        return user


# ── Register Supplier ─────────────────────────────────────────────
class RegisterSupplierSerializer(serializers.ModelSerializer):

    password     = serializers.CharField(write_only=True, min_length=8)
    company_name = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['email', 'full_name', 'phone', 'password', 'company_name']

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value.lower()

    def create(self, validated_data):
        company_name = validated_data.pop('company_name')

        user = User.objects.create_user(
            email     = validated_data['email'],
            password  = validated_data['password'],
            full_name = validated_data['full_name'],
            phone     = validated_data.get('phone', ''),
            role      = 'supplier',
        )

        from django.utils.text import slugify
        base_slug = slugify(company_name)
        slug      = base_slug
        counter   = 1
        while SupplierProfile.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        SupplierProfile.objects.create(
            user         = user,
            company_name = company_name,
            slug         = slug,
        )
        return user


# ── User Info ─────────────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'phone', 'avatar_url', 'role', 'is_verified', 'created_at']


# ── Store (lecture) ───────────────────────────────────────────────
# Tous les champs de vitrine sont exposés → supplier_public ET supplier_me
# renvoient de quoi peindre la vitrine complète.
STORE_FIELDS = [
    'logo_url', 'banner_url', 'description',
    'founded_year', 'certifications',
    'page_views', 'response_rate', 'response_time_hrs',
    'hero_title', 'stats_title', 'stats_description',
    'highlight_image_1', 'highlight_image_2',
    'about_title_main', 'about_title_accent', 'about_image_url', 'about_images',
    'mission',
]


class SupplierStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SupplierStore
        fields = STORE_FIELDS


# ── Store (écriture — édition par le fournisseur connecté) ─────────
# page_views n'est PAS éditable (compteur serveur). Tout est optionnel
# (partial=True côté vue) → le fournisseur PATCH un champ à la fois.
class SupplierStoreWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SupplierStore
        fields = [
            'logo_url', 'banner_url', 'description',
            'founded_year', 'certifications',
            'response_rate', 'response_time_hrs',
            'hero_title', 'stats_title', 'stats_description',
            'highlight_image_1', 'highlight_image_2',
            'about_title_main', 'about_title_accent', 'about_image_url', 'about_images',
            'mission',
        ]

    def validate_about_images(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("about_images doit être une liste d'URLs.")
        return [str(v) for v in value if v]


class SupplierPublicSerializer(serializers.ModelSerializer):

    store          = SupplierStoreSerializer(read_only=True)
    total_products = serializers.SerializerMethodField()

    class Meta:
        model  = SupplierProfile
        fields = [
            'id', 'company_name', 'slug',
            'city', 'wilaya',
            'verification_status',
            'rating_avg', 'rating_count',
            'followers_count', 'created_at',
            'store', 'total_products',
        ]

    def get_total_products(self, obj):
        return obj.products.filter(status='approved').count()


# ══════════════════════════════════════════════════════════════════
# ADDRESS
# ══════════════════════════════════════════════════════════════════
class AddressSerializer(serializers.ModelSerializer):

    formatted = serializers.SerializerMethodField()

    class Meta:
        model  = Address
        fields = [
            'id', 'full_name', 'phone',
            'country', 'region', 'city', 'postal_code', 'street', 'additional',
            'is_default', 'created_at', 'updated_at', 'formatted',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'formatted']

    def get_formatted(self, obj):
        return obj.formatted()

    def validate(self, attrs):
        required_on_create = ['full_name', 'phone', 'region', 'city', 'postal_code', 'street']
        if self.instance is None:  # création
            missing = [f for f in required_on_create if not attrs.get(f)]
            if missing:
                raise serializers.ValidationError(
                    {f: 'Champ obligatoire.' for f in missing}
                )
        return attrs