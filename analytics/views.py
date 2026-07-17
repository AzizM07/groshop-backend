# analytics/views.py — GROSHOP.tn
from datetime import timedelta

from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.response import Response

from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import PageView, Session, MonthlyTarget, OrderChannel, OrderRegion
from .serializers import (
    PageViewCreateSerializer, MonthlyTargetSerializer,
    OrderChannelSerializer, OrderRegionSerializer,
)


# ── Permission fournisseur ────────────────────────────────────────
class IsSupplier(BasePermission):
    message = "Compte fournisseur requis."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'supplier_profile')
        )


# ══════════════════════════════════════════════════════════════════
# TRACKING
# ══════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([AllowAny])
def track_pageview(request):
    """POST /api/analytics/pageview/ — fire-and-forget depuis le front."""
    ser = PageViewCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    user       = request.user if request.user.is_authenticated else None
    session_id = ser.validated_data.get('session_key')
    session    = None

    # ── Session : upsert ──
    if session_id:
        session, created = Session.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user':         user,
                'channel':      ser.validated_data.get('channel', 'unknown'),
                'device_type':  ser.validated_data.get('device_type', 'desktop'),
                'utm_source':   ser.validated_data.get('utm_source', ''),
                'utm_campaign': ser.validated_data.get('utm_campaign', ''),
            },
        )
        if not created:
            session.last_activity   = timezone.now()
            session.page_view_count += 1
            # rattache l'user si connexion en cours de session
            if user and not session.user_id:
                session.user = user
                session.save(update_fields=['last_activity', 'page_view_count', 'user'])
            else:
                session.save(update_fields=['last_activity', 'page_view_count'])

    ser.save(
        user=user,
        session=session,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
    )
    return Response({'ok': True}, status=201)


# ══════════════════════════════════════════════════════════════════
# STATS AUDIENCE / CONVERSION
# ══════════════════════════════════════════════════════════════════
class SupplierAnalyticsView(generics.GenericAPIView):
    """GET /api/analytics/supplier/stats/ — audience, canaux, conversion, séries journalières."""
    permission_classes = [IsSupplier]

    def get(self, request):
        supplier    = request.user.supplier_profile
        now         = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        views_qs = PageView.objects.filter(supplier=supplier, viewed_at__gte=month_start)

        # ⚡ 1 seule requête pour le total + les uniques (au lieu de 2)
        agg = views_qs.aggregate(
            total=Count('id'),
            uniques=Count('session_key', distinct=True),   # session_key = la chaîne, pas la FK
        )
        views_month     = agg['total'] or 0
        unique_visitors = agg['uniques'] or 0

        by_channel = list(views_qs.values('channel').annotate(count=Count('id')).order_by('-count'))
        by_device  = list(views_qs.values('device_type').annotate(count=Count('id')).order_by('-count'))
        by_page    = list(views_qs.values('page_type').annotate(count=Count('id')).order_by('-count'))

        # ── Conversion : sessions ayant vu ce fournisseur ──
        sessions_qs = Session.objects.filter(
            pageviews__supplier=supplier, started_at__gte=month_start
        ).distinct()

        # ⚡ 1 requête pour sessions + converties (au lieu de 2)
        s_agg = sessions_qs.aggregate(
            total=Count('id', distinct=True),
            conv=Count('id', distinct=True, filter=Q(converted=True)),
        )
        sessions_count  = s_agg['total'] or 0
        converted_count = s_agg['conv'] or 0
        conversion_rate = round(converted_count / sessions_count * 100, 2) if sessions_count else 0

        # ⚡ 1 requête au lieu d'une par canal (avant : boucle → N requêtes)
        conv_rows = sessions_qs.values('channel').annotate(
            total=Count('id', distinct=True),
            conv=Count('id', distinct=True, filter=Q(converted=True)),
        )
        conv_by_channel = [{
            'channel':   r['channel'],
            'sessions':  r['total'],
            'converted': r['conv'],
            'rate':      round(r['conv'] / r['total'] * 100, 2) if r['total'] else 0,
        } for r in conv_rows]

        # ── Séries journalières (14 derniers jours) — graphes hebdo du dashboard ──
        d14 = (now - timedelta(days=13)).replace(hour=0, minute=0, second=0, microsecond=0)

        daily = (PageView.objects
                 .filter(supplier=supplier, viewed_at__gte=d14)
                 .annotate(d=TruncDate('viewed_at')).values('d')
                 .annotate(
                     views=Count('id'),
                     uniques=Count('session_key', distinct=True),
                     product_views=Count('id', filter=Q(page_type='product_detail')),
                 )
                 .order_by('d'))
        rows = list(daily)   # ⚡ 1 requête pour les 2 séries (avant : 2 requêtes)

        views_by_day = [
            {'date': r['d'].isoformat(), 'views': r['views'], 'uniques': r['uniques']}
            for r in rows
        ]
        product_views_by_day = [
            {'date': r['d'].isoformat(), 'views': r['product_views']}
            for r in rows
        ]

        return Response({
            'views_month':           views_month,
            'unique_visitors':       unique_visitors,
            'sessions_count':        sessions_count,
            'converted_count':       converted_count,
            'conversion_rate':       conversion_rate,
            'by_channel':            by_channel,
            'by_device':             by_device,
            'by_page_type':          by_page,
            'conversion_by_channel': conv_by_channel,
            'views_by_day':          views_by_day,
            'product_views_by_day':  product_views_by_day,
        })


class SupplierActiveUsersView(generics.GenericAPIView):
    """GET /api/analytics/supplier/active-users/ — DAU / WAU / MAU (fenêtres glissantes)."""
    permission_classes = [IsSupplier]

    def get(self, request):
        supplier = request.user.supplier_profile
        now      = timezone.now()

        d1  = now - timedelta(days=1)
        d7  = now - timedelta(days=7)
        d30 = now - timedelta(days=30)

        # ⚡ 1 seule requête pour les 6 métriques (avant : 6 requêtes)
        a = PageView.objects.filter(supplier=supplier, viewed_at__gte=d30).aggregate(
            u_dau=Count('session_key', distinct=True, filter=Q(viewed_at__gte=d1)),
            u_wau=Count('session_key', distinct=True, filter=Q(viewed_at__gte=d7)),
            u_mau=Count('session_key', distinct=True),
            a_dau=Count('user', distinct=True, filter=Q(viewed_at__gte=d1, user__isnull=False)),
            a_wau=Count('user', distinct=True, filter=Q(viewed_at__gte=d7, user__isnull=False)),
            a_mau=Count('user', distinct=True, filter=Q(user__isnull=False)),
        )

        visitors = {'dau': a['u_dau'] or 0, 'wau': a['u_wau'] or 0, 'mau': a['u_mau'] or 0}
        auth_users = {'dau': a['a_dau'] or 0, 'wau': a['a_wau'] or 0, 'mau': a['a_mau'] or 0}

        return Response({
            'authenticated_users': auth_users,
            'unique_visitors':     visitors,
            'stickiness_ratio': round(visitors['dau'] / visitors['mau'] * 100, 2)
                                if visitors['mau'] else 0,
        })


# ══════════════════════════════════════════════════════════════════
# RÉGIONS (carte Tunisie)
# ══════════════════════════════════════════════════════════════════
class SupplierRegionStatsView(generics.GenericAPIView):
    """GET /api/analytics/supplier/regions/ — commandes & CA par gouvernorat."""
    permission_classes = [IsSupplier]

    def get(self, request):
        supplier = request.user.supplier_profile

        rows = (
            OrderRegion.objects
            .filter(order__sub_orders__supplier=supplier)
            .exclude(order__sub_orders__status='cancelled')
            .values('gouvernorat')
            .annotate(
                orders_count=Count('order', distinct=True),
                revenue=Sum('order__sub_orders__subtotal_tnd'),
            )
            .order_by('-revenue')
        )

        labels = dict(OrderRegion._meta.get_field('gouvernorat').choices)
        data = [{
            'gouvernorat':  r['gouvernorat'],
            'label':        labels.get(r['gouvernorat'], r['gouvernorat']),
            'orders_count': r['orders_count'],
            'revenue':      float(r['revenue'] or 0),
        } for r in rows]

        return Response({'by_region': data})


# ══════════════════════════════════════════════════════════════════
# OBJECTIFS MENSUELS
# ══════════════════════════════════════════════════════════════════
class MonthlyTargetListCreateView(generics.ListCreateAPIView):
    serializer_class   = MonthlyTargetSerializer
    permission_classes = [IsSupplier]

    def get_queryset(self):
        return MonthlyTarget.objects.filter(supplier=self.request.user.supplier_profile)

    def perform_create(self, serializer):
        serializer.save(
            supplier=self.request.user.supplier_profile,
            created_by=self.request.user,
        )


class MonthlyTargetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = MonthlyTargetSerializer
    permission_classes = [IsSupplier]

    def get_queryset(self):
        return MonthlyTarget.objects.filter(supplier=self.request.user.supplier_profile)


class CurrentMonthTargetView(generics.GenericAPIView):
    """GET /api/analytics/supplier/target/ — objectif du mois en cours + réalisé."""
    permission_classes = [IsSupplier]

    def get(self, request):
        from orders.models import SubOrder

        supplier = request.user.supplier_profile
        now      = timezone.now()
        start    = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        target = MonthlyTarget.objects.filter(
            supplier=supplier, year=now.year, month=now.month
        ).first()

        a = SubOrder.objects.filter(
            supplier=supplier, created_at__gte=start
        ).exclude(status='cancelled').aggregate(rev=Sum('subtotal_tnd'), n=Count('id'))

        achieved_revenue = float(a['rev'] or 0)
        achieved_orders  = a['n'] or 0

        target_revenue = float(target.revenue_target) if target else 0
        pct = round(achieved_revenue / target_revenue * 100, 1) if target_revenue else 0

        return Response({
            'has_target':       bool(target),
            'year':             now.year,
            'month':            now.month,
            'target_revenue':   target_revenue,
            'target_orders':    target.orders_target if target else 0,
            'achieved_revenue': achieved_revenue,
            'achieved_orders':  achieved_orders,
            'progress_pct':     min(pct, 100),
            'remaining':        max(target_revenue - achieved_revenue, 0),
        })