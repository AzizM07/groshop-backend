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
from django.utils import timezone
from datetime import timedelta
from .models import Order, SubOrder, OrderItem, CartItem, CustomizationRequest
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, CreateOrderSerializer,
    CartItemSerializer, SupplierSubOrderSerializer,
    CustomizationRequestSerializer,
    CustomizationRequestCreateSerializer,
    CustomizationRequestQuoteSerializer,
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
              .prefetch_related(
                  Prefetch('sub_orders', queryset=SubOrder.objects
                           .select_related('supplier')
                           .prefetch_related(ITEMS_PREFETCH)),
              )
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
            cart_item_id = item_data.get('cart_item_id')  # ← nouveau : id du CartItem source
            quantity   = int(item_data.get('quantity', 1))

            # Si cart_item_id fourni, on charge le CartItem pour récupérer perso + prix verrouillé
            cart_item = None
            if cart_item_id:
                try:
                    cart_item = CartItem.objects.select_related(
                        'product', 'product__supplier', 'customization_request',
                    ).get(id=cart_item_id, buyer=request.user)
                    product = cart_item.product
                    quantity = cart_item.quantity
                except CartItem.DoesNotExist:
                    raise Exception(f'Item panier {cart_item_id} introuvable.')
            else:
                try:
                    product = Product.objects.select_related('supplier').get(
                        id=product_id, status='approved')
                except Product.DoesNotExist:
                    raise Exception(f'Produit {product_id} non trouvé.')

            if quantity < product.moq:
                raise Exception(
                    f'Quantité minimum pour {product.name} est {product.moq}.')

            # Prix résolu : property unit_price du CartItem gère les 3 cas (quote/fixed/standard)
            if cart_item is not None:
                unit_price = cart_item.unit_price
            else:
                tier = product.price_tiers.filter(
                    min_qty__lte=quantity
                ).order_by('-min_qty').first()
                unit_price = tier.price_tnd if tier else product.base_price_tnd
                # Item ajouté sans passer par le panier : applique le surcoût fixed si perso
                if (product.allow_customization
                        and product.customization_mode == 'fixed'
                        and item_data.get('is_customized')):
                    unit_price = unit_price + product.customization_extra_price_tnd

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
                'product':               product,
                'quantity':              quantity,
                'unit_price':            unit_price,
                'total':                 total,
                'is_customized':         cart_item.is_customized if cart_item else bool(item_data.get('is_customized')),
                'customization_values':  cart_item.customization_values if cart_item else (item_data.get('customization_values') or []),
                'customization_request': cart_item.customization_request if cart_item else None,
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
                    sub_order             = sub_order,
                    product               = item['product'],
                    quantity              = item['quantity'],
                    unit_price_tnd        = item['unit_price'],
                    total_tnd             = item['total'],
                    is_customized         = item.get('is_customized', False),
                    customization_values  = item.get('customization_values', []),
                    customization_request = item.get('customization_request'),
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

    with transaction.atomic():
        order.sub_orders.update(status='cancelled')
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

    update_fields = ['status', 'updated_at']
    so.status = new_status

    delivery_type = request.data.get('delivery_type')
    if delivery_type is not None:
        if delivery_type not in dict(SubOrder.DELIVERY_TYPES):
            return Response({'error': 'Type de livraison invalide.'}, status=400)
        so.delivery_type = delivery_type
        update_fields.append('delivery_type')

    so.save(update_fields=update_fields)
    return Response(SupplierSubOrderSerializer(so).data)


# ══════════════════════════════════════════════════════════════════
# CART — accepte user connecté OU invité (via guest_id cookie)
# ══════════════════════════════════════════════════════════════════
from rest_framework.permissions import AllowAny


def _cart_filter(request):
    """Retourne le filtre queryset selon connecté / invité."""
    if request.user.is_authenticated:
        return {'buyer': request.user}
    return {'guest_id': request.guest_id}


def _cart_owner_fields(request):
    """Retourne les kwargs pour create/update_or_create."""
    if request.user.is_authenticated:
        return {'buyer': request.user, 'guest_id': None}
    return {'buyer': None, 'guest_id': request.guest_id}


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def cart_view(request):
    if request.method == 'GET':
        items = CartItem.objects.filter(**_cart_filter(request)).select_related(
            'product', 'product__supplier', 'variant', 'customization_request',
        ).prefetch_related('product__images', 'product__price_tiers')
        return Response(CartItemSerializer(items, many=True).data)

    # ── POST : ajout au panier ──
    product_id                = request.data.get('product_id')
    quantity                  = request.data.get('quantity', 1)
    variant_id                = request.data.get('variant_id') or None
    is_customized             = bool(request.data.get('is_customized', False))
    customization_values      = request.data.get('customization_values') or []
    customization_request_id  = request.data.get('customization_request_id') or None

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

    # ── Gate : produit en mode 'quote' → obligatoirement via devis ──
    if product.allow_customization and product.customization_mode == 'quote':
        if not is_customized or not customization_request_id:
            return Response(
                {'error': 'Ce produit nécessite un devis accepté avant ajout au panier.'},
                status=400,
            )

    # ── Gate : produit fixed + required → obligatoirement personnalisé ──
    if (product.allow_customization
            and product.customization_mode == 'fixed'
            and product.customization_required
            and not is_customized):
        return Response(
            {'error': 'Ce produit doit être personnalisé pour être commandé.'},
            status=400,
        )

    # ── Cas : item customisé ──
    if is_customized:
        if not product.allow_customization:
            return Response({'error': 'Ce produit n\'accepte pas la personnalisation.'}, status=400)

        # Validation des champs obligatoires
        provided_field_ids = {str(v.get('field_id')) for v in customization_values}
        for field in product.customization_fields.all():
            if field.required and str(field.id) not in provided_field_ids:
                return Response(
                    {'error': f'Le champ "{field.label}" est obligatoire.'},
                    status=400,
                )

        # Mode 'quote' : la demande doit exister, être acceptée, appartenir au buyer
        req = None
        if product.customization_mode == 'quote':
            if not request.user.is_authenticated:
                return Response({'error': 'Connexion requise pour un item sur devis.'}, status=401)
            try:
                req = CustomizationRequest.objects.get(id=customization_request_id)
            except CustomizationRequest.DoesNotExist:
                return Response({'error': 'Devis introuvable.'}, status=404)
            if req.buyer_id != request.user.id:
                return Response({'error': "Ce devis ne vous appartient pas."}, status=403)
            if req.status != 'accepted':
                return Response({'error': "Ce devis n'est pas accepté."}, status=400)
            if req.product_id != product.id:
                return Response({'error': 'Devis / produit incohérents.'}, status=400)

        # Création directe (pas d'update_or_create : chaque perso est unique)
        item = CartItem.objects.create(
            product=product,
            variant_id=variant_id,
            quantity=quantity,
            is_customized=True,
            customization_values=customization_values,
            customization_request=req,
            **_cart_owner_fields(request),
        )
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    # ── Cas : item standard (comportement existant) ──
    item, created = CartItem.objects.update_or_create(
        product=product,
        variant_id=variant_id,
        is_customized=False,
        **_cart_filter(request),
        defaults={'quantity': quantity, **_cart_owner_fields(request)},
    )

    return Response(
        CartItemSerializer(item).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )

@api_view(['PATCH', 'DELETE'])
@permission_classes([AllowAny])
def cart_item_view(request, pk):
    item = get_object_or_404(
        CartItem.objects.select_related('product', 'product__supplier', 'variant')
                        .prefetch_related('product__images', 'product__price_tiers'),
        id=pk, **_cart_filter(request),
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
@permission_classes([AllowAny])
def cart_clear(request):
    CartItem.objects.filter(**_cart_filter(request)).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def cart_count(request):
    count = CartItem.objects.filter(**_cart_filter(request)).count()
    return Response({'count': count})


# ══════════════════════════════════════════════════════════════════
# CART MERGE — appelée après login/register pour fusionner panier invité
# ══════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_merge(request):
    """
    Fusionne le panier invité (lié au cookie gs_guest_id) dans le panier
    de l'utilisateur qui vient de se connecter. Si un même produit existe
    des deux côtés, on additionne les quantités.
    """
    guest_id = getattr(request, 'guest_id', None)
    if not guest_id:
        return Response({'merged': 0})

    guest_items = list(CartItem.objects.filter(guest_id=guest_id))
    if not guest_items:
        return Response({'merged': 0})

    merged = 0
    with transaction.atomic():
        for g_item in guest_items:
            existing = CartItem.objects.filter(
                buyer=request.user,
                product=g_item.product,
                variant=g_item.variant,
            ).first()
            if existing:
                # Additionne les quantités
                existing.quantity = existing.quantity + g_item.quantity
                existing.save(update_fields=['quantity', 'updated_at'])
                g_item.delete()
            else:
                # Transfère au user
                g_item.buyer = request.user
                g_item.guest_id = None
                g_item.save(update_fields=['buyer', 'guest_id', 'updated_at'])
            merged += 1

    return Response({'merged': merged})


# ══════════════════════════════════════════════════════════════════
# CUSTOMIZATION REQUESTS (devis pour perso mode 'quote')
# ══════════════════════════════════════════════════════════════════

def _format_quote_request_message(req):
    """Résumé texte de la demande, posté comme premier message dans la conv."""
    lines = [
        f"📋 Demande de personnalisation — {req.product.name}",
        f"Quantité souhaitée : {req.quantity}",
        "",
        "Détails :",
    ]
    for v in req.values or []:
        label = v.get('label', '(sans nom)')
        value = v.get('value', '')
        ftype = v.get('field_type', 'text')
        if ftype in ('image', 'file'):
            lines.append(f"• {label} : {value}")
        else:
            lines.append(f"• {label} : {value}")
    lines.append("")
    lines.append("Merci de m'envoyer un devis avec le prix et le délai.")
    return "\n".join(lines)


def _format_quote_response_message(req):
    """Message du devis posté par le fournisseur."""
    total = req.quoted_price_tnd * req.quantity if req.quoted_price_tnd else 0
    lines = [
        f"💰 Devis proposé",
        f"Prix unitaire : {req.quoted_price_tnd} TND × {req.quantity} = {total} TND",
    ]
    if req.expires_at:
        lines.append(f"Validité : jusqu'au {req.expires_at.strftime('%d/%m/%Y')}")
    if req.supplier_note:
        lines.append("")
        lines.append(req.supplier_note)
    return "\n".join(lines)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customization_requests(request):
    """
    GET  = liste des demandes de l'utilisateur (buyer OU supplier)
    POST = crée une demande (buyer soumet la popup 'Personnaliser')
    """
    from messaging.models import Conversation, Message

    if request.method == 'GET':
        role = getattr(request.user, 'role', 'buyer')
        if role == 'supplier' and hasattr(request.user, 'supplier_profile'):
            qs = CustomizationRequest.objects.filter(
                product__supplier=request.user.supplier_profile,
            )
        else:
            qs = CustomizationRequest.objects.filter(buyer=request.user)
        qs = qs.select_related(
            'product', 'buyer', 'variant',
        ).prefetch_related('product__images').order_by('-created_at')
        return Response(CustomizationRequestSerializer(qs, many=True).data)

    # ── POST : création par l'acheteur ──
    if getattr(request.user, 'role', None) != 'buyer':
        return Response(
            {'error': 'Seuls les acheteurs peuvent demander une personnalisation.'},
            status=403,
        )

    ser = CustomizationRequestCreateSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)
    data = ser.validated_data

    try:
        product = Product.objects.select_related('supplier').get(
            id=data['product_id'], status='approved',
        )
    except Product.DoesNotExist:
        return Response({'error': 'Produit non trouvé.'}, status=404)

    if not product.allow_customization:
        return Response({'error': "Ce produit n'est pas personnalisable."}, status=400)

    # Validation des champs obligatoires
    provided_field_ids = {str(v.get('field_id')) for v in data['values']}
    for field in product.customization_fields.all():
        if field.required and str(field.id) not in provided_field_ids:
            return Response(
                {'error': f'Le champ "{field.label}" est obligatoire.'},
                status=400,
            )

    with transaction.atomic():
        # Conversation (get_or_create — évite les doublons si plusieurs demandes)
        conv, _ = Conversation.objects.get_or_create(
            buyer      = request.user,
            supplier   = product.supplier,
            product    = product,
        )

        req = CustomizationRequest.objects.create(
            buyer       = request.user,
            product     = product,
            variant_id  = data.get('variant_id') or None,
            quantity    = data['quantity'],
            values      = data['values'],
            status      = 'pending',
            conversation= conv,
        )

        # Message quote_request dans la conv
        Message.objects.create(
            conversation          = conv,
            sender                = request.user,
            content               = _format_quote_request_message(req),
            message_type          = 'quote_request',
            customization_request = req,
        )
        conv.last_msg_at = timezone.now()
        conv.save(update_fields=['last_msg_at'])

    return Response(CustomizationRequestSerializer(req).data, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customization_request_quote(request, pk):
    """Fournisseur envoie un devis (prix + validité) pour une demande pending."""
    from messaging.models import Message

    if not hasattr(request.user, 'supplier_profile'):
        return Response({'error': 'Compte fournisseur requis.'}, status=403)

    try:
        req = CustomizationRequest.objects.select_related(
            'product', 'product__supplier', 'conversation',
        ).get(id=pk)
    except CustomizationRequest.DoesNotExist:
        return Response({'error': 'Demande introuvable.'}, status=404)

    if req.product.supplier_id != request.user.supplier_profile.id:
        return Response({'error': "Cette demande n'est pas adressée à votre boutique."}, status=403)

    if req.status not in ('pending', 'quoted'):
        return Response({'error': "Impossible de coter une demande déjà finalisée."}, status=400)

    ser = CustomizationRequestQuoteSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)
    data = ser.validated_data

    with transaction.atomic():
        req.quoted_price_tnd = data['quoted_price_tnd']
        req.quoted_at        = timezone.now()
        req.expires_at       = timezone.now() + timedelta(days=data['validity_days'])
        req.supplier_note    = data.get('supplier_note', '')
        req.status           = 'quoted'
        req.save()

        if req.conversation_id:
            Message.objects.create(
                conversation          = req.conversation,
                sender                = request.user,
                content               = _format_quote_response_message(req),
                message_type          = 'quote_response',
                customization_request = req,
            )
            req.conversation.last_msg_at = timezone.now()
            req.conversation.save(update_fields=['last_msg_at'])

    return Response(CustomizationRequestSerializer(req).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customization_request_accept(request, pk):
    """Buyer accepte le devis → crée un CartItem avec prix verrouillé."""
    from messaging.models import Message

    try:
        req = CustomizationRequest.objects.select_related(
            'product', 'conversation',
        ).get(id=pk)
    except CustomizationRequest.DoesNotExist:
        return Response({'error': 'Demande introuvable.'}, status=404)

    if req.buyer_id != request.user.id:
        return Response({'error': "Cette demande ne vous appartient pas."}, status=403)
    if req.status != 'quoted':
        return Response({'error': "Aucun devis à accepter."}, status=400)
    if req.is_expired:
        req.status = 'expired'
        req.save(update_fields=['status'])
        return Response({'error': "Ce devis a expiré."}, status=400)

    with transaction.atomic():
        cart_item = CartItem.objects.create(
            buyer                 = request.user,
            product               = req.product,
            variant_id            = req.variant_id,
            quantity              = req.quantity,
            is_customized         = True,
            customization_values  = req.values,
            customization_request = req,
        )
        req.status = 'accepted'
        req.save(update_fields=['status'])

        if req.conversation_id:
            Message.objects.create(
                conversation          = req.conversation,
                sender                = request.user,
                content               = "✅ Devis accepté — ajouté au panier.",
                message_type          = 'quote_accepted',
                customization_request = req,
            )
            req.conversation.last_msg_at = timezone.now()
            req.conversation.save(update_fields=['last_msg_at'])

    return Response({
        'request':   CustomizationRequestSerializer(req).data,
        'cart_item': CartItemSerializer(cart_item).data,
    }, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customization_request_reject(request, pk):
    """Buyer OU fournisseur refuse la demande/le devis."""
    from messaging.models import Message

    try:
        req = CustomizationRequest.objects.select_related(
            'product', 'product__supplier', 'conversation',
        ).get(id=pk)
    except CustomizationRequest.DoesNotExist:
        return Response({'error': 'Demande introuvable.'}, status=404)

    is_buyer    = req.buyer_id == request.user.id
    is_supplier = (hasattr(request.user, 'supplier_profile')
                   and req.product.supplier_id == request.user.supplier_profile.id)
    if not (is_buyer or is_supplier):
        return Response({'error': 'Non autorisé.'}, status=403)

    if req.status in ('accepted', 'rejected', 'expired'):
        return Response({'error': "Cette demande est déjà finalisée."}, status=400)

    with transaction.atomic():
        req.status = 'rejected'
        req.save(update_fields=['status'])
        if req.conversation_id:
            who = "L'acheteur" if is_buyer else "Le fournisseur"
            Message.objects.create(
                conversation          = req.conversation,
                sender                = request.user,
                content               = f"❌ {who} a refusé le devis.",
                message_type          = 'quote_rejected',
                customization_request = req,
            )
            req.conversation.last_msg_at = timezone.now()
            req.conversation.save(update_fields=['last_msg_at'])

    return Response(CustomizationRequestSerializer(req).data)