# messaging/views.py — GROSHOP.tn
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.utils.dateparse import parse_datetime
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
# ACCÈS — un seul point de vérité : participant-only, scoping par rôle
# ══════════════════════════════════════════════════════════════════
def _get_conversation(user, pk):
    """Renvoie la conversation SI l'utilisateur en est un participant, sinon None.
    Empêche tout accès croisé (un fournisseur ne peut lire la conv d'un autre)."""
    try:
        if user.role == 'buyer':
            return Conversation.objects.get(id=pk, buyer=user)
        if user.role == 'supplier':
            supplier = SupplierProfile.objects.get(user=user)
            return Conversation.objects.get(id=pk, supplier=supplier)
    except (Conversation.DoesNotExist, SupplierProfile.DoesNotExist):
        return None
    return None


def _conversations_for(user):
    """Queryset des conversations visibles par l'utilisateur, selon son rôle."""
    if user.role == 'buyer':
        return Conversation.objects.filter(buyer=user)
    if user.role == 'supplier':
        try:
            supplier = SupplierProfile.objects.get(user=user)
        except SupplierProfile.DoesNotExist:
            return Conversation.objects.none()
        return Conversation.objects.filter(supplier=supplier)
    return Conversation.objects.none()


# ══════════════════════════════════════════════════════════════════
# CONVERSATIONS
# ══════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversations_list(request):
    conversations = (_conversations_for(request.user)
                     .select_related('supplier', 'supplier__store', 'supplier__user',
                                     'buyer', 'product')
                     .prefetch_related('messages')
                     .order_by('-last_msg_at'))
    serializer = ConversationListSerializer(
        conversations, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, pk):
    conv = _get_conversation(request.user, pk)
    if conv is None:
        return Response({'error': 'Conversation non trouvée.'}, status=404)

    # Chargement initial → on marque comme lus les messages de l'autre partie
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    conv = (Conversation.objects
            .select_related('supplier', 'supplier__user', 'buyer', 'product')
            .prefetch_related('messages__sender')
            .get(id=conv.id))
    return Response(ConversationDetailSerializer(conv).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_poll(request, pk):
    """Poll incrémental. Renvoie UNIQUEMENT :
      - messages: ceux créés après ?after=<iso>
      - read_ids: MES messages désormais lus (→ double coche bleue)
      - server_time: nouveau curseur
    ?mark_read=1 (onglet actif) marque comme lus les messages entrants."""
    user = request.user
    conv = _get_conversation(user, pk)
    if conv is None:
        return Response({'error': 'Conversation non trouvée.'}, status=404)

    after     = parse_datetime(request.query_params.get('after') or '')
    mark_read = request.query_params.get('mark_read') in ('1', 'true', 'True')

    qs = conv.messages.select_related('sender').order_by('created_at')
    new_qs = qs.filter(created_at__gt=after) if after else qs
    new_messages = list(new_qs)

    # Marque lus les messages de l'AUTRE partie, seulement si l'onglet regarde vraiment
    if mark_read:
        conv.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    # Accusés de lecture : MES messages désormais lus (limités aux 60 récents)
    read_ids = list(
        conv.messages.filter(sender=user, is_read=True)
        .order_by('-created_at').values_list('id', flat=True)[:60]
    )

    return Response({
        'messages':    MessageSerializer(new_messages, many=True).data,
        'read_ids':    [str(i) for i in read_ids],
        'server_time': timezone.now().isoformat(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """Total des messages non lus, tous fils confondus. Pour le badge de nav."""
    convs = _conversations_for(request.user)
    count = (Message.objects
             .filter(conversation__in=convs, is_read=False)
             .exclude(sender=request.user)
             .count())
    return Response({'count': count})


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

    conv = (Conversation.objects
            .select_related('supplier', 'supplier__user', 'buyer', 'product')
            .prefetch_related('messages__sender')
            .get(id=conv.id))
    return Response(ConversationDetailSerializer(conv).data,
                    status=201 if created else 200)


# ══════════════════════════════════════════════════════════════════
# SEND MESSAGE
# ══════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, pk):
    user = request.user
    conv = _get_conversation(user, pk)
    if conv is None:
        return Response({'error': 'Conversation non trouvée.'}, status=404)

    serializer = SendMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    content = serializer.validated_data['content']

    filtered, error = filter_message(content)
    if error:
        return Response({'error': error}, status=400)

    message = Message.objects.create(
        conversation   = conv,
        sender         = user,
        content        = filtered,
        attachment_url = serializer.validated_data.get('attachment_url', ''),
    )

    conv.last_msg_at = timezone.now()
    conv.save(update_fields=['last_msg_at'])

    return Response(MessageSerializer(message).data, status=201)