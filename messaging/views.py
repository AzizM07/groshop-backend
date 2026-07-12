# messaging/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import re

from .models import Conversation, Message
from .serializers import (
    ConversationListSerializer, ConversationDetailSerializer,
    SendMessageSerializer, MessageSerializer,
)
from users.models import SupplierProfile


# ══════════════════════════════════════════════════════════════════
# FILTRE MESSAGES (anti-contournement plateforme)
# ══════════════════════════════════════════════════════════════════
BANNED_PATTERNS = [
    r'(\+216|00216)[\s\-\.\*\_]?\d{2}[\s\-\.\*\_]?\d{3}[\s\-\.\*\_]?\d{3}',
    r'\b[2459]\d{7}\b',
    r'[\w\.-]+@[\w\.-]+\.\w+',
    r'http[s]?://\S+|www\.\S+',
]
BANNED_WORDS = [
    'whatsapp', 'telegram', 'viber',
    'appelle-moi', 'contacte-moi',
    'paiement direct', 'mon numéro',
]

def filter_message(content):
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return None, 'Message contient des informations de contact interdites.'
    for word in BANNED_WORDS:
        if word.lower() in content.lower():
            return None, f'Message contient un mot interdit : "{word}".'
    return content, None


# ══════════════════════════════════════════════════════════════════
# CONVERSATIONS
# ══════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversations_list(request):
    user = request.user

    if user.role == 'buyer':
        conversations = Conversation.objects.filter(
            buyer=user
        ).select_related(
            'supplier', 'supplier__store', 'buyer'
        ).prefetch_related('messages').order_by('-last_msg_at')

    elif user.role == 'supplier':
        try:
            supplier = SupplierProfile.objects.get(user=user)
        except SupplierProfile.DoesNotExist:
            return Response([])
        conversations = Conversation.objects.filter(
            supplier=supplier
        ).select_related(
            'supplier', 'supplier__store', 'buyer'
        ).prefetch_related('messages').order_by('-last_msg_at')

    else:
        conversations = Conversation.objects.none()

    serializer = ConversationListSerializer(
        conversations, many=True, context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, pk):
    user = request.user

    try:
        if user.role == 'buyer':
            conv = Conversation.objects.prefetch_related('messages__sender') \
                .get(id=pk, buyer=user)
        else:
            supplier = SupplierProfile.objects.get(user=user)
            conv = Conversation.objects.prefetch_related('messages__sender') \
                .get(id=pk, supplier=supplier)
    except (Conversation.DoesNotExist, SupplierProfile.DoesNotExist):
        return Response({'error': 'Conversation non trouvée.'}, status=404)

    # Marquer les messages comme lus
    conv.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    serializer = ConversationDetailSerializer(conv)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_conversation(request, supplier_slug):
    try:
        supplier = SupplierProfile.objects.get(slug=supplier_slug)
    except SupplierProfile.DoesNotExist:
        return Response({'error': 'Fournisseur non trouvé.'}, status=404)

    if request.user.role != 'buyer':
        return Response(
            {'error': 'Seuls les acheteurs peuvent initier une conversation.'},
            status=403)

    product_id = request.data.get('product_id')

    conv, created = Conversation.objects.get_or_create(
        buyer      = request.user,
        supplier   = supplier,
        product_id = product_id or None,
    )

    serializer = ConversationDetailSerializer(conv)
    return Response(serializer.data,
                    status=201 if created else 200)


# ══════════════════════════════════════════════════════════════════
# SEND MESSAGE — renvoie maintenant le message COMPLET sérialisé
# ══════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, pk):
    user = request.user

    try:
        if user.role == 'buyer':
            conv = Conversation.objects.get(id=pk, buyer=user)
        else:
            supplier = SupplierProfile.objects.get(user=user)
            conv     = Conversation.objects.get(id=pk, supplier=supplier)
    except (Conversation.DoesNotExist, SupplierProfile.DoesNotExist):
        return Response({'error': 'Conversation non trouvée.'}, status=404)

    serializer = SendMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    content = serializer.validated_data['content']

    # Filtre anti-contournement
    filtered, error = filter_message(content)
    if error:
        return Response({'error': error}, status=400)

    message = Message.objects.create(
        conversation   = conv,
        sender         = user,
        content        = filtered,
        attachment_url = serializer.validated_data.get('attachment_url', ''),
    )

    # Met à jour last_msg_at
    conv.last_msg_at = timezone.now()
    conv.save(update_fields=['last_msg_at'])

    # ── CORRIGÉ : renvoie le message complet (avec sender_id) ──
    return Response(MessageSerializer(message).data, status=201)