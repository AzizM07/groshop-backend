# store/views.py — GROSHOP.tn
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction

from users.models import SupplierProfile
from products.models import Product
from .models import SubscriptionPlan, SupplierSubscription
from .serializers import SubscriptionPlanSerializer, SupplierSubscriptionSerializer


# ── Historique de recherche (stubs existants — à compléter plus tard) ──
def recent_searches(request):
    return JsonResponse({"status": "recent_searches view"})


def clear_recent_searches(request):
    return JsonResponse({"status": "clear_recent_searches view"})


# ══════════════════════════════════════════════════════════════════
# ABONNEMENT FOURNISSEUR
# ══════════════════════════════════════════════════════════════════
def _get_supplier(user):
    if user.role != 'supplier':
        return None, Response({'error': 'Accès réservé aux fournisseurs.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        return SupplierProfile.objects.get(user=user), None
    except SupplierProfile.DoesNotExist:
        return None, Response({'error': 'Profil fournisseur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def plans_list(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_tnd')
    return Response(SubscriptionPlanSerializer(plans, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_subscription(request):
    supplier, err = _get_supplier(request.user)
    if err:
        return err
    sub = (SupplierSubscription.objects
           .filter(supplier=supplier, status='active')
           .select_related('plan')
           .order_by('-started_at')
           .first())
    if not sub:
        return Response(None)
    return Response(SupplierSubscriptionSerializer(sub).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_plan(request):
    supplier, err = _get_supplier(request.user)
    if err:
        return err

    plan_id = request.data.get('plan_id')
    if not plan_id:
        return Response({'error': 'plan_id manquant.'}, status=400)

    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response({'error': 'Plan introuvable ou inactif.'}, status=404)

    # Garde-fou downgrade : le catalogue actuel doit tenir dans max_products
    if plan.max_products is not None:
        current_count = Product.objects.filter(supplier=supplier).exclude(status='draft').count()
        if current_count > plan.max_products:
            return Response({
                'error': (
                    f"Ce plan limite à {plan.max_products} produits, "
                    f"or vous en avez {current_count}. Retirez-en avant de rétrograder."
                )
            }, status=400)

    with transaction.atomic():
        SupplierSubscription.objects.filter(
            supplier=supplier, status='active'
        ).update(status='cancelled')

        sub = SupplierSubscription.objects.create(
            supplier   = supplier,
            plan       = plan,
            status     = 'active',
            started_at = timezone.now(),
            changed_by = request.user,
        )

    return Response(SupplierSubscriptionSerializer(sub).data, status=200)


# ══════════════════════════════════════════════════════════════════
# PLANS PUBLICS — landing "devenir fournisseur" (AllowAny, visiteur anonyme)
# Chemin final : /api/store/plans/
# Aplatit features JSON → items / description / highlighted / badge
# ══════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([AllowAny])
def public_plans(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_tnd')
    out = []
    for p in plans:
        feats = p.features or {}
        out.append({
            'id':             str(p.id),
            'name':           p.name,
            'price_tnd':      str(p.price_tnd),
            'commission_pct': str(p.commission_pct),
            'max_products':   p.max_products,          # null = illimité
            'features':       feats.get('items', []),
            'description':    feats.get('description', ''),
            'highlighted':    bool(feats.get('highlighted', False)),
            'badge':          feats.get('badge', ''),
        })
    return Response(out)