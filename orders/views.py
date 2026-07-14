# orders/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.db.models import Count, F
from django.shortcuts import get_object_or_404

from analytics.tracking import attribute_order
from products.models import Product

from .models import Order, SubOrder, OrderItem, CartItem
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, CreateOrderSerializer,
    CartItemSerializer, SupplierSubOrderSerializer,
)


# ══════════════════════════════════════════════════════════════════
# ORDERS — ACHETEUR
# ══════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_list(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    serializer = OrderListSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    try:
        order = Order.objects.prefetch_related(
            'sub_orders__items__product__images'
        ).get(id=pk, buyer=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Commande non trouvée.'}, status=404)
    return Response(OrderDetailSerializer(order).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data  = serializer.validated_data
    items = data['items']

    if not items:
        return Response({'error': 'Aucun produit dans la commande.'}, status=400)

    with transaction.atomic():
        order = Order.objects.create(
            buyer            = request.user,
            shipping_address = data['shipping_address'],
            payment_method   = data['payment_method'],
            notes            = data.get('notes', ''),
            status           = 'pending',
            payment_status   = 'unpaid',
        )

        total_order     = 0
        suppliers_items = {}

        for item_data in items:
            product_id = item_data.get('product_id')
            quantity   = int(item_data.get('quantity', 1))

            try:
                product = Product.objects.select_related('supplier').get(
                    id=product_id, status='approved')
            except Product.DoesNotExist:
                raise Exception(f'Produit {product_id} non trouvé.')

            if quantity < product.moq:
                raise Exception(
                    f'Quantité minimum pour {product.name} est {product.moq}.')

            tier = product.price_tiers.filter(
                min_qty__lte=quantity
            ).order_by('-min_qty').first()
            unit_price   = tier.price_tnd if tier else product.base_price_tnd
            total        = unit_price * quantity
            total_order += total

            supplier_id = str(product.supplier.id)
            if supplier_id not in suppliers_items:
                suppliers_items[supplier_id] = {
                    'supplier': product.supplier,
                    'items':    [],
                    'subtotal': 0,
                }
            suppliers_items[supplier_id]['items'].append({
                'product':    product,
                'quantity':   quantity,
                'unit_price': unit_price,
                'total':      total,
            })
            suppliers_items[supplier_id]['subtotal'] += total

        for supplier_id, supplier_data in suppliers_items.items():
            sub_order = SubOrder.objects.create(
                order        = order,
                supplier     = supplier_data['supplier'],
                status       = 'pending',
                subtotal_tnd = supplier_data['subtotal'],
            )
            for item in supplier_data['items']:
                OrderItem.objects.create(
                    sub_order      = sub_order,
                    product        = item['product'],
                    quantity       = item['quantity'],
                    unit_price_tnd = item['unit_price'],
                    total_tnd      = item['total'],
                )
                # F() : incrément côté base → pas de perte si commandes simultanées
                Product.objects.filter(id=item['product'].id).update(
                    sold_count=F('sold_count') + item['quantity'])

        order.total_tnd = total_order
        order.save()

        # ── Attribution analytics : canal + région + session convertie ──
        attribute_order(order, request)

    return Response(
        OrderDetailSerializer(order).data,
        status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, pk):
    try:
        order = Order.objects.get(
            id=pk, buyer=request.user, status='pending')
    except Order.DoesNotExist:
        return Response({'error': 'Commande non trouvée ou non annulable.'}, status=404)
    order.status = 'cancelled'
    order.save()
    return Response({'message': 'Commande annulée.'})


# ══════════════════════════════════════════════════════════════════
# ORDERS — FOURNISSEUR
# ══════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_orders(request):
    if not hasattr(request.user, 'supplier_profile'):
        return Response({'error': 'Compte fournisseur requis.'}, status=403)
    supplier = request.user.supplier_profile

    qs = SubOrder.objects.filter(supplier=supplier).select_related(
        'order', 'order__buyer'
    ).prefetch_related('items__product__images').order_by('-created_at')

    st = request.query_params.get('status')
    if st and st != 'all':
        qs = qs.filter(status=st)

    base   = SubOrder.objects.filter(supplier=supplier)
    counts = {r['status']: r['c'] for r in base.values('status').annotate(c=Count('id'))}
    counts['all'] = base.count()

    return Response({
        'results': SupplierSubOrderSerializer(qs, many=True).data,
        'counts':  counts,
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def supplier_suborder_update(request, pk):
    if not hasattr(request.user, 'supplier_profile'):
        return Response({'error': 'Compte fournisseur requis.'}, status=403)
    try:
        so = SubOrder.objects.get(id=pk, supplier=request.user.supplier_profile)
    except SubOrder.DoesNotExist:
        return Response({'error': 'Sous-commande non trouvée.'}, status=404)
    new_status = request.data.get('status')
    if new_status not in dict(SubOrder.STATUS):
        return Response({'error': 'Statut invalide.'}, status=400)
    so.status = new_status
    so.save(update_fields=['status', 'updated_at'])
    return Response(SupplierSubOrderSerializer(so).data)


# ══════════════════════════════════════════════════════════════════
# CART
# ══════════════════════════════════════════════════════════════════
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    """
    GET  /api/cart/      → liste les items du panier
    POST /api/cart/      → ajoute un item (ou met à jour la qty si déjà présent)
                            body: { product_id, quantity, variant_id? }
    """
    if request.method == 'GET':
        items = CartItem.objects.filter(buyer=request.user).select_related(
            'product', 'product__supplier', 'variant',
        ).prefetch_related('product__images', 'product__price_tiers')
        return Response(CartItemSerializer(items, many=True).data)

    # POST → add or update
    product_id = request.data.get('product_id')
    quantity   = request.data.get('quantity', 1)
    variant_id = request.data.get('variant_id') or None

    if not product_id:
        return Response({'error': 'product_id requis.'}, status=400)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response({'error': 'Quantité invalide.'}, status=400)

    try:
        product = Product.objects.get(id=product_id, status='approved')
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé.'}, status=404)

    if quantity < product.moq:
        quantity = product.moq

    item, created = CartItem.objects.update_or_create(
        buyer=request.user,
        product=product,
        variant_id=variant_id,
        defaults={'quantity': quantity},
    )

    return Response(
        CartItemSerializer(item).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_item_view(request, pk):
    """
    PATCH  /api/cart/<id>/   → modifie la qty
    DELETE /api/cart/<id>/   → supprime l'item
    """
    item = get_object_or_404(CartItem, id=pk, buyer=request.user)

    if request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PATCH
    quantity = request.data.get('quantity')
    if quantity is not None:
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({'error': 'Quantité invalide.'}, status=400)
        if quantity < 1:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        item.quantity = quantity
        item.save()

    return Response(CartItemSerializer(item).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_clear(request):
    """DELETE /api/cart/clear/ → vide le panier."""
    CartItem.objects.filter(buyer=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_count(request):
    """GET /api/cart/count/ → nombre d'items pour badge nav."""
    count = CartItem.objects.filter(buyer=request.user).count()
    return Response({'count': count})