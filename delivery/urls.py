# delivery/urls.py — GROSHOP.tn
# À inclure dans le urls racine : path("api/delivery/", include("delivery.urls"))
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CarrierListView, SupplierCarrierConfigViewSet,
                    ShipmentViewSet, CarrierWebhookView)

router = DefaultRouter()
router.register("carrier-configs", SupplierCarrierConfigViewSet, basename="carrier-config")
router.register("shipments", ShipmentViewSet, basename="shipment")

urlpatterns = [
    path("carriers/", CarrierListView.as_view(), name="carriers"),
    path("webhooks/<str:carrier_code>/", CarrierWebhookView.as_view(), name="carrier-webhook"),
    path("", include(router.urls)),
]