# delivery/serializers.py — GROSHOP.tn
from rest_framework import serializers
from .models import CarrierProvider, SupplierCarrierConfig, Shipment, ShipmentEvent


class CarrierProviderSerializer(serializers.ModelSerializer):
    """Admin GROSHOP. Les secrets ne repartent JAMAIS en lecture :
    on expose seulement `has_credentials` / `has_webhook_secret` (booléens)."""
    credentials        = serializers.JSONField(write_only=True, required=False)
    webhook_secret     = serializers.CharField(write_only=True, required=False, allow_blank=True)
    has_credentials    = serializers.SerializerMethodField()
    has_webhook_secret = serializers.SerializerMethodField()

    class Meta:
        model = CarrierProvider
        fields = ["id", "code", "name", "description", "logo_url", "base_url",
                  "credentials", "webhook_secret", "has_credentials", "has_webhook_secret",
                  "cod_supported", "is_active", "sort_order", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def get_has_credentials(self, obj):
        return bool(obj.credentials)

    def get_has_webhook_secret(self, obj):
        return bool(obj.webhook_secret)


class ShipmentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentEvent
        fields = ["status", "carrier_status", "message", "location", "happened_at"]


class ShipmentSerializer(serializers.ModelSerializer):
    events = ShipmentEventSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = ["id", "order", "carrier_code", "tracking_number", "status",
                  "service", "cod_amount_tnd", "label_url", "events",
                  "created_at", "updated_at"]
        read_only_fields = ["tracking_number", "status", "label_url", "events"]


class SupplierCarrierConfigSerializer(serializers.ModelSerializer):
    # `credentials` déprécié (compte maître GROSHOP) — write_only par prudence.
    credentials = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = SupplierCarrierConfig
        fields = ["id", "carrier_code", "is_active", "is_default",
                  "credentials", "created_at"]