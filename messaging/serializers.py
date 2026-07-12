# messaging/serializers.py
from rest_framework import serializers
from .models import Conversation, Message


# ══════════════════════════════════════════════════════════════════
# MESSAGE
# ══════════════════════════════════════════════════════════════════
class MessageSerializer(serializers.ModelSerializer):
    sender_id   = serializers.UUIDField(source='sender.id', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)

    class Meta:
        model  = Message
        fields = ['id', 'sender_id', 'sender_name', 'sender_role',
                  'content', 'attachment_url',
                  'is_read', 'created_at']


# ══════════════════════════════════════════════════════════════════
# Helpers communs pour construire les objets buyer/supplier
# ══════════════════════════════════════════════════════════════════
def _supplier_data(s):
    logo = None
    try:
        logo = s.store.logo_url if hasattr(s, 'store') else None
    except Exception:
        logo = None
    
    # Statut online via le user du supplier
    user = getattr(s, 'user', None)
    is_online = user.is_online if user else False
    last_seen = user.last_seen.isoformat() if user and user.last_seen else None
    
    return {
        'id':              str(s.id),
        'name':            getattr(s, 'company_name', '') or '',
        'company_name':    getattr(s, 'company_name', '') or '',
        'slug':            getattr(s, 'slug', '') or '',
        'logo_url':        logo,
        'verified':        getattr(s, 'verified_status', '') == 'approved',
        'verified_status': getattr(s, 'verified_status', ''),
        'is_online':       is_online,
        'last_seen':       last_seen,
    }


def _buyer_data(b):
    return {
        'id':         str(b.id),
        'full_name':  getattr(b, 'full_name', '') or '',
        'avatar_url': getattr(b, 'avatar_url', None),
        'is_online':  b.is_online,
        'last_seen':  b.last_seen.isoformat() if b.last_seen else None,
    }


# ══════════════════════════════════════════════════════════════════
# CONVERSATION LIST
# ══════════════════════════════════════════════════════════════════
class ConversationListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_slug = serializers.CharField(source='supplier.slug', read_only=True)
    supplier_logo = serializers.CharField(source='supplier.store.logo_url', read_only=True)

    supplier = serializers.SerializerMethodField()
    buyer    = serializers.SerializerMethodField()

    buyer_name    = serializers.CharField(source='buyer.full_name', read_only=True)
    last_message  = serializers.SerializerMethodField()
    unread_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ['id', 'supplier', 'buyer',
                  'supplier_name', 'supplier_slug', 'supplier_logo',
                  'buyer_name', 'last_msg_at', 'last_message', 'unread_count']

    def get_supplier(self, obj): return _supplier_data(obj.supplier)
    def get_buyer(self, obj):    return _buyer_data(obj.buyer)

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if not msg:
            return None
        return {
            'id':         str(msg.id),
            'content':    msg.content[:200],
            'sender_id':  str(msg.sender_id),
            'created_at': msg.created_at.isoformat(),
            'is_read':    msg.is_read,
        }

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


# ══════════════════════════════════════════════════════════════════
# CONVERSATION DETAIL
# ══════════════════════════════════════════════════════════════════
class ConversationDetailSerializer(serializers.ModelSerializer):
    messages      = MessageSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_slug = serializers.CharField(source='supplier.slug', read_only=True)
    product_name  = serializers.CharField(source='product.name', read_only=True)

    supplier = serializers.SerializerMethodField()
    buyer    = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ['id', 'supplier', 'buyer',
                  'supplier_name', 'supplier_slug',
                  'product_name', 'last_msg_at', 'messages']

    def get_supplier(self, obj): return _supplier_data(obj.supplier)
    def get_buyer(self, obj):    return _buyer_data(obj.buyer)


# ══════════════════════════════════════════════════════════════════
# SEND MESSAGE
# ══════════════════════════════════════════════════════════════════
class SendMessageSerializer(serializers.Serializer):
    content        = serializers.CharField(min_length=1, max_length=2000)
    attachment_url = serializers.CharField(required=False, allow_blank=True)