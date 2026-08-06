# delivery/views.py — GROSHOP.tn
from rest_framework import viewsets, decorators, response, status, permissions
from rest_framework.views import APIView
from .models import SupplierCarrierConfig, Shipment
from .serializers import SupplierCarrierConfigSerializer, ShipmentSerializer
from .carriers.registry import available_carriers
from . import services


def _supplier_of(request):
    # ⚠️ ADAPTE à ta logique : le SupplierProfile lié à l'utilisateur connecté.
    return getattr(request.user, "supplier_profile", None) \
        or getattr(request.user, "supplier", None)


class CarrierListView(APIView):
    """GET /api/delivery/carriers/ → transporteurs disponibles (pour le menu)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return response.Response(
            [{"code": c, "label": l} for c, l in available_carriers()]
        )


class SupplierCarrierConfigViewSet(viewsets.ModelViewSet):
    """CRUD des transporteurs activés par le fournisseur connecté."""
    serializer_class = SupplierCarrierConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SupplierCarrierConfig.objects.filter(supplier=_supplier_of(self.request))

    def perform_create(self, serializer):
        serializer.save(supplier=_supplier_of(self.request))


class ShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (Shipment.objects.filter(supplier=_supplier_of(self.request))
                .prefetch_related("events"))

    def create(self, request, *args, **kwargs):
        d = request.data
        shipment = services.create_shipment(
            supplier=_supplier_of(request),
            order_id=d.get("order"),
            origin=d.get("origin", {}),
            destination=d.get("destination", {}),
            parcels=d.get("parcels"),
            carrier_code=d.get("carrier_code"),
            service=d.get("service", "standard"),
            cod_amount_tnd=d.get("cod_amount_tnd", 0),
        )
        return response.Response(ShipmentSerializer(shipment).data,
                                 status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["post"])
    def refresh(self, request, pk=None):
        shipment = services.refresh_tracking(self.get_object())
        return response.Response(ShipmentSerializer(shipment).data)


class CarrierWebhookView(APIView):
    """POST /api/delivery/webhooks/<carrier_code>/ — MAJ de statut poussées.
    ⚠️ Vérifie la signature du transporteur avant de faire confiance au payload."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, carrier_code):
        shipment = services.apply_webhook(carrier_code, request.data, dict(request.headers))
        if shipment is None:
            return response.Response({"detail": "ignoré"},
                                     status=status.HTTP_202_ACCEPTED)
        return response.Response({"status": shipment.status})