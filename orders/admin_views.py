# orders/admin_views.py
# Endpoints LECTURE du dashboard admin/CEO, sous /api/admin/…, protégés IsAdmin.
# NB modèle : Order n'a PAS de date de livraison (ni delivered_at ni date prévue).
#   → « en retard » est DÉRIVÉ de created_at + Product.delivery_days.
#   → « délai moyen de livraison » n'est PAS calculable ici (voir admin_stats).
#
# ⭐ CORRIGÉ : le numéro de commande affiché (`ref`) utilise désormais
# order.reference (ex: "ORD-2026-0007"), généré une seule fois par Order.save().
# Avant, plusieurs endpoints reconstruisaient un numéro différent à partir de
# l'id tronqué ("CMD-81A4FC70") → incohérent avec la page de confirmation et
# la liste des commandes acheteur, qui utilisaient déjà order.reference.

from datetime import timedelta
from store.models import SubscriptionPlan 
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator

from rest_framework.decorators import (
    api_view, permission_classes, authentication_classes,
)
from rest_framework.response import Response
from rest_framework import status as http_status

from users.authentication import CookieJWTAuthentication
from users.permissions import IsAdmin
from users.models import SupplierProfile, User, SupplierStore, BuyerProfile
from products.models import Product
from messaging.models import Conversation
from .models import Order, SubOrder


MOIS_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
           'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────
def _initials(name):
    parts = [p for p in (name or '').split() if p]
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _expected_date(sub_order):
    """Date de livraison ATTENDUE, dérivée : created_at + max(delivery_days)
    des produits de la sous-commande. Le modèle n'a pas de date prévue en base."""
    days = 0
    for item in sub_order.items.all():
        d = getattr(item.product, 'delivery_days', 0) or 0
        if d > days:
            days = d
    return sub_order.order.created_at + timedelta(days=days)


def _is_late(sub_order):
    if sub_order.status in ('delivered', 'cancelled'):
        return False
    return _expected_date(sub_order) < timezone.now()


def _due_label(sub_order):
    if sub_order.status in ('delivered', 'cancelled'):
        return None
    exp = _expected_date(sub_order)
    now = timezone.now()
    if exp < now:
        return 'En retard'
    days = (exp.date() - now.date()).days
    if days <= 0:
        return "Aujourd'hui"
    if days == 1:
        return 'Demain'
    return f'Dans {days} jours'


def _order_ref(order):
    """⭐ Numéro de commande affiché — TOUJOURS order.reference.
    Fallback sur l'id tronqué uniquement si reference est absent
    (ne devrait jamais arriver : Order.save() le génère systématiquement)."""
    return order.reference or f'CMD-{str(order.id)[:8].upper()}'


def _suborder_row(so):
    return {
        'id':            str(so.id),
        'order_id':      str(so.order_id),
        'ref':           _order_ref(so.order),
        'buyer_name':    so.order.buyer.full_name,
        'initials':      _initials(so.order.buyer.full_name),
        'supplier_name': so.supplier.company_name,
        'status':        so.status,
        'status_label':  dict(SubOrder.STATUS).get(so.status, so.status),
        'subtotal_tnd':  str(so.subtotal_tnd),
        'item_count':    so.items.count(),
        'is_late':       _is_late(so),
        'due_label':     _due_label(so),
        'created_at':    so.created_at.isoformat(),
    }


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/stats/  — KPIs plateforme
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_stats(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    ca_ce_mois = (Order.objects
                  .filter(created_at__gte=month_start)
                  .exclude(status='cancelled')
                  .aggregate(s=Sum('total_tnd'))['s'] or 0)

    ca_total = (Order.objects
                .exclude(status='cancelled')
                .aggregate(s=Sum('total_tnd'))['s'] or 0)

    months = []
    y, m = now.year, now.month
    for i in range(5, -1, -1):
        mm, yy = m - i, y
        while mm <= 0:
            mm += 12
            yy -= 1
        months.append((yy, mm))

    ca_par_mois = []
    for (yy, mm) in months:
        s = (Order.objects
             .filter(created_at__year=yy, created_at__month=mm)
             .exclude(status='cancelled')
             .aggregate(s=Sum('total_tnd'))['s'] or 0)
        ca_par_mois.append({'label': MOIS_FR[mm - 1], 'total_tnd': str(s)})

    commandes_a_traiter = SubOrder.objects.filter(status='pending').count()

    open_subs = (SubOrder.objects
                 .exclude(status__in=['delivered', 'cancelled'])
                 .select_related('order')
                 .prefetch_related('items__product'))
    commandes_en_retard = sum(1 for so in open_subs if _is_late(so))

    paiements = list(Order.objects
                     .exclude(status='cancelled')
                     .values('payment_method')
                     .annotate(n=Count('id'))
                     .order_by('-n'))

    return Response({
        'commandes_en_retard': commandes_en_retard,
        'commandes_a_traiter': commandes_a_traiter,
        'ca_ce_mois_tnd':      str(ca_ce_mois),
        'ca_total_tnd':        str(ca_total),
        'ca_par_mois':         ca_par_mois,
        'paiements':           paiements,
        'delai_moyen_jours':   None,
    })


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/orders/  — liste des sous-commandes (tous fournisseurs)
# Filtres : ?supplier= &status= &month=YYYY-MM &search= &page= &page_size=
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_orders(request):
    qs = (SubOrder.objects
          .select_related('order', 'order__buyer', 'supplier')
          .prefetch_related('items__product')
          .order_by('-created_at'))

    supplier = request.GET.get('supplier')
    if supplier:
        qs = qs.filter(supplier_id=supplier)

    st = request.GET.get('status')
    if st:
        qs = qs.filter(status=st)

    month = request.GET.get('month')
    if month:
        try:
            yy, mm = month.split('-')
            qs = qs.filter(order__created_at__year=int(yy),
                           order__created_at__month=int(mm))
        except (ValueError, TypeError):
            pass

    search = request.GET.get('search')
    if search:
        # ⭐ CORRIGÉ : recherche sur order.reference (ex: "ORD-2026-0007")
        # au lieu de order.id — c'est ce numéro qui est affiché et copié
        # partout côté client, donc c'est lui que l'admin va taper.
        s = search.strip()
        qs = qs.filter(Q(order__reference__icontains=s) |
                       Q(order__id__icontains=s) |
                       Q(id__icontains=s))

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    paginator = Paginator(qs, page_size)
    p = paginator.get_page(page)

    return Response({
        'results':   [_suborder_row(so) for so in p.object_list],
        'count':     paginator.count,
        'page':      p.number,
        'num_pages': paginator.num_pages,
    })


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/orders/<uuid>/  — détail d'une sous-commande
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_order_detail(request, sub_order_id):
    try:
        so = (SubOrder.objects
              .select_related('order', 'order__buyer', 'supplier')
              .prefetch_related('items__product')
              .get(id=sub_order_id))
    except SubOrder.DoesNotExist:
        return Response({'detail': 'Sous-commande introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    order = so.order

    items = []
    for it in so.items.all():
        img = None
        try:
            pimg = (it.product.images.filter(is_primary=True).first()
                    or it.product.images.first())
            img = pimg.url if pimg else None
        except Exception:
            img = None
        items.append({
            'product':        it.product.name,
            'quantity':       it.quantity,
            'unit_price_tnd': str(it.unit_price_tnd),
            'total_tnd':      str(it.total_tnd),
            'image':          img,
        })

    return Response({
        'id':               str(so.id),
        'order_id':         str(order.id),
        'ref':              _order_ref(order),
        'status':           so.status,
        'status_label':     dict(SubOrder.STATUS).get(so.status, so.status),
        'order_status':     order.status,
        'payment_status':   order.payment_status,
        'payment_method':   order.payment_method,
        'delivery_type':    so.delivery_type,
        'supplier': {
            'name':     so.supplier.company_name,
            'verified': getattr(so.supplier, 'verification_status', '') == 'approved',
        },
        'buyer': {
            'name':     order.buyer.full_name,
            'initials': _initials(order.buyer.full_name),
        },
        'items':            items,
        'subtotal_tnd':     str(so.subtotal_tnd),
        'total_tnd':        str(order.total_tnd),
        'discount_tnd':     str(order.discount_tnd),
        'shipping_address': order.shipping_address,
        'is_late':          _is_late(so),
        'due_label':        _due_label(so),
        'created_at':       so.created_at.isoformat(),
    })

# ──────────────────────────────────────────────────────────────────
# GET /api/admin/suppliers/  — liste des fournisseurs (SupplierProfile)
# Filtre : ?status=pending|approved|rejected
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_suppliers(request):
    qs = (SupplierProfile.objects
          .annotate(n_products=Count('products', distinct=True),
                    n_orders=Count('sub_orders', distinct=True))
          .order_by('company_name'))

    status_f = request.GET.get('status')
    if status_f:
        qs = qs.filter(verification_status=status_f)

    now_year = timezone.now().year
    results = []
    for s in qs:
        years = (now_year - s.created_at.year) if s.created_at else None
        results.append({
            'id':                  str(s.id),
            'company_name':        s.company_name,
            'verification_status': s.verification_status,
            'product_count':       s.n_products,   # relation Product.supplier (related_name='products')
            'order_count':         s.n_orders,     # relation SubOrder.supplier (related_name='sub_orders')
            'years_active':        years,          # dérivé de created_at
            'doc_logo':            s.doc_logo,     # ← NOUVEAU : avatar dans la liste
        })

    return Response({'results': results, 'count': len(results)})


# ──────────────────────────────────────────────────────────────────
# POST /api/admin/suppliers/<uuid>/verify/  — décision de vérification
# body : { "decision": "approved" | "rejected" | "pending" }
# ──────────────────────────────────────────────────────────────────
@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_verify_supplier(request, supplier_id):
    try:
        s = SupplierProfile.objects.get(id=supplier_id)
    except SupplierProfile.DoesNotExist:
        return Response({'detail': 'Fournisseur introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    decision = request.data.get('decision')
    if decision not in ('approved', 'rejected', 'pending'):
        return Response({'detail': 'Décision invalide.'},
                        status=http_status.HTTP_400_BAD_REQUEST)

    s.verification_status = decision
    s.save(update_fields=['verification_status'])
    return Response({'id': str(s.id), 'verification_status': s.verification_status})


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/payments/  — vue paiements (les commandes sous l'angle paiement)
# Filtre : ?status=unpaid|paid|refunded   (pas de modèle "facture" en base)
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_payments(request):
    qs = Order.objects.select_related('buyer').order_by('-created_at')

    status_f = request.GET.get('status')
    if status_f:
        qs = qs.filter(payment_status=status_f)

    results = [{
        'id':             str(o.id),
        'ref':            _order_ref(o),
        'buyer_name':     o.buyer.full_name,
        'total_tnd':      str(o.total_tnd),
        'payment_status': o.payment_status,
        'payment_method': o.payment_method,
        'created_at':     o.created_at.isoformat(),
    } for o in qs[:1000]]

    return Response({'results': results, 'count': len(results)})


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/products/  — modération produits
# Filtre : ?status=draft|pending_review|approved|rejected
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_products(request):
    qs = (Product.objects
          .select_related('supplier')
          .prefetch_related('images')
          .order_by('-created_at'))

    status_f = request.GET.get('status')
    if status_f:
        qs = qs.filter(status=status_f)

    results = []
    for p in qs[:1000]:
        imgs = list(p.images.all())
        primary = next((i for i in imgs if i.is_primary), None) or (imgs[0] if imgs else None)
        results.append({
            'id':             str(p.id),
            'name':           p.name,
            'status':         p.status,
            'base_price_tnd': str(p.base_price_tnd),
            'primary_image':  primary.url if primary else None,
            'supplier_name':  p.supplier.company_name if p.supplier_id else None,
            'sold_count':     p.sold_count,
            'moq':            p.moq,
            'unit':           p.unit,
        })

    return Response({'results': results, 'count': len(results)})


# ──────────────────────────────────────────────────────────────────
# POST /api/admin/products/<uuid>/review/  — valider / rejeter un produit
# body : { "decision": "approved" | "rejected" | "pending_review" | "draft" }
# ──────────────────────────────────────────────────────────────────
@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_review_product(request, product_id):
    try:
        p = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'detail': 'Produit introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    decision = request.data.get('decision')
    if decision not in ('draft', 'pending_review', 'approved', 'rejected'):
        return Response({'detail': 'Décision invalide.'},
                        status=http_status.HTTP_400_BAD_REQUEST)

    p.status = decision
    p.save(update_fields=['status'])
    return Response({'id': str(p.id), 'status': p.status})


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/users/  — comptes plateforme
# Filtre : ?role=buyer|supplier|admin
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_users(request):
    qs = User.objects.all().order_by('-created_at')

    role_f = request.GET.get('role')
    if role_f:
        qs = qs.filter(role=role_f)

    results = [{
        'id':          str(u.id),
        'full_name':   u.full_name,
        'email':       u.email,
        'role':        u.role,
        'is_active':   u.is_active,
        'created_at':  u.created_at.isoformat(),
    } for u in qs[:2000]]

    return Response({'results': results, 'count': len(results)})


# ──────────────────────────────────────────────────────────────────
# POST /api/admin/users/<uuid>/toggle-active/  — activer / désactiver
# ──────────────────────────────────────────────────────────────────
@api_view(['POST'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_toggle_user_active(request, user_id):
    try:
        u = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    if request.user.id == u.id:
        return Response({'detail': 'Vous ne pouvez pas désactiver votre propre compte.'},
                        status=http_status.HTTP_400_BAD_REQUEST)

    u.is_active = not u.is_active
    u.save(update_fields=['is_active'])
    return Response({'id': str(u.id), 'is_active': u.is_active})


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/suppliers/<uuid>/  — fiche complète d'un fournisseur
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_supplier_detail(request, supplier_id):
    try:
        s = (SupplierProfile.objects
             .select_related('user')
             .get(id=supplier_id))
    except SupplierProfile.DoesNotExist:
        return Response({'detail': 'Fournisseur introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    try:
        store = s.store
    except SupplierStore.DoesNotExist:
        store = None

    subs = s.sub_orders.all()
    ca = subs.exclude(status='cancelled').aggregate(x=Sum('subtotal_tnd'))['x'] or 0

    return Response({
        'id':                  str(s.id),
        'company_name':        s.company_name,
        'slug':                s.slug,
        'verification_status': s.verification_status,
        'verified_at':         s.verified_at.isoformat() if s.verified_at else None,
        'rc_number':           s.rc_number,
        'tax_number':          s.tax_number,
        'address':             s.address,
        'city':                s.city,
        'wilaya':              s.wilaya,
        'min_order_tnd':       str(s.min_order_tnd) if s.min_order_tnd is not None else None,
        'rating_avg':          str(s.rating_avg),
        'rating_count':        s.rating_count,
        'followers_count':     s.followers_count,
        'created_at':          s.created_at.isoformat(),
        # ── NOUVEAU : documents de vérification ──
        'doc_rne':             s.doc_rne,
        'doc_cin':             s.doc_cin,
        'doc_rib':             s.doc_rib,
        'doc_logo':            s.doc_logo,
        'user': {
            'full_name': s.user.full_name,
            'email':     s.user.email,
            'phone':     s.user.phone,
            'is_active': s.user.is_active,
        },
        'store': None if store is None else {
            'description':       store.description,
            'founded_year':      store.founded_year,
            'certifications':    store.certifications,
            'page_views':        store.page_views,
            'response_rate':     str(store.response_rate),
            'response_time_hrs': store.response_time_hrs,
            'logo_url':          store.logo_url,
            'banner_url':        store.banner_url,
        },
        'product_count': s.products.count(),
        'order_count':   subs.count(),
        'ca_tnd':        str(ca),
    })


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/products/<uuid>/  — fiche complète d'un produit
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_product_detail(request, product_id):
    try:
        p = (Product.objects
             .select_related('supplier', 'category')
             .prefetch_related('images', 'price_tiers', 'variants')
             .get(id=product_id))
    except Product.DoesNotExist:
        return Response({'detail': 'Produit introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    return Response({
        'id':                 str(p.id),
        'name':               p.name,
        'slug':               p.slug,
        'description':        p.description,
        'sku':                p.sku,
        'brand':              p.brand,
        'reference':          p.reference,
        'unit':               p.unit,
        'moq':                p.moq,
        'pack_size':          p.pack_size,
        'base_price_tnd':     str(p.base_price_tnd),
        'old_price_tnd':      str(p.old_price_tnd) if p.old_price_tnd is not None else None,
        'shipping_price_tnd': str(p.shipping_price_tnd),
        'is_free_shipping':   p.is_free_shipping,
        'delivery_days':      p.delivery_days,
        'stock_qty':          p.stock_qty,
        'sold_count':         p.sold_count,
        'view_count':         p.view_count,
        'rating_avg':         str(p.rating_avg),
        'rating_count':       p.rating_count,
        'status':             p.status,
        'specs_raw':          p.specs_raw,
        'created_at':         p.created_at.isoformat(),
        'supplier': None if not p.supplier_id else {
            'id':       str(p.supplier_id),
            'name':     p.supplier.company_name,
            'verified': p.supplier.verification_status == 'approved',
        },
        'category':    p.category.name if p.category_id else None,
        'images':      [{'url': i.url, 'is_primary': i.is_primary} for i in p.images.all()],
        'price_tiers': [{'min_qty': t.min_qty, 'max_qty': t.max_qty, 'price_tnd': str(t.price_tnd)}
                        for t in p.price_tiers.all()],
        'variants':    [{'id': str(v.id), 'name': v.name, 'image_url': v.image_url}
                        for v in p.variants.all()],
    })


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/conversations/  — liste des conversations (surveillance)
# Filtres : ?supplier=<uuid> &search=
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_conversations(request):
    qs = (Conversation.objects
          .select_related('buyer', 'supplier', 'product')
          .annotate(n_messages=Count('messages'),
                    n_unread=Count('messages', filter=Q(messages__is_read=False)))
          .order_by('-last_msg_at'))

    supplier_f = request.GET.get('supplier')
    if supplier_f:
        qs = qs.filter(supplier_id=supplier_f)

    buyer_f = request.GET.get('buyer')
    if buyer_f:
        qs = qs.filter(buyer_id=buyer_f)

    search = request.GET.get('search')
    if search:
        qs = qs.filter(Q(buyer__full_name__icontains=search) |
                       Q(supplier__company_name__icontains=search))

    results = [{
        'id':            str(c.id),
        'buyer_name':    c.buyer.full_name,
        'supplier_name': c.supplier.company_name,
        'supplier_id':   str(c.supplier_id),
        'product_name':  c.product.name if c.product_id else None,
        'last_msg_at':   c.last_msg_at.isoformat() if c.last_msg_at else None,
        'message_count': c.n_messages,
        'unread_count':  c.n_unread,
    } for c in qs[:500]]

    return Response({'results': results, 'count': len(results)})


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/conversations/<uuid>/  — lecture d'une conversation
# (surveillance / support — accès aux messages privés)
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_conversation_detail(request, conversation_id):
    try:
        c = (Conversation.objects
             .select_related('buyer', 'supplier', 'product')
             .prefetch_related('messages__sender')
             .get(id=conversation_id))
    except Conversation.DoesNotExist:
        return Response({'detail': 'Conversation introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    messages = [{
        'id':             str(m.id),
        'sender_name':    m.sender.full_name,
        'sender_role':    m.sender.role,
        'content':        m.content,
        'attachment_url': m.attachment_url or None,
        'is_read':        m.is_read,
        'created_at':     m.created_at.isoformat(),
    } for m in c.messages.all()]

    return Response({
        'id':           str(c.id),
        'buyer':        {'name': c.buyer.full_name, 'email': c.buyer.email},
        'supplier':     {'id': str(c.supplier_id), 'name': c.supplier.company_name},
        'product_name': c.product.name if c.product_id else None,
        'created_at':   c.created_at.isoformat(),
        'messages':     messages,
    })


# ──────────────────────────────────────────────────────────────────
# GET /api/admin/users/<uuid>/  — fiche complète d'un utilisateur
# ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_user_detail(request, user_id):
    try:
        u = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    data = {
        'id':          str(u.id),
        'full_name':   u.full_name,
        'email':       u.email,
        'phone':       u.phone,
        'role':        u.role,
        'is_active':   u.is_active,
        'is_verified': u.is_verified,
        'is_online':   u.is_online,
        'last_seen':   u.last_seen.isoformat() if u.last_seen else None,
        'created_at':  u.created_at.isoformat(),
        'order_count': u.orders.count(),
        'buyer_profile':    None,
        'supplier_profile': None,
    }

    try:
        bp = u.buyer_profile
        data['buyer_profile'] = {
            'company_name':    bp.company_name,
            'trade_type':      bp.trade_type,
            'city':            bp.city,
            'wilaya':          bp.wilaya,
            'total_orders':    bp.total_orders,
            'total_spent_tnd': str(bp.total_spent_tnd),
        }
    except BuyerProfile.DoesNotExist:
        pass

    try:
        sp = u.supplier_profile
        data['supplier_profile'] = {
            'id':                  str(sp.id),
            'company_name':        sp.company_name,
            'verification_status': sp.verification_status,
        }
    except SupplierProfile.DoesNotExist:
        pass

    return Response(data)
# ──────────────────────────────────────────────────────────────────
# Plans d'abonnement  (CRUD)
# GET/POST          /api/admin/plans/
# GET/PATCH/DELETE  /api/admin/plans/<uuid>/
# SubscriptionPlan est déjà importé en haut du fichier.
# ──────────────────────────────────────────────────────────────────
def _plan_dict(p):
    return {
        'id':             str(p.id),
        'name':           p.name,
        'price_tnd':      str(p.price_tnd),
        'commission_pct': str(p.commission_pct),
        'max_products':   p.max_products,        # null = illimité
        'features':       p.features or {},
        'is_active':      p.is_active,
        'created_at':     p.created_at.isoformat(),
    }


@api_view(['GET', 'POST'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_plans(request):
    if request.method == 'GET':
        qs = SubscriptionPlan.objects.all().order_by('price_tnd')
        active = request.GET.get('active')
        if active in ('true', 'false'):
            qs = qs.filter(is_active=(active == 'true'))
        results = [_plan_dict(p) for p in qs]
        return Response({'results': results, 'count': len(results)})

    # POST → création
    d = request.data
    mp = d.get('max_products')
    plan = SubscriptionPlan.objects.create(
        name           = (d.get('name') or '').strip(),
        price_tnd      = d.get('price_tnd') or 0,
        commission_pct = d.get('commission_pct') or 0,
        max_products   = mp if mp not in ('', None) else None,
        features       = d.get('features') or {},
        is_active      = d.get('is_active', True),
    )
    return Response(_plan_dict(plan), status=http_status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAdmin])
def admin_plan_detail(request, plan_id):
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response({'detail': 'Plan introuvable.'},
                        status=http_status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(_plan_dict(plan))

    if request.method == 'DELETE':
        # SupplierSubscription.plan = on_delete=PROTECT → refus propre si utilisé
        from django.db.models import ProtectedError
        try:
            plan.delete()
        except ProtectedError:
            return Response(
                {'detail': "Ce plan est utilisé par des abonnements — désactivez-le au lieu de le supprimer."},
                status=http_status.HTTP_409_CONFLICT,
            )
        return Response(status=http_status.HTTP_204_NO_CONTENT)

    # PATCH → mise à jour partielle
    d = request.data
    for f in ('name', 'price_tnd', 'commission_pct', 'is_active', 'features'):
        if f in d:
            setattr(plan, f, d[f])
    if 'max_products' in d:
        plan.max_products = d['max_products'] if d['max_products'] not in ('', None) else None
    plan.save()
    return Response(_plan_dict(plan))