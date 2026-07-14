# analytics/views.py — GROSHOP.tn
from datetime import timedelta

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.response import Response

from django.db.models import Count, Sum
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
        session=session,                                   # ⚠️ FIX : lie la vraie FK
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
    )
    return Response({'ok': True}, status=201)


# ══════════════════════════════════════════════════════════════════
# STATS AUDIENCE / CONVERSION
# ══════════════════════════════════════════════════════════════════
class SupplierAnalyticsView(generics.GenericAPIView):
    """GET /api/analytics/supplier/stats/ — audience, canaux, conversion (mois en cours)."""
    permission_classes = [IsSupplier]

    def get(self, request):
        supplier    = request.user.supplier_profile
        now         = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        views_qs = PageView.objects.filter(supplier=supplier, viewed_at__gte=month_start)

        views_month     = views_qs.count()
        unique_visitors = views_qs.values('session_id').distinct().count()

        by_channel = list(views_qs.values('channel').annotate(count=Count('id')).order_by('-count'))
        by_device  = list(views_qs.values('device_type').annotate(count=Count('id')).order_by('-count'))
        by_page    = list(views_qs.values('page_type').annotate(count=Count('id')).order_by('-count'))

        # ── Conversion : sessions ayant vu ce fournisseur ──
        # ⚠️ FIX : passe par la FK 'pageviews' (avant : 'pageview__supplier' → n'existait pas)
        sessions_qs = Session.objects.filter(
            pageviews__supplier=supplier, started_at__gte=month_start
        ).distinct()

        sessions_count  = sessions_qs.count()
        converted_count = sessions_qs.filter(converted=True).count()
        conversion_rate = round(converted_count / sessions_count * 100, 2) if sessions_count else 0

        # Conversion par canal
        conv_by_channel = []
        for row in sessions_qs.values('channel').annotate(total=Count('id', distinct=True)):
            conv = sessions_qs.filter(channel=row['channel'], converted=True).count()
            conv_by_channel.append({
                'channel': row['channel'],
                'sessions': row['total'],
                'converted': conv,
                'rate': round(conv / row['total'] * 100, 2) if row['total'] else 0,
            })

        return Response({
            'views_month':      views_month,
            'unique_visitors':  unique_visitors,
            'sessions_count':   sessions_count,
            'converted_count':  converted_count,
            'conversion_rate':  conversion_rate,
            'by_channel':       by_channel,
            'by_device':        by_device,
            'by_page_type':     by_page,
            'conversion_by_channel': conv_by_channel,
        })


class SupplierActiveUsersView(generics.GenericAPIView):
    """GET /api/analytics/supplier/active-users/ — DAU / WAU / MAU (fenêtres glissantes)."""
    permission_classes = [IsSupplier]

    def get(self, request):
        supplier = request.user.supplier_profile
        now      = timezone.now()
        base     = PageView.objects.filter(supplier=supplier)

        windows = {
            'dau': now - timedelta(days=1),
            'wau': now - timedelta(days=7),
            'mau': now - timedelta(days=30),
        }

        auth_users, visitors = {}, {}
        for key, since in windows.items():
            auth_users[key] = (base.filter(viewed_at__gte=since, user__isnull=False)
                               .values('user').distinct().count())
            visitors[key]   = (base.filter(viewed_at__gte=since)
                               .values('session_id').distinct().count())

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

        # ⚠️ FIX : related_name réel = 'sub_orders' (avant : 'suborders')
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
            'gouvernorat': r['gouvernorat'],
            'label':       labels.get(r['gouvernorat'], r['gouvernorat']),
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

        achieved_qs = SubOrder.objects.filter(
            supplier=supplier, created_at__gte=start
        ).exclude(status='cancelled')

        achieved_revenue = float(achieved_qs.aggregate(s=Sum('subtotal_tnd'))['s'] or 0)
        achieved_orders  = achieved_qs.count()

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