from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Notification
        fields = ['id', 'type', 'title', 'body',
                  'data', 'channel', 'is_read', 'sent_at']