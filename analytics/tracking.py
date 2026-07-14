# analytics/tracking.py — GROSHOP.tn
"""
Attribution d'une commande : canal + région + session convertie.
SANS ça, les cartes Canaux / Régions / Conversion restent vides.

À appeler à la fin de orders/views.py → create_order(), dans le bloc atomic :

    from analytics.tracking import attribute_order
    attribute_order(order, request)
"""
import unicodedata

from django.utils import timezone

from .models import Session, OrderChannel, OrderRegion, GOUVERNORATS


def _norm(txt):
    """minuscule + sans accents, pour matcher 'Béja' == 'beja'."""
    txt = unicodedata.normalize('NFD', txt or '')
    txt = ''.join(c for c in txt if unicodedata.category(c) != 'Mn')
    return txt.lower()


def detect_gouvernorat(address):
    """Cherche un gouvernorat dans une adresse libre. → (code, confiance) | (None, 0)."""
    a = _norm(address)
    for code, label in GOUVERNORATS:
        if _norm(label) in a or code.replace('_', ' ') in a:
            return code, 1.0
    return None, 0.0


def attribute_order(order, request):
    """Crée OrderChannel + OrderRegion et marque la session comme convertie."""
    session_id = (
        request.data.get('session_id')
        or request.headers.get('X-Session-Id')
        or ''
    )

    session = Session.objects.filter(session_id=session_id).first() if session_id else None

    # ── 1. Canal ──
    channel     = (session.channel if session else request.data.get('channel')) or 'unknown'
    device_type = (session.device_type if session else request.data.get('device_type')) or 'desktop'

    OrderChannel.objects.update_or_create(
        order=order,
        defaults={
            'channel':      channel,
            'session':      session,
            'device_type':  device_type,
            'utm_source':   session.utm_source if session else '',
            'utm_campaign': session.utm_campaign if session else '',
        },
    )

    # ── 2. Région ──
    # Priorité au champ explicite envoyé par le checkout, sinon parsing de l'adresse.
    gouv = request.data.get('gouvernorat')
    if gouv and gouv in dict(GOUVERNORATS):
        confidence = 1.0
    else:
        gouv, confidence = detect_gouvernorat(order.shipping_address)

    if gouv:
        OrderRegion.objects.update_or_create(
            order=order,
            defaults={
                'gouvernorat': gouv,
                'city':        request.data.get('city', '')[:100],
                'confidence':  confidence,
                'parsed_from': order.shipping_address[:500],
            },
        )

    # ── 3. Session convertie ──
    if session and not session.converted:
        session.converted    = True
        session.converted_at = timezone.now()
        session.order        = order
        session.save(update_fields=['converted', 'converted_at', 'order'])