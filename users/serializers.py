from rest_framework import serializers
from .models import User, BuyerProfile, SupplierProfile, SupplierStore

# ── Register Buyer ────────────────────────────────────────────────
class RegisterBuyerSerializer(serializers.ModelSerializer):

    password  = serializers.CharField(write_only=True, min_length=8)
    # write_only → le mot de passe ne revient JAMAIS dans la réponse

    class Meta:
        model  = User
        fields = ['email', 'full_name', 'phone', 'password']

    def validate_email(self, value):
        # Vérifie que l'email n'existe pas déjà
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value.lower()

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Minimum 8 caractères.')
        return value

    def create(self, validated_data):
        # Crée le user avec le mot de passe hashé
        user = User.objects.create_user(
            email     = validated_data['email'],
            password  = validated_data['password'],
            full_name = validated_data['full_name'],
            phone     = validated_data.get('phone', ''),
            role      = 'buyer',
        )
        # Crée le profil acheteur automatiquement
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

        # Génère un slug unique à partir du nom de l'entreprise
        import re
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
        # id, email... → retournés dans la réponse
        # password → jamais retourné car pas dans fields

class SupplierStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SupplierStore
        fields = [
            'logo_url', 'banner_url', 'description',
            'founded_year', 'certifications',
            'page_views', 'response_rate', 'response_time_hrs'
        ]


class SupplierPublicSerializer(serializers.ModelSerializer):

    store         = SupplierStoreSerializer(read_only=True)
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
        # rc_number, tax_number → pas inclus → privés

    def get_total_products(self, obj):
        return obj.products.filter(status='approved').count()