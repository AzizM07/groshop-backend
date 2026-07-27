# orders/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.db.models import Count, F, Prefetch, Exists, OuterRef
from django.shortcuts import get_object_or_404

from analytics.tracking import attribute_order
from products.models import Product
from users.models import Address

from .models import Order, SubOrder, OrderItem, CartItem
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, CreateOrderSerializer,
    CartItemSerializer, SupplierSubOrderSerializer,
)


# ── Prefetch réutilisable ─────────────────────────────────────────
ITEMS_PREFETCH = Prefetch(
    'items',
    queryset=OrderItem.objects
        .select_related('product', 'product__category')
        .prefetch_related('product__images'),
)


# ══════════════════════════════════════════════════════════════════
# ORDERS — ACHETEUR
# ══════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_list(request):
    orders = (Order.objects
              .filter(buyer=request.user)
              .prefetch_related('sub_orders')
              .order_by('-created_at'))
    serializer = OrderListSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    try:
        order = Order.objects.prefetch_related(
            Prefetch('sub_orders', queryset=SubOrder.objects
                     .select_related('supplier')
                     .prefetch_related(ITEMS_PREFETCH)),
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

    # ── Résolution de l'adresse ──
    # Priorité : address_id (l'user a sélectionné une adresse sauvegardée)
    #            → snapshot texte via formatted() + FK vers l'Address
    # Fallback  : shipping_address texte brut (invités, ou legacy)
    address_ref = None
    address_snapshot = data.get('shipping_address', '')

    address_id = data.get('address_id')
    if address_id:
        try:
            address_ref = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response(
                {'error': "Adresse introuvable ou n'appartenant pas à cet utilisateur."},
                status=400,
            )
        address_snapshot = address_ref.formatted()

    if not address_snapshot:
        return Response({'error': 'Adresse de livraison manquante.'}, status=400)

    with transaction.atomic():
        order = Order.objects.create(
            buyer                = request.user,
            shipping_address     = address_snapshot,
            shipping_address_ref = address_ref,
            payment_method       = data['payment_method'],
            notes                = data.get('notes', ''),
            status               = 'pending',
            payment_status       = 'unpaid',
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
                Product.objects.filter(id=item['product'].id).update(
                    sold_count=F('sold_count') + item['quantity'])

        order.total_tnd = total_order
        order.save()

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def to_review(request):
    from products.models import Review

    already = Review.objects.filter(
        reviewer=request.user,
        product=OuterRef('product'),
    )

    items = (OrderItem.objects
             .filter(
                 sub_order__order__buyer=request.user,
                 sub_order__status='delivered',
             )
             .annotate(_reviewed=Exists(already))
             .filter(_reviewed=False)
             .select_related('product', 'sub_order', 'sub_order__order')
             .prefetch_related('product__images')
             .order_by('-sub_order__order__created_at'))

    results = []
    for it in items:
        images = it.product.images.all()
        image_url = None
        for img in images:
            if img.is_primary:
                image_url = img.url
                break
        if image_url is None and images:
            image_url = images[0].url

        results.append({
            'order_item_id': str(it.id),
            'order_id':      str(it.sub_order.order_id),
            'product_id':    str(it.product_id),
            'product_name':  it.product.name,
            'product_image': image_url,
            'variant_id':    str(it.variant_id) if getattr(it, 'variant_id', None) else None,
            'quantity':      it.quantity,
            'delivered_at':  it.sub_order.updated_at,
        })

    return Response({'count': len(results), 'results': results})


# ══════════════════════════════════════════════════════════════════
# ORDERS — FOURNISSEUR
# ══════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_orders(request):
    if not hasattr(request.user, 'supplier_profile'):
        return Response({'error': 'Compte fournisseur requis.'}, status=403)
    supplier = request.user.supplier_profile

    qs = (SubOrder.objects
          .filter(supplier=supplier)
          .select_related('order', 'order__buyer')
          .prefetch_related(ITEMS_PREFETCH)
          .order_by('-created_at'))

    st = request.query_params.get('status')
    if st and st != 'all':
        qs = qs.filter(status=st)

    rows = SubOrder.objects.filter(supplier=supplier).values('status').annotate(c=Count('id'))
    counts = {r['status']: r['c'] for r in rows}
    counts['all'] = sum(counts.values())

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
        so = (SubOrder.objects
              .select_related('order', 'order__buyer')
              .prefetch_related(ITEMS_PREFETCH)
              .get(id=pk, supplier=request.user.supplier_profile))
    except SubOrder.DoesNotExist:
        return Response({'error': 'Sous-commande non trouvée.'}, status=404)
    new_status = request.data.get('status')
    if new_status not in dict(SubOrder.STATUS):
        return Response({'error': 'Statut invalide.'}, status=400)
    so.status = new_status
    so.save(update_fields=['status', 'updated_at'])
    return Response(SupplierSubOrderSerializer(so).data)


# ══════════════════════════════════════════════════════════════════
# CART (inchangé)
# ══════════════════════════════════════════════════════════════════
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    if request.method == 'GET':
        items = CartItem.objects.filter(buyer=request.user).select_related(
            'product', 'product__supplier', 'variant',
        ).prefetch_related('product__images', 'product__price_tiers')
        return Response(CartItemSerializer(items, many=True).data)

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
    item = get_object_or_404(
        CartItem.objects.select_related('product', 'product__supplier', 'variant')
                        .prefetch_related('product__images', 'product__price_tiers'),
        id=pk, buyer=request.user,
    )

    if request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
    CartItem.objects.filter(buyer=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_count(request):
    count = CartItem.objects.filter(buyer=request.user).count()
    return Response({'count': count})