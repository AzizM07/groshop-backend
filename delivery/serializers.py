# delivery/serializers.py — GROSHOP.tn
from rest_framework import serializers
from .models import SupplierCarrierConfig, Shipment, ShipmentEvent


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
    # Les identifiants ne repartent JAMAIS en lecture.
    credentials = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = SupplierCarrierConfig
        fields = ["id", "carrier_code", "is_active", "is_default",
                  "credentials", "created_at"]