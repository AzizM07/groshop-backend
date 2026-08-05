from rest_framework import serializers          # ← seulement s'il n'est pas déjà en haut du fichier
from .models import SubscriptionPlan, SupplierSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SubscriptionPlan
        fields = ['id', 'name', 'price_tnd', 'commission_pct', 'max_products', 'features', 'is_active']


class SupplierSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model  = SupplierSubscription
        fields = ['id', 'plan', 'status', 'started_at', 'expires_at', 'created_at']