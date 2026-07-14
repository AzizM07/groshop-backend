# analytics/serializers.py — GROSHOP.tn
from rest_framework import serializers
from .models import PageView, Session, MonthlyTarget, OrderChannel, OrderRegion


class PageViewCreateSerializer(serializers.ModelSerializer):
    """Écriture seule — appelé par le hook usePageTracking du front."""

    # le front envoie 'session_id' → stocké dans 'session_key'
    session_id = serializers.CharField(source='session_key', max_length=64)

    class Meta:
        model  = PageView
        fields = [
            'supplier', 'product', 'page_type',
            'session_id', 'channel', 'device_type',
            'utm_source', 'utm_medium', 'utm_campaign', 'referrer',
        ]
        extra_kwargs = {
            'supplier': {'required': False, 'allow_null': True},
            'product':  {'required': False, 'allow_null': True},
            'referrer': {'required': False, 'allow_blank': True},
        }


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Session
        fields = ['session_id', 'channel', 'device_type', 'started_at',
                  'last_activity', 'page_view_count', 'converted', 'converted_at']


class MonthlyTargetSerializer(serializers.ModelSerializer):
    period_label = serializers.ReadOnlyField()

    class Meta:
        model  = MonthlyTarget
        fields = ['id', 'year', 'month', 'period_label',
                  'revenue_target', 'orders_target',
                  'new_buyers_target', 'views_target', 'updated_at']
        # supplier & created_by sont injectés par la vue (perform_create)

    def validate_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("Le mois doit être entre 1 et 12.")
        return value


class OrderChannelSerializer(serializers.ModelSerializer):
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)

    class Meta:
        model  = OrderChannel
        fields = ['order', 'channel', 'channel_display',
                  'utm_source', 'utm_campaign', 'device_type']


class OrderRegionSerializer(serializers.ModelSerializer):
    gouvernorat_display = serializers.CharField(source='get_gouvernorat_display', read_only=True)

    class Meta:
        model  = OrderRegion
        fields = ['order', 'gouvernorat', 'gouvernorat_display', 'city', 'confidence']