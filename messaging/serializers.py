# messaging/serializers.py — GROSHOP.tn
from rest_framework import serializers
from django.utils import timezone
from .models import Conversation, Message


# ══════════════════════════════════════════════════════════════════
# MESSAGE
# ══════════════════════════════════════════════════════════════════
class MessageSerializer(serializers.ModelSerializer):
    sender_id   = serializers.UUIDField(source='sender.id', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    quote       = serializers.SerializerMethodField()  # ← AJOUT

    class Meta:
        model  = Message
        fields = ['id', 'sender_id', 'sender_name', 'sender_role',
                  'content', 'attachment_url',
                  'is_read', 'created_at',
                  'message_type', 'quote']  # ← AJOUT

    def get_quote(self, obj):
        """Bulle spéciale : renvoie les infos du devis quand le message y est lié."""
        if not obj.customization_request_id:
            return None
        # Import local pour éviter les cycles
        from orders.serializers import CustomizationRequestSerializer
        return CustomizationRequestSerializer(obj.customization_request).data

# ══════════════════════════════════════════════════════════════════
# Helpers communs pour construire les objets buyer/supplier
# ══════════════════════════════════════════════════════════════════
def _supplier_data(s):
    logo = None
    try:
        logo = s.store.logo_url if hasattr(s, 'store') else None
    except Exception:
        logo = None

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
    # Choix produit : NOM RÉEL du client (B2B). On n'expose jamais tél/email/adresse.
    city = getattr(b, 'city', None) or getattr(b, 'ville', None) or ''
    return {
        'id':         str(b.id),
        'full_name':  getattr(b, 'full_name', '') or '',
        'city':       city,
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
    product_name  = serializers.CharField(source='product.name', read_only=True)
    last_message  = serializers.SerializerMethodField()
    unread_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ['id', 'supplier', 'buyer',
                  'supplier_name', 'supplier_slug', 'supplier_logo',
                  'buyer_name', 'product_name',
                  'last_msg_at', 'last_message', 'unread_count']

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

    supplier    = serializers.SerializerMethodField()
    buyer       = serializers.SerializerMethodField()
    # curseur serveur : le front l'utilise comme point de départ du poll incrémental
    server_time = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ['id', 'supplier', 'buyer',
                  'supplier_name', 'supplier_slug',
                  'product_name', 'last_msg_at', 'messages', 'server_time']

    def get_supplier(self, obj):   return _supplier_data(obj.supplier)
    def get_buyer(self, obj):      return _buyer_data(obj.buyer)
    def get_server_time(self, obj): return timezone.now().isoformat()


# ══════════════════════════════════════════════════════════════════
# SEND MESSAGE
# ══════════════════════════════════════════════════════════════════
class SendMessageSerializer(serializers.Serializer):
    content        = serializers.CharField(min_length=1, max_length=2000)
    attachment_url = serializers.CharField(required=False, allow_blank=True)

    def validate_attachment_url(self, v):
        # Sécurité : on n'accepte qu'une URL https (ou vide). Bloque javascript:, data:, etc.
        if v and not v.startswith('https://'):
            raise serializers.ValidationError("Pièce jointe invalide (https requis).")
        return v