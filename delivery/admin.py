# delivery/admin.py — GROSHOP.tn
from django.contrib import admin
from .models import CarrierProvider, SupplierCarrierConfig, Shipment, ShipmentEvent


class ShipmentEventInline(admin.TabularInline):
    model = ShipmentEvent
    extra = 0


@admin.register(CarrierProvider)
class CarrierProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "cod_supported", "sort_order", "updated_at")
    list_filter = ("is_active", "cod_supported")
    search_fields = ("name", "code")
    ordering = ("sort_order", "name")


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