# users/phone_verify.py — GROSHOP.tn
# Vérification du numéro de téléphone (+216) par code OTP.
#
# ⚠️ MODE DEV : send_otp() écrit le code dans les logs au lieu de l'envoyer.
#    Quand ton WhatsApp/SMS est prêt, remplace UNIQUEMENT le corps de send_otp().
#    Rien d'autre à toucher.

import re
import secrets
import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User, BannedPhone, PhoneOTP

logger = logging.getLogger(__name__)

OTP_TTL_MINUTES  = 10   # durée de validité du code
OTP_COOLDOWN_SEC = 60   # délai mini entre deux envois (anti-spam / anti-coût)
OTP_MAX_ATTEMPTS = 5    # essais de saisie avant blocage du code


# ── Envoi du code ──────────────────────────────────────────────────
def send_otp(phone, code):
    """
    MODE DEV : log le code (visible dans la console / les logs Render).
    ➜ Plus tard, remplace ce corps par l'appel WhatsApp Business API (ou SMS) :
        envoyer à `phone` un message contenant `code`.
    Le reste du système ne change pas.
    """
    logger.warning('[OTP] code pour %s : %s', phone, code)
    print(f'[OTP] code pour {phone} : {code}')   # visible aussi en dev local


# ── Normalisation d'un numéro tunisien → +216XXXXXXXX ──────────────
def normalize_tn_phone(raw):
    digits = re.sub(r'\D', '', raw or '')
    if digits.startswith('00216'):
        digits = digits[5:]
    elif digits.startswith('216') and len(digits) == 11:
        digits = digits[3:]
    if len(digits) != 8:
        return None
    return f'+216{digits}'


# ── 1) Demande d'un code ───────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_phone_otp(request):
    phone = normalize_tn_phone(request.data.get('phone'))
    if not phone:
        return Response({'error': 'phone_invalid'}, status=400)

    # Numéro banni → refus direct
    if BannedPhone.objects.filter(phone=phone).exists():
        return Response({'error': 'phone_banned'}, status=403)

    # Déjà vérifié par un AUTRE compte → refus (ta règle d'unicité)
    if User.objects.filter(phone=phone, phone_verified=True).exclude(id=request.user.id).exists():
        return Response({'error': 'phone_taken'}, status=409)

    # Anti-spam : un seul envoi par minute
    since = timezone.now() - timedelta(seconds=OTP_COOLDOWN_SEC)
    if PhoneOTP.objects.filter(user=request.user, created_at__gte=since).exists():
        return Response({'error': 'cooldown'}, status=429)

    code = f'{secrets.randbelow(1_000_000):06d}'
    PhoneOTP.objects.create(
        user=request.user,
        phone=phone,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )
    send_otp(phone, code)
    return Response({'ok': True})


# ── 2) Vérification du code ────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_phone_otp(request):
    phone = normalize_tn_phone(request.data.get('phone'))
    code = (request.data.get('code') or '').strip()
    if not phone or not code:
        return Response({'error': 'invalid'}, status=400)

    if BannedPhone.objects.filter(phone=phone).exists():
        return Response({'error': 'phone_banned'}, status=403)

    otp = (PhoneOTP.objects
           .filter(user=request.user, phone=phone, consumed=False)
           .order_by('-created_at')
           .first())
    if not otp:
        return Response({'error': 'no_code'}, status=400)
    if otp.expires_at < timezone.now():
        return Response({'error': 'expired'}, status=400)
    if otp.attempts >= OTP_MAX_ATTEMPTS:
        return Response({'error': 'too_many'}, status=429)
    if otp.code != code:
        otp.attempts += 1
        otp.save(update_fields=['attempts'])
        return Response({'error': 'wrong_code'}, status=400)

    # Code bon → dernière vérif d'unicité (course entre deux comptes)
    if User.objects.filter(phone=phone, phone_verified=True).exclude(id=request.user.id).exists():
        return Response({'error': 'phone_taken'}, status=409)

    otp.consumed = True
    otp.save(update_fields=['consumed'])

    u = request.user
    u.phone = phone
    u.phone_verified = True
    u.save(update_fields=['phone', 'phone_verified'])

    return Response({'ok': True, 'phone': phone})