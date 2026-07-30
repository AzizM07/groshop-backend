import os
import uuid as _uuid

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import DeviceToken, PushNotification
from .fcm import send_to_tokens


def _notif_dict(n):
    return {
        'id': str(n.id),
        'title': n.title,
        'body': n.body,
        'image_url': n.image_url,
        'link': n.link,
        'audience': n.audience,
        'target_user': str(n.target_user_id) if n.target_user_id else None,
        'sent_count': n.sent_count,
        'fail_count': n.fail_count,
        'created_at': n.created_at.isoformat(),
    }


# ── Public : enregistrer / retirer un token ───────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def register_token(request):
    token = (request.data.get('token') or '').strip()
    if not token:
        return Response({'error': 'token requis'}, status=400)
    DeviceToken.objects.update_or_create(
        token=token,
        defaults={
            'user': request.user if request.user.is_authenticated else None,
            'platform': request.data.get('platform', 'web'),
            'is_active': True,
        },
    )
    return Response({'ok': True}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def unregister_token(request):
    token = (request.data.get('token') or '').strip()
    DeviceToken.objects.filter(token=token).delete()
    return Response(status=204)


# ── Admin : stats ─────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_stats(request):
    base = DeviceToken.objects.filter(is_active=True)
    return Response({
        'total': base.count(),
        'buyers': base.filter(user__role='buyer').count(),
        'suppliers': base.filter(user__role='supplier').count(),
        'anonymous': base.filter(user__isnull=True).count(),
    })


# ── Admin : liste + envoi ─────────────────────────────────────────
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def admin_notifications(request):
    if request.method == 'GET':
        qs = PushNotification.objects.all()[:100]
        return Response([_notif_dict(n) for n in qs])

    data = request.data
    title = (data.get('title') or '').strip()
    body = (data.get('body') or '').strip()
    if not title or not body:
        return Response({'error': 'Titre et message obligatoires.'}, status=400)

    audience = data.get('audience') or 'all'

    # Image : fichier uploadé → storage, sinon URL fournie
    image_url = data.get('image_url') or ''
    f = request.FILES.get('image')
    if f is not None:
        ext = os.path.splitext(f.name)[1].lower() or '.jpg'
        key = f'notifications/{_uuid.uuid4().hex}{ext}'
        path = default_storage.save(key, ContentFile(f.read()))
        url = default_storage.url(path)
        if url.startswith('/'):
            url = request.build_absolute_uri(url)
        image_url = url

    # Cible → tokens
    tokens_qs = DeviceToken.objects.filter(is_active=True)
    target_user_id = None
    if audience == 'buyers':
        tokens_qs = tokens_qs.filter(user__role='buyer')
    elif audience == 'suppliers':
        tokens_qs = tokens_qs.filter(user__role='supplier')
    elif audience == 'user':
        target_user_id = data.get('target_user') or None
        if not target_user_id:
            return Response({'error': 'Utilisateur cible requis.'}, status=400)
        tokens_qs = tokens_qs.filter(user_id=target_user_id)

    tokens = list(tokens_qs.values_list('token', flat=True))
    link = data.get('link') or ''

    result = send_to_tokens(tokens, title, body, image=image_url or None, link=link or None)

    # Nettoie les tokens morts
    if result['invalid']:
        DeviceToken.objects.filter(token__in=result['invalid']).delete()

    notif = PushNotification.objects.create(
        title=title, body=body, image_url=image_url, link=link,
        audience=audience, target_user_id=target_user_id,
        sent_count=result['success'], fail_count=result['failure'],
    )
    return Response(_notif_dict(notif), status=201)