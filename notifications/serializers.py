from rest_framework import serializers
from .models import DeviceToken, PushNotification


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform', 'is_active', 'created_at', 'last_seen']
        read_only_fields = ['id', 'created_at', 'last_seen']


class PushNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotification
        fields = ['id', 'title', 'body', 'image_url', 'link',
                  'audience', 'target_user', 'sent_count', 'fail_count', 'created_at']
        read_only_fields = ['id', 'sent_count', 'fail_count', 'created_at']