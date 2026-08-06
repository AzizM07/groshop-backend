# delivery/admin.py — GROSHOP.tn
from django.contrib import admin
from .models import SupplierCarrierConfig, Shipment, ShipmentEvent


class ShipmentEventInline(admin.TabularInline):
    model = ShipmentEvent
    extra = 0


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("tracking_number", "carrier_code", "status", "supplier", "created_at")
    list_filter = ("carrier_code", "status")
    search_fields = ("tracking_number",)
    inlines = [ShipmentEventInline]


@admin.register(SupplierCarrierConfig)
class SupplierCarrierConfigAdmin(admin.ModelAdmin):
    list_display = ("supplier", "carrier_code", "is_active", "is_default")
    list_filter = ("carrier_code", "is_active")