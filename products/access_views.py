# products/access_views.py — GROSHOP.tn
# Endpoints REST pour la gestion des accès prix (unlocks).

from datetime import timedelta
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User, SupplierProfile
from .models import Product
from .access_models import SupplierUserUnlock, ProductPriceUnlock


def _get_supplier_or_403(request):
    """L'utilisateur doit être un fournisseur pour donner/révoquer des accès."""
    if request.user.role != 'supplier':
        return None, Response({'error': 'Réservé aux fournisseurs.'}, status=403)
    try:
        supplier = SupplierProfile.objects.get(user=request.user)
    except SupplierProfile.DoesNotExist:
        return None, Response({'error': 'Profil fournisseur introuvable.'}, status=404)
    return supplier, None


def _compute_expires_at(duration_days):
    """Renvoie None si permanent, sinon now + duration_days."""
    if duration_days is None:
        return None
    try:
        days = int(duration_days)
    except (TypeError, ValueError):
        return None
    if days <= 0:
        return None
    return timezone.now() + timedelta(days=days)


# ─── 1. Débloquer TOUT le catalogue pour un user ─────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlock_supplier_for_user(request, user_id):
    supplier, err = _get_supplier_or_403(request)
    if err: return err

    target_user = get_object_or_404(User, id=user_id)
    duration_days = request.data.get('duration_days')  # None ou int
    note          = request.data.get('note', '')
    expires_at    = _compute_expires_at(duration_days)

    unlock, created = SupplierUserUnlock.objects.update_or_create(
        supplier=supplier,
        user=target_user,
        defaults={
            'expires_at': expires_at,
            'revoked_at': None,
            'note': note,
        },
    )
    return Response({
        'id': str(unlock.id),
        'type': 'supplier',
        'user_id': str(target_user.id),
        'expires_at': unlock.expires_at,
        'is_active': True,
        'created': created,
    }, status=201 if created else 200)


# ─── 2. Débloquer UN produit pour un user ────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlock_product_for_user(request, product_id):
    supplier, err = _get_supplier_or_403(request)
    if err: return err

    product = get_object_or_404(Product, id=product_id, supplier=supplier)
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'error': 'user_id requis.'}, status=400)
    target_user = get_object_or_404(User, id=user_id)

    duration_days = request.data.get('duration_days')
    note          = request.data.get('note', '')
    expires_at    = _compute_expires_at(duration_days)

    unlock, created = ProductPriceUnlock.objects.update_or_create(
        product=product,
        user=target_user,
        defaults={
            'expires_at': expires_at,
            'revoked_at': None,
            'note': note,
        },
    )
    return Response({
        'id': str(unlock.id),
        'type': 'product',
        'product_id': str(product.id),
        'user_id': str(target_user.id),
        'expires_at': unlock.expires_at,
        'is_active': True,
        'created': created,
    }, status=201 if created else 200)


# ─── 3. Révoquer accès catalogue ─────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_supplier_unlock(request, unlock_id):
    supplier, err = _get_supplier_or_403(request)
    if err: return err

    unlock = get_object_or_404(SupplierUserUnlock, id=unlock_id, supplier=supplier)
    unlock.revoked_at = timezone.now()
    unlock.save(update_fields=['revoked_at'])
    return Response({'revoked': True})


# ─── 4. Révoquer accès produit ───────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_product_unlock(request, unlock_id):
    supplier, err = _get_supplier_or_403(request)
    if err: return err

    unlock = get_object_or_404(ProductPriceUnlock, id=unlock_id, product__supplier=supplier)
    unlock.revoked_at = timezone.now()
    unlock.save(update_fields=['revoked_at'])
    return Response({'revoked': True})


# ─── 5. Consulter les accès accordés (dashboard fournisseur) ─────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_unlocks(request):
    supplier, err = _get_supplier_or_403(request)
    if err: return err

    now = timezone.now()
    active_filter = models.Q(revoked_at__isnull=True) & (
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
    )

    supplier_unlocks = SupplierUserUnlock.objects.filter(
        supplier=supplier
    ).filter(active_filter).select_related('user').order_by('-granted_at')

    product_unlocks = ProductPriceUnlock.objects.filter(
        product__supplier=supplier
    ).filter(active_filter).select_related('user', 'product').order_by('-granted_at')

    return Response({
        'supplier_unlocks': [{
            'id': str(u.id),
            'user_id': str(u.user.id),
            'user_name': u.user.full_name,
            'user_email': u.user.email,
            'granted_at': u.granted_at,
            'expires_at': u.expires_at,
            'note': u.note,
        } for u in supplier_unlocks],
        'product_unlocks': [{
            'id': str(u.id),
            'user_id': str(u.user.id),
            'user_name': u.user.full_name,
            'user_email': u.user.email,
            'product_id': str(u.product.id),
            'product_name': u.product.name,
            'granted_at': u.granted_at,
            'expires_at': u.expires_at,
            'note': u.note,
        } for u in product_unlocks],
    })


# ─── 6. Vérifier l'état d'accès dans une conversation ────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_access(request, user_id):
    """
    Utilisé par le frontend messagerie : "ce user a-t-il accès à mon catalogue
    ou à un produit précis ?". Renvoie l'état complet à afficher dans le bandeau.
    """
    supplier, err = _get_supplier_or_403(request)
    if err: return err

    target_user = get_object_or_404(User, id=user_id)
    product_id  = request.query_params.get('product_id')

    now = timezone.now()

    # État catalogue complet
    supplier_unlock = SupplierUserUnlock.objects.filter(
        supplier=supplier,
        user=target_user,
        revoked_at__isnull=True,
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
    ).first()

    result = {
        'user_is_verified_business': target_user.business_status == 'verified',
        'catalog_unlocked': supplier_unlock is not None,
        'catalog_unlock': None,
        'product_unlocked': False,
        'product_unlock': None,
    }

    if supplier_unlock:
        result['catalog_unlock'] = {
            'id': str(supplier_unlock.id),
            'granted_at': supplier_unlock.granted_at,
            'expires_at': supplier_unlock.expires_at,
        }

    if product_id:
        product_unlock = ProductPriceUnlock.objects.filter(
            product_id=product_id,
            product__supplier=supplier,
            user=target_user,
            revoked_at__isnull=True,
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).first()

        if product_unlock:
            result['product_unlocked'] = True
            result['product_unlock']   = {
                'id': str(product_unlock.id),
                'granted_at': product_unlock.granted_at,
                'expires_at': product_unlock.expires_at,
            }

    return Response(result)